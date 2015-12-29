import bpy
from .. text_block import TextBlock
from . base import InsertTemplateBase
from .. graphics.utils import getDpiFactor

class InsertKeymapItem(bpy.types.Operator, InsertTemplateBase):
    bl_idname = "code_autocomplete.insert_keymap_item"
    bl_label = "Insert Keymap Item"
    bl_description = ""

    def invoke(self, context, event):
        wm = context.window_manager
        self.temp_keymap = wm.keyconfigs.addon.keymaps.new("3D View", space_type = "VIEW_3D")
        self.temp_keymap_item = self.temp_keymap.keymap_items.new(self.bl_idname, type = "P", value = "PRESS")

        dpiFactor = getDpiFactor()
        return context.window_manager.invoke_props_dialog(self, 300 * dpiFactor, 200 * dpiFactor)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self.temp_keymap_item, "type")
        col.prop(self.temp_keymap_item, "value")
        row = col.row()
        row.prop(self.temp_keymap_item, "shift")
        row.prop(self.temp_keymap_item, "ctrl")
        row.prop(self.temp_keymap_item, "alt")

    def check(self, context):
        return True

    def execute(self, context):
        kmi = self.temp_keymap_item

        line = "kmi = km.keymap_items.new(\"transform.translate\", type = \"{}\", value = \"{}\"".format(kmi.type, kmi.value)
        if kmi.shift: line += ", shift = True"
        if kmi.ctrl: line += ", ctrl = True"
        if kmi.alt: line += ", alt = True"
        line += ")"

        text_block = TextBlock.get_active()
        text_block.insert(line)
        text_block.select_text_in_current_line("transform.translate")

        wm = context.window_manager
        self.temp_keymap.keymap_items.remove(self.temp_keymap_item)
        wm.keyconfigs.addon.keymaps.remove(self.temp_keymap)
        return {"FINISHED"}
