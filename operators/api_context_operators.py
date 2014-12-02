import bpy, inspect, re
from script_auto_complete.operators.text_operators import *
from script_auto_complete.text_editor_utils import *
from script_auto_complete.documentation import get_documentation

def get_api_context_operators():
    operators = []
    last_word = get_last_word()
    word_start = get_word_start()
    
    documentation = get_documentation()
    properties = documentation.get_subproperties_of_property(last_word)
    
    secondary_operators = []
    for property in properties:
        if property.name.startswith(word_start):
            operators.append(ExtendWordOperator(property.name, additional_data = property))
        elif word_start in property.name:
            secondary_operators.append(ExtendWordOperator(property.name, additional_data = property))
    return operators + secondary_operators


    