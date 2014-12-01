import bpy, keyword, inspect
from script_auto_complete.text_editor_utils import *
from script_auto_complete.operators.text_operators import *

words = []

def get_extend_word_operators():
    operators = []
    word_start = get_word_start().upper()
    all_existing_words = words
    for word in all_existing_words:
        if word.upper().startswith(word_start):
            operators.append(ExtendWordOperator(word))
    return operators
    
    
blender_names = ["register", "unregister", "default"]

def update_word_list():
    global words
    words = []
    words.extend(get_existing_words())
    words.extend(keyword.kwlist)
    words.extend(dir(__builtins__))
    words.extend(blender_names)
    words = list(set(words))
    words.sort(key = str.lower)
