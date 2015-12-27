import bpy
from bpy.props import *
from . base import InsertClassTemplateBase, insert_template
from .. utils.variable_name_conversion import (get_valid_variable_name,
                                               get_lower_case_with_underscores,
                                               get_separated_capitalized_words)

menu_type_items = [
    ("NORMAL", "Normal", ""),
    ("PIE", "Pie", "") ]

class InsertMenu(bpy.types.Operator, InsertClassTemplateBase):
    bl_idname = "code_autocomplete.insert_menu"
    bl_label = "Insert Menu"
    bl_description = ""

    menu_type = EnumProperty(items = menu_type_items, default = "NORMAL")

    def execute(self, context):
        if self.menu_type == "NORMAL": code = menu_template
        if self.menu_type == "PIE": code = pie_menu_template
        changes = {
            "CLASS_NAME" : get_valid_variable_name(self.class_name),
            "ID_NAME" : "view3d." + get_lower_case_with_underscores(self.class_name),
            "LABEL" : get_separated_capitalized_words(self.class_name) }
        insert_template(code, changes)
        return {"FINISHED"}

menu_template = '''class CLASS_NAME(bpy.types.Menu):
    bl_idname = "ID_NAME"
    bl_label = "LABEL"

    def draw(self, context):
        layout = self.layout
        '''

pie_menu_template = '''class CLASS_NAME(bpy.types.Menu):
    bl_idname = "ID_NAME"
    bl_label = "LABEL"

    def draw(self, context):
        pie = self.layout.menu_pie()
        '''
