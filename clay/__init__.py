bl_info = {
    "name": "Clay",
    "blender": (2, 80, 0),
    "category": "Import-Export",
}

import os
import tempfile

import bpy
import requests


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

            with open(filepath, mode="rb") as file:
                url = "https://api.localhost.clay3d.io/v1/workspaces/e816747e-81ca-4788-bf92-3b9a56215c0b/files"
                r = requests.post(
                    url,
                    verify=False,
                    headers={"authorization": "Bearer " + prefs.api_key},
                    files={file_name: file},
                )

                if r.status_code != 200:
                    try:
                        json = r.json()
                        self.report({"ERROR"}, json["message"])
                    except Exception as e:
                        self.report({"DEBUG"}, str(e))
                        message = "Couldn't export file to Clay. Please contact support@clay3d.io."
                        self.report({"ERROR"}, message)
                    return {"CANCELLED"}
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
