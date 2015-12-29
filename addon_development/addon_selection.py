import os
import bpy
from bpy.props import *
from datetime import datetime
from . utils import (get_directory_names,
                     current_addon_exists,
                     is_addon_name_valid,
                     get_current_addon_path,
                     get_addon_name,
                     correct_file_name,
                     get_settings,
                     addons_path,
                     new_addon_file)

class FindExistingAddon(bpy.types.Operator):
    bl_idname = "code_autocomplete.find_existing_addon"
    bl_label = "Find Existing Addon"
    bl_description = "Pick an existing addon"
    bl_options = {"REGISTER"}
    bl_property = "item"

    def get_items(self, context):
        items = []
        directories = get_directory_names(addons_path)
        for addon in directories:
            items.append((addon, addon, ""))
        return items

    item = bpy.props.EnumProperty(items = get_items)

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"CANCELLED"}

    def execute(self, context):
        get_settings().addon_name = self.item
        path = get_current_addon_path()
        bpy.ops.code_autocomplete.set_directory_visibility(directory = path, visibility = True)
        context.area.tag_redraw()
        return {"FINISHED"}


class MakeAddonNameValid(bpy.types.Operator):
    bl_idname = "code_autocomplete.make_addon_name_valid"
    bl_label = "Make Name Valid"
    bl_description = "Make the addon name a valid module name"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return not current_addon_exists() and not is_addon_name_valid()

    def execute(self, context):
        name = get_addon_name()
        get_settings().addon_name = correct_file_name(name, is_directory = True)
        return {"FINISHED"}


new_addon_type_items = [
    ("BASIC", "Basic", ""),
    ("MULTIFILE", "Multi-File (recommended)", "") ]

class CreateNewAddon(bpy.types.Operator):
    bl_idname = "code_autocomplete.new_addon"
    bl_label = "New Addon"
    bl_description = "Create a folder in the addon directory and setup a basic code base"
    bl_options = {"REGISTER"}

    new_addon_type = EnumProperty(default = "BASIC", items = new_addon_type_items)

    @classmethod
    def poll(cls, context):
        return not current_addon_exists() and is_addon_name_valid()

    def execute(self, context):
        self.create_addon_directory()
        self.generate_from_template()
        addon_path = get_current_addon_path()
        bpy.ops.code_autocomplete.open_file(path = addon_path + "__init__.py")
        bpy.ops.code_autocomplete.set_directory_visibility(directory = addon_path, visibility = True)
        context.area.tag_redraw()
        return {"FINISHED"}

    def create_addon_directory(self):
        os.makedirs(get_current_addon_path())

    def generate_from_template(self):
        t = self.new_addon_type
        if t == "BASIC":
            code = self.read_template_file("basic.txt")
            code = code.replace("BLENDER_VERSION", str(bpy.app.version))
            new_addon_file("__init__.py", code)

        if t == "MULTIFILE":
            code = self.read_template_file("multifile.txt")
            code = code.replace("CURRENT_YEAR", str(datetime.now().year))
            code = code.replace("BLENDER_VERSION", str(bpy.app.version))
            new_addon_file("__init__.py", code)

            code = self.read_template_file("developer_utils.txt")
            new_addon_file("developer_utils.py", code)

    def read_template_file(self, path):
        path = os.path.join(os.path.dirname(__file__), "addon_templates", path)
        file = open(path)
        text = file.read()
        file.close()
        return text
