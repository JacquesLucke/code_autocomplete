import bpy, inspect, re
from script_auto_complete.operators.text_operators import *
from script_auto_complete.text_editor_utils import *
from script_auto_complete.documentation import get_documentation

def get_api_context_operators():
    operators = []
    last_word = get_last_word()
    word_start = get_word_start()
    
    documentation = get_documentation()
    words = documentation.get_subproperty_names_of_property(last_word)
    words.sort()
    
    secondary_operators = []
    for word in words:
        if word.startswith(word_start):
            operators.append(ExtendWordOperator(word))
        elif word_start in word:
            secondary_operators.append(ExtendWordOperator(word))
    print(repr(word_start))
    return operators + secondary_operators


    