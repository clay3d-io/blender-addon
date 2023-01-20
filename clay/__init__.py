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


def api_request(method, path, api_key, files):
    url = api_host + "/v1" + path
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


class SceneProperties(bpy.types.PropertyGroup):
    file_name: bpy.props.StringProperty(
        name="File name",
        default="",
    )


class ExportOperator(bpy.types.Operator):
    bl_idname = "clay.export"
    bl_label = "Export to Clay"

    def execute(self, context):
        clay = context.scene.clay
        prefs = context.preferences.addons[__name__].preferences

        file_name = bpy.path.ensure_ext(clay.file_name or "Untitled", ".glb")

        with tempfile.TemporaryDirectory() as folder:
            filepath = os.path.join(folder, file_name)
            bpy.ops.export_scene.gltf(filepath=filepath, export_format="GLB")

            json = {}
            with open(filepath, mode="rb") as file:
                try:
                    json = api_request(
                        method="POST",
                        path="/workspaces/e816747e-81ca-4788-bf92-3b9a56215c0b/files",
                        api_key=prefs.api_key,
                        files={file_name: file},
                    )
                except Exception as e:
                    message = (
                        str(e)
                        or "Couldn't export file to Clay. Please contact support@clay3d.io."
                    )
                    self.report({"ERROR"}, message)
                    return {"CANCELLED"}

            print("UPLOADED", json)

        return {"FINISHED"}


class ClayPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_claypanel"
    bl_label = "Clay"
    bl_category = "Clay"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    file_name: bpy.props.StringProperty(name="Filename")

    def draw(self, context):
        self.layout.prop(context.scene.clay, "file_name")
        self.layout.operator(ExportOperator.bl_idname, text="Export to Clay")


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
    bpy.types.Scene.clay = bpy.props.PointerProperty(type=SceneProperties)
    bpy.app.handlers.load_post.append(initialize_file_name)
    bpy.app.handlers.save_post.append(initialize_file_name)


def unregister():
    del bpy.types.Scene.clay
    bpy.utils.unregister_class(ExportOperator)
    bpy.utils.unregister_class(ClayPanel)
    bpy.utils.unregister_class(SceneProperties)
    bpy.utils.unregister_class(Preferences)
    bpy.app.handlers.load_post.remove(initialize_file_name)
    bpy.app.handlers.save_post.remove(initialize_file_name)


if __name__ == "__main__":
    register()
