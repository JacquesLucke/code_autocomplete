import bpy, keyword, inspect
from script_auto_complete.text_editor_utils import *
from script_auto_complete.text_operators import *
from script_auto_complete.expression_utils import *

words = []

def get_extend_word_operators():
    operators = []
    text_before = get_text_before()
    word_start = get_current_word(text_before).upper()
    for word in words:
        if word.upper().startswith(word_start):
            operators.append(ExtendWordOperator(word))
    return operators
    
builtin_functions = (
    "abs", "all", "any", "ascii", "bin", "bool", "bytearray", "bytes", "callable", "chr", "classmethod", "compile", "complex", "delattr",
    "dict", "dir", "divmod", "enumerate", "eval", "exec", "filter", "float", "format", "frozenset", "getattr", "globals", "hasattr", "hash",
    "help", "hex", "id", "input", "int", "isinstance", "issubclass", "iter", "len", "list", "locals", "map", "max", "memoryview",
    "min", "next", "object", "oct", "open", "ord", "pow", "print", "property", "range", "repr", "reversed", "round", "set",
    "setattr", "slice", "sorted", "staticmethod", "str", "sum", "super", "tuple", "type", "vars", "zip", "__import__")  
    
blender_names = ["register", "unregister", "default", "bl_info"]

def update_word_list():
    global words
    words = []
    words.extend(get_existing_words())
    words.extend(keyword.kwlist)
    words.extend(blender_names)
    words.extend(builtin_functions)
    words = list(set(words))
    words.sort(key = str.lower)
