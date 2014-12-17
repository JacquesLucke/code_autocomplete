import bpy, re
from operator import attrgetter
import script_auto_complete.expression_utils as exp
from script_auto_complete.text_operators import *
from script_auto_complete.text_editor_utils import *

def get_dynamic_snippets_operators():
    operators = []
    text_block = bpy.context.space_data.text
    current_line = text_block.current_line.body
    character_index = text_block.current_character
    for name, (expression, function) in snippets.items():
        match = re.search(expression, current_line)
        if match:
            if match.start() <= character_index <= match.end():
                operators.append(DynamicSnippetOperator(name, function)) 
    return operators

new_class_expression = "(Panel|Operator|Menu)\|(\w+)" 
def new_class_definition(text_block):
    current_line = text_block.current_line.body
    match = re.search(new_class_expression, current_line)
    if match:
        text = "class " + match.group(2) + "(bpy.types." + match.group(1).capitalize() + ")"
        replace_match(match, text)
        

snippets = {}

snippets["New Class"] = (new_class_expression, new_class_definition)   
    
    
def replace_match(match, text):
    set_selection_in_line(match.start(), match.end())
    bpy.ops.text.insert(text = text)