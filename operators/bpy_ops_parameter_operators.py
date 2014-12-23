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
            for input in op.inputs:
                pattern = "[\(\,]\s*"
                word_start = text_block.get_current_text_after_pattern(pattern)
                if word_start is not None:
                    if input.name.upper().startswith(word_start.upper()):
                        operators.append(ExtendWordOperator(input.name, align = "INSET", additional_data = input))
                if input.type == "Enum":
                    pattern = input.name+"\s*=\s*(\"|\')"
                    word_start = text_block.get_current_text_after_pattern(pattern)
                    if word_start is None: continue
                    word_start = word_start.upper()
                    for suggestion in input.enum_items:
                        if suggestion.upper().startswith(word_start):
                            operators.append(ExtendWordOperator(suggestion))
    operators.sort(key = attrgetter("display_name"))
    return operators
    