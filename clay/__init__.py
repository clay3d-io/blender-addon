bl_info = {
    "name": "Clay",
    "blender": (2, 80, 0),
    "category": "Import-Export",
}

import os
import tempfile

import bpy
import requests


api_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImQwNTU5YzU5MDgzZDc3YWI2NDUxOThiNTIxZmM4ZmVmZmVlZmJkNjIiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiSmFrZSBMYXphcm9mZiIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS0vQUZkWnVjcXF6T01ETVZQZHMza3FKVTNnUnVWc1ZRU1RVNEkyeWJHWXFCenQ2TG5WRnRLZm1OYWh6Q0RqeGZteS1jQXo4NWY2SXpKRWpFNkV1RE0zZWVhRVd1SVo3clJtb2VRb2QtS2NYNUo0X0ZuZU9lc1pGeXAwSzFEdHpCb0tuNkoyVVhURnlBR2xtTC1DZ0VyaHVienNCOTNSZ2c2SHgyNzFnZC1aaUdRaUdHaUVuaDZIM2tuVFJUdzRwWHVRekdXaXpFMDhFWkxoSXRxTVFqWk51WXBzMkV4T0FRRTZQSWJ5ZlBWeWNGU2hJQUlYTTVsSWJIV19MU2xtREM3RGhKd3FULTNqRFJDdzR0T20xbm51Z2xDeHIwZ3U1VXV4UVNZTEtJRzNlUGIxTU9QWXZqZmhTaUh6M1p1aTI5MWNkeGVGVEJmbjFPQVBmYWdiOGhyNUZ6c0o4Rm1HcTJ3Vmc2dDZWZTR0M2xvcFVMNG5OTEhGRzlWYVRxVmNxSktMeTNucGRER1lCQVI3Sk5XWEZYQlhqTnJ2ZnM5T1J0MURfR19pMVBjZjFQb1l2d0ZZWkVfakZ1aVI5VXJIQ3Uzc1MwMFVjOVpRM1lMZnZmV1AzOERGZUd5WTI4Q204R2JnNHVNZzBFOFpzRVVEc3pHc2J5UVZNWGxQbnFqY3dGVUJtcTlEdkVvWHdremZmRUJKVjFSUWs3WjNLcnBSdGNxUU1lRjF5MFlwSlRsT3FwNXppMFhYMnp0b1c4Ukx0YXd0RUpUUEFqWUVkQWVBU210RHVIU1VkZ3JidG5UUjBQRzV2bi1kazA1RXJ3eVBBSHZ5UXpJU2NUZmJKdXlaNGZUbDE5dUFoUFB0TlA5V1Ixc3ZubjBiRVhRVDRHMGxBNFdxdEVRTXlIQ2FiWHFqeFNNZkt3dkVySS1kNVpMZVlpdUFZQ003dDFGRzl5TmlvMXRKOUhkQjZ4MzVvVWI1SjQ0OGtZcXBqLTR2ZktlVGdJNE96a1NMa3lzTktpeHFEZkxYQUFJeFhXdEdELXZGPXM5Ni1jIiwiaXNzIjoiaHR0cHM6Ly9zZWN1cmV0b2tlbi5nb29nbGUuY29tL2NsYXkzZC02ZmVmMiIsImF1ZCI6ImNsYXkzZC02ZmVmMiIsImF1dGhfdGltZSI6MTY3Mzk5MDAxMSwidXNlcl9pZCI6InBINkpaTTlXdU9ONm1MVUl5Y2pJSlVhMXJEVTIiLCJzdWIiOiJwSDZKWk05V3VPTjZtTFVJeWNqSUpVYTFyRFUyIiwiaWF0IjoxNjc0MTYyNjMyLCJleHAiOjE2NzQxNjYyMzIsImVtYWlsIjoiamFrZUBjbGF5M2QuaW8iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6eyJnb29nbGUuY29tIjpbIjExNTMwMTk5ODMxODE1NTAwODEyMiJdLCJlbWFpbCI6WyJqYWtlQGNsYXkzZC5pbyJdfSwic2lnbl9pbl9wcm92aWRlciI6Imdvb2dsZS5jb20ifX0.LgKb9ilJaDIAIpvbQ5JK3aiHRm7rVRu3mKPupNpk77aRQb0OIsfM63jHCwS4JZdAebrz5uQj7BNRRF-GNfgmzKP-05C0vcGvIhF4jN8yjH2gTuwjRPQHmwW0567mehqmbJGf_kkI3SOx2_VPoHk1tOUs554D0UNUQECTcZ4wfJBEhXLX0aWORulsMwIOQ2RJnRl9x6bWsbR1uTbqtRIV5au1SnQtrpvBxWP7oqKfgShxUzlSa8TSnPWjqQlpazaF5d2oyNJFI4L6RztLnIjUz3e2n_lLlO4K6Q1yFnBceQrCiJXx6lED-8vTKtRn_jG0DjxzGBjrub5TGVxGV3kRlw"


class ClayExportOperator(bpy.types.Operator):
    bl_idname = "clay.export"
    bl_label = "Export to Clay"

    def execute(self, context):
        with tempfile.TemporaryDirectory() as folder:
            filename = "Untitled.glb"
            if context.blend_data.filepath:
                filename = bpy.path.ensure_ext(
                    bpy.path.display_name(context.blend_data.filepath, has_ext=True),
                    ".glb",
                )

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


def draw_item(self, context):
    layout = self.layout
    layout.operator("clay.export")


def register():
    bpy.utils.register_class(ClayExportOperator)
    bpy.types.TOPBAR_MT_file.append(draw_item)


def unregister():
    bpy.types.TOPBAR_MT_file.remove(draw_item)
    bpy.utils.unregister_class(ClayExportOperator)
