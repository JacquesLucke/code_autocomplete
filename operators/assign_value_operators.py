import bpy
from script_auto_complete.text_operators import ExtendWordOperator
from script_auto_complete.documentation import get_documentation, PropertyDocumentation
from operator import attrgetter

def get_assign_value_operators(text_block):
    operators = []
    
    function_path = text_block.get_current_line_assign_variable_path()
    if function_path is not None:
        documentation = get_documentation()
        attributes = documentation.get_best_matching_attributes_of_path(function_path)
        pattern = function_path + "\s*=\s*(\"|\')"
        word_start = text_block.get_current_text_after_pattern(pattern)
        if word_start is not None:
            items = set()
            for attribute in attributes:
                if isinstance(attribute, PropertyDocumentation):
                    items.update(attribute.enum_items)
                    
            word_start = word_start.upper()
            for item in items:
                if item.upper().startswith(word_start):
                    operators.append(ExtendWordOperator(item))
            
    operators.extend(get_compare_value_operators(text_block))
    operators.sort(key = attrgetter("display_name"))
    return operators
    
def get_compare_value_operators(text_block):
    operators = []
    
    function_path, reference_operator = text_block.get_current_compare_variable_path()
    if function_path is not None:
        documentation = get_documentation()
        attributes = documentation.get_best_matching_attributes_of_path(function_path)
        pattern = function_path + "\s*"+reference_operator+"\s*(\"|\')"
        word_start = text_block.get_current_text_after_pattern(pattern)
        if word_start is not None:
            items = set()
            for attribute in attributes:
                if isinstance(attribute, PropertyDocumentation):
                    items.update(attribute.enum_items)
                    
            word_start = word_start.upper()
            for item in items:
                if item.upper().startswith(word_start):
                    operators.append(ExtendWordOperator(item))
            
    operators.sort(key = attrgetter("display_name"))
    return operators