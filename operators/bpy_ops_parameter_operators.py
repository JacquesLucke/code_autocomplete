import bpy
from script_auto_complete.text_operators import ExtendWordOperator
from script_auto_complete.documentation import get_documentation, WordDescription
from operator import attrgetter

def get_bpy_ops_parameter_operators(text_block):
    operators = []
    function_path = text_block.get_current_function_path()
    if function_path is not None:
        documentation = get_documentation()
        op = documentation.get_operator_by_full_name(function_path)
        if op is not None:
            operators.extend(get_parameter_name_operators(text_block, op))
            operators.extend(get_enum_items_operators(text_block, op))
    operators.sort(key = attrgetter("display_name"))
    return operators

# bpy.ops.text.move(#type# = "NEXT_CHARACTER")
def get_parameter_name_operators(text_block, op):
    word_start = text_block.get_current_text_after_pattern("[\(\,]\s*")
    if word_start is None: return []
    operators = []
    word_start = word_start.upper()
    for input in op.inputs:
        if input.name.upper().startswith(word_start):
            operators.append(ExtendWordOperator(input.name, align = "INSET", additional_data = input))
    return operators

# bpy.ops.text.move(type = "#NEXT_CHARACTER#") 
def get_enum_items_operators(text_block, op):
    operators = []
    for input in op.inputs:
        pattern = input.name + "\s*=\s*(\"|\')"
        word_start =text_block.get_current_text_after_pattern(pattern)
        if word_start is None: continue
        word_start = word_start.upper()
        for enum_item in input.enum_items:
            if enum_item.upper().startswith(word_start):
                operators.append(ExtendWordOperator(enum_item))
    return operators
    