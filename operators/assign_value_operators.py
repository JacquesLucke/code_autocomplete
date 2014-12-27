import bpy
from script_auto_complete.text_operators import ExtendWordOperator
from script_auto_complete.documentation import get_documentation, PropertyDocumentation
from operator import attrgetter

def get_assign_value_operators(text_block):
    operators = []
    
    function_path = text_block.get_current_assign_variable_path()
    if function_path is not None:
        documentation = get_documentation()
        attributes = documentation.get_best_matching_attributes_of_path(function_path)
        pattern = function_path + "\s*=\s*(\"|\')"
        word_start = text_block.get_current_text_after_pattern(pattern)
        if word_start is not None:
            word_start = word_start.upper()
            for attribute in attributes:
                if isinstance(attribute, PropertyDocumentation):
                    for suggestion in attribute.enum_items:
                        if suggestion.upper().startswith(word_start):
                            operators.append(ExtendWordOperator(suggestion))
            
    operators.sort(key = attrgetter("display_name"))
    return operators
    