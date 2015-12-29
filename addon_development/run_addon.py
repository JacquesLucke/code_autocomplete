import bpy
import addon_utils
import importlib
import sys
from . utils import current_addon_exists, get_addon_name

class RunAddon(bpy.types.Operator):
    bl_idname = "code_autocomplete.run_addon"
    bl_label = "Run Addon"
    bl_description = "Unregister, reload and register it again."
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return current_addon_exists()

    def execute(self, context):
        bpy.ops.code_autocomplete.save_files()

        addon_name = get_addon_name()
        module = sys.modules.get(addon_name)
        if module:
            addon_utils.disable(addon_name)
            importlib.reload(module)
        addon_utils.enable(addon_name)
        return {"FINISHED"}
