import bpy, keyword
from .. text_operators import ExtendWordOperator

def get_extend_word_operators(text_block):
    operators = []
    secondary_operators = []
    current_word = text_block.current_word.upper()
    for word in words:
        if word.upper().startswith(current_word):
            operators.append(ExtendWordOperator(word))
        elif current_word in word.upper():
            secondary_operators.append(ExtendWordOperator(word))
    return operators + secondary_operators
    
builtin_functions = (
    "abs", "all", "any", "ascii", "bin", "bool", "bytearray", "bytes", "callable", "chr", "classmethod", "compile", "complex", "delattr",
    "dict", "dir", "divmod", "enumerate", "eval", "exec", "filter", "float", "format", "frozenset", "getattr", "globals", "hasattr", "hash",
    "help", "hex", "id", "input", "int", "isinstance", "issubclass", "iter", "len", "list", "locals", "map", "max", "memoryview",
    "min", "next", "object", "oct", "open", "ord", "pow", "print", "property", "range", "repr", "reversed", "round", "set",
    "setattr", "slice", "sorted", "staticmethod", "str", "sum", "super", "tuple", "type", "vars", "zip", "__import__")  
    
blender_names = ["register", "unregister", "default", "bl_info", "keymap"]

words = []
def update_word_list(text_block):
    global words
    words = []
    words.extend(text_block.get_existing_words())
    words.extend(keyword.kwlist)
    words.extend(blender_names)
    words.extend(builtin_functions)
    words = list(set(words))
    words.sort(key = str.lower)
