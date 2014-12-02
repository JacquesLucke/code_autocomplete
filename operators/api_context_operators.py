import bpy, inspect, re
from script_auto_complete.operators.text_operators import *
from script_auto_complete.text_editor_utils import *
from script_auto_complete.documentation import get_documentation

def get_api_context_operators():
    operators = []
    last_word = get_last_word()
    word_start = get_word_start()
    
    documentation = get_documentation()
    attributes = documentation.get_subproperties_of_property(last_word)
    attributes += documentation.get_sub_functions_of_property(last_word)
    
    secondary_operators = []
    for attribute in attributes:
        if attribute.name.startswith(word_start):
            operators.append(ExtendWordOperator(attribute.name, additional_data = attribute))
        elif word_start in attribute.name:
            secondary_operators.append(ExtendWordOperator(attribute.name, additional_data = attribute))
    return operators + secondary_operators


    