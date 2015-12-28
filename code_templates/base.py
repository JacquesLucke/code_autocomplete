import bpy
from bpy.props import *
from .. text_block import TextBlock
from .. graphics.utils import getDpiFactor

class InsertTemplateMenu(bpy.types.Menu):
    bl_idname = "code_autocomplete_insert_template_menu"
    bl_label = "Insert Template"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("code_autocomplete.insert_panel", text = "Panel")
        layout.operator_menu_enum("code_autocomplete.insert_menu", "menu_type", text = "Menu")
        layout.operator_menu_enum("code_autocomplete.insert_operator", "operator_type", text = "Operator")
        layout.separator()
        layout.operator("code_autocomplete.insert_addon_info", "Addon Info")
        layout.operator("code_autocomplete.insert_register", "Register")
        layout.operator("code_autocomplete.insert_license", "License")
        layout.menu("code_autocomplete_insert_keymap_menu", "Keymap")

def draw_template_menu(self, context):
    self.layout.menu("code_autocomplete_insert_template_menu", text = "Code Autocomplete")

class InsertKeymapMenu(bpy.types.Menu):
    bl_idname = "code_autocomplete_insert_keymap_menu"
    bl_label = "Insert Template"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("code_autocomplete.insert_keymap", text = "Keymap")
        layout.operator("code_autocomplete.insert_keymap_item", text = "Keymap Item")

class InsertTemplateBase:
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return TextBlock.get_active()

class InsertClassTemplateBase(InsertTemplateBase):
    class_name = StringProperty(name = "Class Name", default = "")

    def invoke(self, context, event):
        dpiFactor = getDpiFactor()
        return context.window_manager.invoke_props_dialog(self, 300 * dpiFactor, 200 * dpiFactor)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "class_name", text = "Name")


def insert_template(code, changes = {}):
    text_block = TextBlock.get_active()

    if text_block.current_line.strip() != "":
        text_block.insert("\n")
    text_block.current_character_index = 0

    for old, new in changes.items():
        code = code.replace(old, new)
    if text_block:
        text_block.insert(code)
