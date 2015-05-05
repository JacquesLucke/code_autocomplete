import bpy, re
from operator import attrgetter
from .. text_operators import ExtendWordOperator
from .. documentation import get_documentation, PropertyDocumentation

# scene.sync_mode = "#AUDIO_SYNC#"
def get_assign_or_compare_operators(text_block):
    operators = []
    
    assign_in_line_path = text_block.get_current_line_assign_variable_path()
    compare_path = text_block.get_current_compare_variable_path()
    
    doc = get_documentation()
    
    if assign_in_line_path is not None:
        attributes = doc.get_best_matching_attributes_of_path(assign_in_line_path)
        enum_items = get_enum_items_from_attributes(attributes)
        pattern = assign_in_line_path + "\s*=\s*(\"|\')"
        word_start = text_block.get_current_text_after_pattern(pattern)
        operators = get_operators_from_enum_items(enum_items, word_start)
    elif compare_path is not None:
        attributes = doc.get_best_matching_attributes_of_path(compare_path)
        enum_items = get_enum_items_from_attributes(attributes)
        pattern = compare_path + "\s*(==|<|>|!=|(not )?in \[)\s*(\"|\')"
        word_start = text_block.get_current_text_after_pattern(pattern)
        operators = get_operators_from_enum_items(enum_items, word_start)
  
    return operators
    
def get_enum_items_from_attributes(attributes):
    items = set()
    for attribute in attributes:
        items.update(getattr(attribute, "enum_items", []))
    return items
    
def get_operators_from_enum_items(enum_items, word_start):
    if word_start is None: return []
    if "]" not in word_start:
        split = re.split(",\s*(\"|\')", word_start)[::2]
        word_start = split[-1]
    
    word_start = word_start.upper()
    operators = []
    secondary_operators = []
    for item in enum_items:
        item = item.upper()
        if item.startswith(word_start):
            operators.append(ExtendWordOperator(item))
        elif word_start in item:
            secondary_operators.append(ExtendWordOperator(item))
    operators.sort(key = attrgetter("display_name"))
    secondary_operators.sort(key = attrgetter("display_name"))
    return operators + secondary_operators