import bpy, keyword
from script_auto_complete.operators.text_operators import *

def get_insert_template_operators():
    operators = []
    text_before = get_text_before()
    if text_before.endswith("Panel):"):
        operators.append(InsertTextOperator("New Panel", insert_panel_text))
    if text_before.endswith("register():"):
        operators.append(InsertTextOperator("Register Code", register_text))
    return operators
    
def get_text_before():
    text_block = bpy.context.space_data.text
    text_line = text_block.current_line
    character_index = text_block.current_character
    return text_line.body[:character_index]

    
insert_panel_text = '''    bl_idname = "name"
    bl_label = "label"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "category"
    
    def draw(self, context):
        layout = self.layout'''
        
register_text = '''    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()'''