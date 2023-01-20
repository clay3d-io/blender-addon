bl_info = {
    "name": "Clay",
    "blender": (2, 80, 0),
    "category": "Import-Export",
}

import os
import tempfile

import bpy
import requests


api_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImQwNTU5YzU5MDgzZDc3YWI2NDUxOThiNTIxZmM4ZmVmZmVlZmJkNjIiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiSmFrZSBMYXphcm9mZiIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS0vQUZkWnVjcXF6T01ETVZQZHMza3FKVTNnUnVWc1ZRU1RVNEkyeWJHWXFCenQ2TG5WRnRLZm1OYWh6Q0RqeGZteS1jQXo4NWY2SXpKRWpFNkV1RE0zZWVhRVd1SVo3clJtb2VRb2QtS2NYNUo0X0ZuZU9lc1pGeXAwSzFEdHpCb0tuNkoyVVhURnlBR2xtTC1DZ0VyaHVienNCOTNSZ2c2SHgyNzFnZC1aaUdRaUdHaUVuaDZIM2tuVFJUdzRwWHVRekdXaXpFMDhFWkxoSXRxTVFqWk51WXBzMkV4T0FRRTZQSWJ5ZlBWeWNGU2hJQUlYTTVsSWJIV19MU2xtREM3RGhKd3FULTNqRFJDdzR0T20xbm51Z2xDeHIwZ3U1VXV4UVNZTEtJRzNlUGIxTU9QWXZqZmhTaUh6M1p1aTI5MWNkeGVGVEJmbjFPQVBmYWdiOGhyNUZ6c0o4Rm1HcTJ3Vmc2dDZWZTR0M2xvcFVMNG5OTEhGRzlWYVRxVmNxSktMeTNucGRER1lCQVI3Sk5XWEZYQlhqTnJ2ZnM5T1J0MURfR19pMVBjZjFQb1l2d0ZZWkVfakZ1aVI5VXJIQ3Uzc1MwMFVjOVpRM1lMZnZmV1AzOERGZUd5WTI4Q204R2JnNHVNZzBFOFpzRVVEc3pHc2J5UVZNWGxQbnFqY3dGVUJtcTlEdkVvWHdremZmRUJKVjFSUWs3WjNLcnBSdGNxUU1lRjF5MFlwSlRsT3FwNXppMFhYMnp0b1c4Ukx0YXd0RUpUUEFqWUVkQWVBU210RHVIU1VkZ3JidG5UUjBQRzV2bi1kazA1RXJ3eVBBSHZ5UXpJU2NUZmJKdXlaNGZUbDE5dUFoUFB0TlA5V1Ixc3ZubjBiRVhRVDRHMGxBNFdxdEVRTXlIQ2FiWHFqeFNNZkt3dkVySS1kNVpMZVlpdUFZQ003dDFGRzl5TmlvMXRKOUhkQjZ4MzVvVWI1SjQ0OGtZcXBqLTR2ZktlVGdJNE96a1NMa3lzTktpeHFEZkxYQUFJeFhXdEdELXZGPXM5Ni1jIiwiaXNzIjoiaHR0cHM6Ly9zZWN1cmV0b2tlbi5nb29nbGUuY29tL2NsYXkzZC02ZmVmMiIsImF1ZCI6ImNsYXkzZC02ZmVmMiIsImF1dGhfdGltZSI6MTY3Mzk5MDAxMSwidXNlcl9pZCI6InBINkpaTTlXdU9ONm1MVUl5Y2pJSlVhMXJEVTIiLCJzdWIiOiJwSDZKWk05V3VPTjZtTFVJeWNqSUpVYTFyRFUyIiwiaWF0IjoxNjc0MTY3Mjk3LCJleHAiOjE2NzQxNzA4OTcsImVtYWlsIjoiamFrZUBjbGF5M2QuaW8iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6eyJnb29nbGUuY29tIjpbIjExNTMwMTk5ODMxODE1NTAwODEyMiJdLCJlbWFpbCI6WyJqYWtlQGNsYXkzZC5pbyJdfSwic2lnbl9pbl9wcm92aWRlciI6Imdvb2dsZS5jb20ifX0.AX6A19x323d-Rl5U3RSc8eOzesGLKsh9kJM7SCsN-2rfQhc6UtOUu0-seXzrSdWg_R3S2zjjb4uxRtxDr0q82hh4zhvDv8NrMV_UBPl0ohkquovQbV0R0f2_6DwsBt8zy3rxiyp1H22Fsv2a6S7WL1Yx3TTt-L7bTCQcJRPgOazDruXXAOsbebk_pfILHelYlD3ahMLY96K2gjstD3mKMllmtfXc2KlGmiIMd9J4ju42GI8_XvixFweiWteppQztgb8RUqDUi9oMXdV-RP1JtPUPWnBLzvYCAYa0hvYQvr_G0j5fDP0DMgIwRBZ80CcRa2donNcr-hDXwFXRTNIgLw"


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


class ClayExportModalOperator(bpy.types.Operator):
    bl_idname = "clay.export_modal"
    bl_label = "Export to Clay"

    filename: bpy.props.StringProperty(name="Filename")

    def execute(self, context):
        filename = bpy.path.ensure_ext(self.filename or "Untitled", ".glb")

        with tempfile.TemporaryDirectory() as folder:
            filepath = os.path.join(folder, filename)
            bpy.ops.export_scene.gltf(filepath=filepath, export_format="GLB")

            with open(filepath, mode="rb") as file:
                url = "https://api.localhost.clay3d.io/v1/workspaces/e816747e-81ca-4788-bf92-3b9a56215c0b/files"
                r = requests.post(
                    url,
                    verify=False,
                    headers={"authorization": "Bearer " + api_token},
                    files={filename: file},
                )
                print(r.text)
        return {"FINISHED"}

    def invoke(self, context, event):
        self.filename = bpy.path.display_name(context.blend_data.filepath, has_ext=True)
        return context.window_manager.invoke_props_dialog(self)


class ClayPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_claypanel"
    bl_label = "Clay"
    bl_category = "Clay"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    file_name: bpy.props.StringProperty(name="Filename")

    def draw(self, context):
        # prefs = context.preferences.addons[__name__].preferences
        print(context.scene)
        self.layout.label(text="Hello,")
        self.layout.prop(prefs, "api_key")
        self.layout.label(text="world!")


def open_export_modal(self, context):
    self.layout.operator(ClayExportModalOperator.bl_idname, text="Export to Clay")


def register():
    bpy.utils.register_class(Preferences)
    bpy.utils.register_class(ClayPanel)
    bpy.utils.register_class(ClayExportModalOperator)
    bpy.types.TOPBAR_MT_file.append(open_export_modal)


def unregister():
    del bpy.types.Scene.clay
    bpy.types.TOPBAR_MT_file.remove(open_export_modal)
    bpy.utils.unregister_class(ClayExportModalOperator)
    bpy.utils.unregister_class(ClayPanel)
    bpy.utils.unregister_class(Preferences)


if __name__ == "__main__":
    register()
