bl_info = {
    "name": "Clay",
    "blender": (2, 80, 0),
    "category": "Import-Export",
}

import os
import tempfile

import bpy
import requests


api_host = "https://api.localhost.clay3d.io"
web_host = "https://localhost.clay3d.io"


def api_request(method, path, api_key, files=None):
    url = f"{api_host}/v1{path}"
    headers = {"authorization": "Bearer " + api_key}
    r = requests.request(
        method=method,
        url=url,
        verify=False,
        headers=headers,
        files=files,
    )

    json = r.json()
    if 200 <= r.status_code <= 299:
        return json
    else:
        raise Exception(json.get("message", ""))


class Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    api_key: bpy.props.StringProperty(
        name="API Key",
        default="",
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "api_key")


def workspace_items(self, context):
    prefs = bpy.context.preferences.addons[__name__].preferences
    workspaces = api_request(method="GET", path="/workspaces", api_key=prefs.api_key)
    return [(workspace["id"], workspace["name"], "") for workspace in workspaces]


class SceneProperties(bpy.types.PropertyGroup):
    file_name: bpy.props.StringProperty(
        name="File name",
        default="",
    )

    workspace: bpy.props.EnumProperty(
        name="Workspace",
        items=workspace_items,
    )


class ClayPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_claypanel"
    bl_label = "Clay"
    bl_category = "Clay"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    file_name: bpy.props.StringProperty(name="Filename")

    def draw(self, context):
        self.layout.prop(context.scene.clay, "workspace")
        self.layout.prop(context.scene.clay, "file_name")
        self.layout.operator(ExportOperator.bl_idname, text="Export to Clay")


class ExportOperator(bpy.types.Operator):
    bl_idname = "clay.export"
    bl_label = "Export to Clay"

    def execute(self, context):
        clay = context.scene.clay
        prefs = context.preferences.addons[__name__].preferences

        file_name = bpy.path.ensure_ext(clay.file_name or "Untitled", ".glb")

        with tempfile.TemporaryDirectory() as folder:
            filepath = os.path.join(folder, file_name)
            bpy.ops.export_scene.gltf(
                filepath=filepath,
                export_format="GLB",
                export_draco_mesh_compression_enable=True,
                export_draco_mesh_compression_level=6,
            )

            with open(filepath, mode="rb") as file:
                try:
                    json = api_request(
                        method="POST",
                        path=f"/workspaces/{clay.workspace}/files",
                        api_key=prefs.api_key,
                        files={file_name: file},
                    )

                    bpy.ops.clay.success("INVOKE_DEFAULT", file_id=json["id"])
                except Exception as e:
                    message = (
                        str(e)
                        or "Couldn't export file to Clay. Please contact support@clay3d.io."
                    )
                    self.report({"ERROR"}, message)
                    return {"CANCELLED"}

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
        op.url = f"{web_host}/file/{self.file_id}"


@bpy.app.handlers.persistent
def initialize_file_name(scene):
    if bpy.context.scene.clay.file_name != "":
        return

    basename = bpy.path.basename(bpy.context.blend_data.filepath)
    bpy.context.scene.clay.file_name = os.path.splitext(basename)[0]


def register():
    bpy.utils.register_class(Preferences)
    bpy.utils.register_class(SceneProperties)
    bpy.utils.register_class(ClayPanel)
    bpy.utils.register_class(ExportOperator)
    bpy.utils.register_class(SuccessDialogOperator)
    bpy.types.Scene.clay = bpy.props.PointerProperty(type=SceneProperties)
    bpy.app.handlers.load_post.append(initialize_file_name)
    bpy.app.handlers.save_post.append(initialize_file_name)


def unregister():
    del bpy.types.Scene.clay
    bpy.utils.unregister_class(ExportOperator)
    bpy.utils.unregister_class(ClayPanel)
    bpy.utils.unregister_class(SceneProperties)
    bpy.utils.unregister_class(Preferences)
    bpy.utils.unregister_class(SuccessDialogOperator)
    bpy.app.handlers.load_post.remove(initialize_file_name)
    bpy.app.handlers.save_post.remove(initialize_file_name)


if __name__ == "__main__":
    register()
