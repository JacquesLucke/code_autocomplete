import bpy, re
from script_auto_complete.operators.code_templates import *
from script_auto_complete.operators.text_operators import *

def get_insert_template_operators():
    operators = []
    text_before = get_text_before()
    templates = get_templates()
    for name, (before, text) in templates.items():
        if re.match(before, text_before) is not None:
            operators.append(InsertTextOperator(name, text))
    return operators
    
def get_text_before():
    text_block = bpy.context.space_data.text
    text_line = text_block.current_line
    character_index = text_block.current_character
    return text_line.body[:character_index]
