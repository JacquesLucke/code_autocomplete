import bpy
from . base import InsertTemplateBase, insert_template

class InsertRegister(bpy.types.Operator, InsertTemplateBase):
    bl_idname = "code_autocomplete.insert_register"
    bl_label = "Insert Keymap"
    bl_description = ""

    def execute(self, context):
        insert_template(register_template)
        return {"FINISHED"}

register_template = '''def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
'''
