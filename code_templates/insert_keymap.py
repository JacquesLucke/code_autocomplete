import bpy
from . base import InsertTemplateBase, insert_template

class InsertKeymap(bpy.types.Operator, InsertTemplateBase):
    bl_idname = "code_autocomplete.insert_keymap"
    bl_label = "Insert Keymap"
    bl_description = ""

    def execute(self, context):
        insert_template(keymap_template)
        return {"FINISHED"}

keymap_template = '''addon_keymaps = []
def register_keymaps():
    global addon_keymaps
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name = "3D View", space_type = "VIEW_3D")

    addon_keymaps.append(km)

def unregister_keymaps():
    global addon_keymaps
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()
'''
