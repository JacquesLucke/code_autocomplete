import bpy
import os
from bpy.props import *
from . utils import current_addon_exists, get_current_addon_path

class ConvertAddonIndentation(bpy.types.Operator):
    bl_idname = "code_autocomplete.convert_addon_indentation"
    bl_label = "Convert Addon Indentation"
    bl_description = ""
    bl_options = {"REGISTER"}

    old_indentation = StringProperty(default = "\t")
    new_indentation = StringProperty(default = "    ")

    @classmethod
    def poll(cls, context):
        return current_addon_exists()

    def execute(self, context):
        paths = self.get_addon_files()
        for path in paths:
            bpy.ops.code_autocomplete.convert_file_indentation(
                path = path,
                old_indentation = self.old_indentation,
                new_indentation = self.new_indentation)
        return {"FINISHED"}

    def get_addon_files(self):
        paths = []
        for root, dirs, files in os.walk(get_current_addon_path()):
            for file in files:
                if file.endswith(".py"):
                    paths.append(os.path.join(root, file))
        return paths
