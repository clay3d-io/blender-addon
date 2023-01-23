bl_info = {
    "name": "Clay",
    "blender": (2, 80, 0),
    "category": "Import-Export",
}

import json
import os
import tempfile

import bpy

from .api import request, graphql


WEB_HOST = "https://localhost.clay3d.io"

WORKSPACES_CACHE = "workspace_items"


class Cache:
    FILE = os.path.join(
        bpy.utils.user_resource("SCRIPTS", path="clay", create=True),
        ".cache",
    )

    def read():
        if not os.path.exists(Cache.FILE):
            return {}

        with open(Cache.FILE, "rb") as f:
            data = f.read().decode("utf-8")
            return json.loads(data)

    def get(key):
        data = Cache.read()
        if key in data:
            return data[key]

    def set(key, value):
        data = Cache.read()
        data[key] = value
        with open(Cache.FILE, "wb+") as file:
            file.write(json.dumps(data).encode("utf-8"))

    def delete(key):
        data = Cache.read()
        if key in data:
            del data[key]

        with open(Cache.FILE, "wb+") as f:
            f.write(json.dumps(data).encode("utf-8"))


def update_api_key(self, value):
    Cache.delete(WORKSPACES_CACHE)
    pass


class Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    api_key: bpy.props.StringProperty(name="API Key", update=update_api_key)

    def draw(self, context):
        self.layout.label(
            text="""To generate an API key, go to your Clay account settings and click "API Key" on the left."""
        )
        self.layout.prop(self, "api_key")


def fetch_workspaces(self, context):
    items = Cache.get(WORKSPACES_CACHE)
    if items:
        return [tuple(item) for item in items]

    prefs = bpy.context.preferences.addons[__name__].preferences
    response = graphql(
        api_key=prefs.api_key,
        query="""\
        query GetWorkspaces {
            me {
                workspaces {
                    id
                    name
                }
            }
        }
        """,
    )

    items = [
        (workspace["id"], workspace["name"], "")
        for workspace in response["data"]["me"]["workspaces"]
    ]
    Cache.set(WORKSPACES_CACHE, items)

    return items


class SceneProperties(bpy.types.PropertyGroup):
    file_name: bpy.props.StringProperty(name="File name")
    workspace: bpy.props.EnumProperty(name="Workspace", items=fetch_workspaces)


class ClayPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_claypanel"
    bl_label = "Clay"
    bl_category = "Clay"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    file_name: bpy.props.StringProperty(name="Filename")

    def draw(self, context):
        if not context.preferences.addons[__name__].preferences.api_key:
            text = "Enter your API key in the Clay addon preferences"
            self.layout.label(text=text, icon="ERROR")
            self.layout.operator(
                OpenPreferencesOperator.bl_idname,
                text="Open preferences",
            )
            return

        self.layout.prop(context.scene.clay, "workspace")
        self.layout.prop(context.scene.clay, "file_name")
        self.layout.operator(
            ExportOperator.bl_idname,
            text="Export to Clay",
            icon="EXPORT",
        )


class OpenPreferencesOperator(bpy.types.Operator):
    bl_idname = "clay.open_preferences"
    bl_label = "Open Clay preferences"

    def execute(self, context):
        bpy.ops.screen.userpref_show()
        bpy.context.preferences.active_section = "ADDONS"
        bpy.data.window_managers["WinMan"].addon_search = "Clay"
        return {"FINISHED"}


class ExportOperator(bpy.types.Operator):
    bl_idname = "clay.export"
    bl_label = "Export to Clay"
    bl_description = "Export the scene to Clay"

    def execute(self, context):
        clay = context.scene.clay
        prefs = context.preferences.addons[__name__].preferences

        file_name = bpy.path.ensure_ext(clay.file_name or "Untitled", ".glb")

        with tempfile.TemporaryDirectory() as folder:
            file_path = os.path.join(folder, file_name)
            bpy.ops.export_scene.gltf(
                filepath=file_path,
                export_format="GLB",
                # export_draco_mesh_compression_enable=True,
                # export_draco_mesh_compression_level=6,
            )

            file_id = ""
            with open(file_path, mode="rb") as file:
                try:
                    json = request(
                        api_key=prefs.api_key,
                        method="POST",
                        path=f"/v1/workspaces/{clay.workspace}/files",
                        files={file_name: file},
                    )

                    file_id = json["id"]
                    bpy.ops.clay.success("INVOKE_DEFAULT", file_id=file_id)
                except Exception as e:
                    message = (
                        str(e)
                        or "Couldn't export file to Clay. Please contact support@clay3d.io."
                    )
                    self.report({"ERROR"}, message)
                    return {"CANCELLED"}

            render_path = os.path.join(folder, "render.png")
            context.scene.render.filepath = render_path
            context.scene.render.image_settings.file_format = "PNG"
            context.scene.render.resolution_x = 1200
            context.scene.render.resolution_y = 627
            bpy.ops.render.render(
                write_still=True,
                use_viewport=context.scene.camera is None,
            )

            image_id = ""
            with open(render_path, mode="rb") as render:
                try:
                    json = request(
                        api_key=prefs.api_key,
                        method="POST",
                        path="/v1/images/upload",
                        files={"render.png": render},
                    )

                    image_id = json["id"]
                except Exception as e:
                    self.report({"WARNING"}, message)

            try:
                graphql(
                    api_key=prefs.api_key,
                    query="""\
                    mutation UpdateFile($input: UpdateFileInput!) {
                        fileUpdate(input: $input) {
                            id
                        }
                    }
                    """,
                    variables={"input": {"id": file_id, "thumbnailId": image_id}},
                )
            except Exception as e:
                print(e)

        return {"FINISHED"}


class SuccessDialogOperator(bpy.types.Operator):
    bl_idname = "clay.success"
    bl_label = "Export successful!"

    file_id: bpy.props.StringProperty()

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        op = self.layout.operator("wm.url_open", text="Open in Clay", icon="URL")
        op.url = f"{WEB_HOST}/file/{self.file_id}"


@bpy.app.handlers.persistent
def initialize_file_name(scene):
    if bpy.context.scene.clay.file_name != "":
        return

    basename = bpy.path.basename(bpy.context.blend_data.filepath)
    bpy.context.scene.clay.file_name = os.path.splitext(basename)[0]


def file_menu_item(self, context):
    self.layout.operator("clay.export", text="Clay")


classes = (
    Preferences,
    SceneProperties,
    ClayPanel,
    ExportOperator,
    SuccessDialogOperator,
    OpenPreferencesOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.clay = bpy.props.PointerProperty(type=SceneProperties)

    if initialize_file_name not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(initialize_file_name)

    if initialize_file_name not in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.append(initialize_file_name)

    bpy.types.TOPBAR_MT_file_export.append(file_menu_item)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.clay

    if initialize_file_name in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(initialize_file_name)
    if initialize_file_name in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.remove(initialize_file_name)

    bpy.types.TOPBAR_MT_file_export.remove(file_menu_item)
