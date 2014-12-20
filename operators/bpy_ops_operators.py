from script_auto_complete.text_operators import ExtendWordOperator
from script_auto_complete.documentation import get_documentation
from operator import attrgetter

def get_bpy_ops_operators(text_block):
    all_operators = []
    parents = text_block.parents_of_current_word
    if len(parents) >= 2:
        if parents[0] == "bpy" and parents[1] == "ops":
            if len(parents) == 2:
                all_operators.extend(get_container_operators())
            if len(parents) == 3:
                all_operators.extend(get_ops_operators(parents[2]))
    
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