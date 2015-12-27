import bpy
from bpy.props import *
from .. text_block import TextBlock
from .. graphics.utils import getDpiFactor
from . base import InsertTemplateBase, insert_template

class InsertKeymap(bpy.types.Operator, InsertTemplateBase):
    bl_idname = "code_autocomplete.insert_keymap"
    bl_label = "Insert Keymap"
    bl_description = ""

    insert_callers = BoolProperty(name = "Extend Register Functions", default = True,
        description = "Insert code in register and unregister functions if they exist")

    def invoke(self, context, event):
        dpiFactor = getDpiFactor()
        return context.window_manager.invoke_props_dialog(self, 200 * dpiFactor, 200 * dpiFactor)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "insert_callers")

    def execute(self, context):
        insert_template(keymap_template)
        if self.insert_callers:
            self.insert_function_calls()
        return {"FINISHED"}

    def insert_function_calls(self):
        text_block = TextBlock.get_active()

        for i, line in enumerate(text_block.lines):
            if line.startswith("def register():"):
                text_block.current_line_index = i
                text_block.move_cursor_to_line_end()
                text_block.insert("\n    register_keymaps()")

        for i, line in enumerate(text_block.lines):
            if line.startswith("def unregister():"):
                text_block.current_line_index = i
                text_block.move_cursor_to_line_end()
                text_block.insert("\n    unregister_keymaps()")


keymap_template = '''addon_keymaps = []
def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name = "3D View", space_type = "VIEW_3D")
    # insert keymap items here
    addon_keymaps.append(km)

def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()
'''
