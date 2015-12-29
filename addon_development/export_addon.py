import bpy
import os
import zipfile
from bpy.props import *
from . utils import current_addon_exists, get_addon_name, get_current_addon_path

class ExportAddon(bpy.types.Operator):
    bl_idname = "code_autocomplete.export_addon"
    bl_label = "Export Addon"
    bl_description = "Save a .zip file of the addon"
    bl_options = {"REGISTER"}

    filepath = StringProperty(subtype = "FILE_PATH")

    @classmethod
    def poll(cls, context):
        return current_addon_exists()

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        subdirectory_name = get_addon_name() + os.sep
        source_path = get_current_addon_path()
        output_path = self.filepath
        if not output_path.lower().endswith(".zip"):
            output_path += ".zip"
        zip_directory(source_path, output_path, additional_path = subdirectory_name)
        return {"FINISHED"}


def zip_directory(source_path, output_path, additional_path = ""):
    try:
        parent_folder = os.path.dirname(source_path)
        content = os.walk(source_path)
        zip_file = zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED)
        for root, folders, files in content:
            for data in folders + files:
                absolute_path = os.path.join(root, data)
                relative_path = additional_path + absolute_path[len(parent_folder+os.sep):]
                zip_file.write(absolute_path, relative_path)
        zip_file.close()
    except: print("Could not zip the directory")
