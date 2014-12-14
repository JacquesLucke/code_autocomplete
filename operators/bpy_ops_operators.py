import bpy, re
from script_auto_complete.text_operators import *
from script_auto_complete.text_editor_utils import *
from script_auto_complete.documentation import get_documentation
from operator import attrgetter
import script_auto_complete.expression_utils as exp

def get_bpy_ops_operators():
    operators = []
    text_before = get_text_before()
    parents = exp.get_parent_words(text_before)
    if len(parents) >= 2:
        if parents[0] == "bpy" and parents[1] == "ops":
            if len(parents) == 2:
                operators.extend(get_container_operators(text_before))
            if len(parents) == 3:
                operators.extend(get_ops_operators(text_before, parents[2]))
    return operators
    
def get_container_operators(text_before):
    operators = []
    documentation = get_documentation()
    container_names = documentation.get_operator_container_names()
    word_start = exp.get_current_word(text_before)
    for name in container_names:
        if name.startswith(word_start):
            operators.append(ExtendWordOperator(name))
    return operators
    
def get_ops_operators(text_before, container_name):
    operators = []
    documentation = get_documentation()
    word_start = exp.get_current_word(text_before)
    ops = documentation.get_operators_in_container(container_name)
    for op in ops:
        if op.name.startswith(word_start):
            operators.append(ExtendWordOperator(op.name))
    return operators