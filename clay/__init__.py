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
        maxlen=1024,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "api_key")


class SceneProperties(bpy.types.PropertyGroup):
    file_name: bpy.props.StringProperty(
        name="File name",
        default="",
        maxlen=1024,
    )


class ExportOperator(bpy.types.Operator):
    bl_idname = "clay.export"
    bl_label = "Export to Clay"

    def execute(self, context):
        clay = context.scene.clay

        file_name = bpy.path.ensure_ext(clay.file_name or "Untitled", ".glb")
        print(file_name)

        # with tempfile.TemporaryDirectory() as folder:
        #     filepath = os.path.join(folder, filename)
        #     bpy.ops.export_scene.gltf(filepath=filepath, export_format="GLB")

        #     with open(filepath, mode="rb") as file:
        #         url = "https://api.localhost.clay3d.io/v1/workspaces/e816747e-81ca-4788-bf92-3b9a56215c0b/files"
        #         r = requests.post(
        #             url,
        #             verify=False,
        #             headers={"authorization": "Bearer " + api_token},
        #             files={filename: file},
        #         )
        #         print(r.text)
        return {"FINISHED"}

    # def invoke(self, context, event):
    #     self.filename = bpy.path.display_name(context.blend_data.filepath, has_ext=True)
    #     return context.window_manager.invoke_props_dialog(self)


class ClayPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_claypanel"
    bl_label = "Clay"
    bl_category = "Clay"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    file_name: bpy.props.StringProperty(name="Filename")

    def draw(self, context):
        # prefs = context.preferences.addons[__name__].preferences
        # self.layout.label(text="Export")
        self.layout.prop(context.scene.clay, "file_name")
        self.layout.operator(ExportOperator.bl_idname, text="Export to Clay")


# def open_export_modal(self, context):
#     self.layout.operator(ClayExportModalOperator.bl_idname, text="Export to Clay")


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
    # bpy.types.TOPBAR_MT_file.append(open_export_modal)
    bpy.types.Scene.clay = bpy.props.PointerProperty(type=SceneProperties)
    bpy.app.handlers.load_post.append(initialize_file_name)
    bpy.app.handlers.save_post.append(initialize_file_name)


def unregister():
    del bpy.types.Scene.clay
    # bpy.types.TOPBAR_MT_file.remove(open_export_modal)
    bpy.utils.unregister_class(ExportOperator)
    bpy.utils.unregister_class(ClayPanel)
    bpy.utils.unregister_class(SceneProperties)
    bpy.utils.unregister_class(Preferences)
    bpy.app.handlers.load_post.remove(initialize_file_name)
    bpy.app.handlers.save_post.remove(initialize_file_name)


if __name__ == "__main__":
    register()
