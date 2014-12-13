import bpy, inspect, re
from script_auto_complete.text_operators import *
from script_auto_complete.text_editor_utils import *
from script_auto_complete.documentation import get_documentation
from operator import attrgetter

def get_api_context_operators():
    operators = []
    last_word = get_last_word()
    word_start = get_word_start().lower()
    
    documentation = get_documentation()
    attributes = documentation.get_possible_subproperties_of_property(last_word)
    attributes += documentation.get_possible_subfunctions_of_property(last_word)
    
    secondary_operators = []
    for attribute in attributes:
        attribute_name = attribute.name.lower()
        if attribute_name.startswith(word_start):
            operators.append(ExtendWordOperator(attribute.name, additional_data = attribute))
        elif word_start in attribute_name:
            secondary_operators.append(ExtendWordOperator(attribute.name, additional_data = attribute))
            
    operators.extend(secondary_operators)
    operators.sort(key = attrgetter("display_name"))
    return operators


    