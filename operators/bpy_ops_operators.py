import re
from operator import attrgetter
from .. text_operators import ExtendWordOperator
from .. documentation import get_documentation

# bpy.ops.#text#.#move#
def get_bpy_ops_operators(text_block):
    all_operators = []
    all_operators.extend(get_operators_with_call_trigger(text_block))
    all_operators.extend(get_operators_with_ui_trigger(text_block))
    
    operators = []
    secondary_operators = []
    current_word = text_block.current_word
    for operator in all_operators:
        if operator.target_word.startswith(current_word):
            operators.append(operator)
        elif current_word in operator.target_word:
            secondary_operators.append(operator)
                
    operators.sort(key = attrgetter("display_name"))
    secondary_operators.sort(key = attrgetter("display_name"))
    return operators + secondary_operators
    
def get_operators_with_call_trigger(text_block):
    operators = []
    parents = text_block.parents_of_current_word
    if len(parents) >= 2:
        if parents[0] == "bpy" and parents[1] == "ops":
            if len(parents) == 2:
                operators.extend(get_container_operators())
            if len(parents) == 3:
                operators.extend(get_ops_operators(parents[2]))
    return operators
                
def get_operators_with_ui_trigger(text_block):
    operators = []
    possible_patterns = ("\.operator\((\"|\')", "\.keymap_items\.new\((\"|\')")
    for pattern in possible_patterns:
        text = text_block.get_current_text_after_pattern(pattern)
        if text is not None:
            if not re.fullmatch("[\w\.]*", text): continue
            if "." in text:
                operators.extend(get_ops_operators(text.split(".")[0]))
            else:
                operators.extend(get_container_operators())     
            break
    return operators
    
def get_container_operators():
    operators = []
    documentation = get_documentation()
    container_names = documentation.get_operator_container_names()
    for name in container_names:
        operators.append(ExtendWordOperator(name))
    return operators
    
def get_ops_operators(container_name):
    operators = []
    documentation = get_documentation()
    ops = documentation.get_operators_in_container(container_name)
    for op in ops:
        operators.append(ExtendWordOperator(op.name, additional_data = op))
    return operators