import bpy, re
from script_auto_complete.text_operators import *
from script_auto_complete.text_editor_utils import *
from script_auto_complete.documentation import get_documentation
from operator import attrgetter

def get_bpy_ops_operators():
    operators = []
    text_before = get_text_before()
    match = re.match(".*bpy\.ops\.", text_before)
    if match is None: return []
    word_start = text_before[match.end():]
    docs = get_documentation()
    container_names = docs.get_operator_container_names()
    for container_name in container_names:
        if container_name.startswith(word_start):
            operators.append(ExtendWordOperator(container_name))
    split = word_start.split(".")
    if len(split) > 1:
        container_name = split[0]
        word_start = split[1]
        ops_names = docs.get_operator_names_in_container(container_name)
        for ops_name in ops_names:
            if ops_name.startswith(word_start):
                operators.append(ExtendWordOperator(ops_name))
    return operators