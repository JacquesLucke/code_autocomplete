import bpy
from script_auto_complete.text_operators import *
from script_auto_complete.text_editor_utils import *
from operator import attrgetter
import script_auto_complete.expression_utils as exp

def get_suggestion_from_text_before():
    operators = []
    text_before = get_text_before()
    for pattern, values in suggestions.items():
        word_start = exp.get_text_after_match(pattern, text_before)
        if word_start is None: continue
        word_start = word_start.upper()
        for value in values:
            create_operator_from_value(operators, word_start, value)
    operators.sort(key = attrgetter("display_name"))
    return operators
    
def create_operator_from_value(operators, word_start, value):
    if isinstance(value, tuple):
        if value[0].upper().startswith(word_start):
            operators.append(ExtendWordOperator(value[0], additional_data = WordDescription(value[0], value[1])))
    elif value.upper().startswith(word_start):
        operators.append(ExtendWordOperator(value))
   
    
suggestions = {}

suggestions[".*bl_space_type.*=.*(\"|\')"] = [
    "EMPTY", "VIEW_3D", "TIMELINE", "GRAPH_EDITOR", "DOPESHEET", "NLA_EDITOR", "IMAGE_EDITOR", "SEQUENCE_EDITOR", "CLIP_EDITOR",
    "TEXT_EDITOR", "NODE_EDITOR", "LOGIC_EDITOR", "PROPERTIES", "OUTLINER", "USER_PREFERENCES", "INFO", "FILE_BROWSER", "CONSOLE" ]
    
suggestions[".*bl_region_type.*=.*(\"|\')"] = ["WINDOW", "HEADER", "CHANNELS", "TEMPORARY", "UI",
    ("TOOLS", "e.g. left sidebar in 3D view"), ("TOOL_PROPS", "e.g. lower part of the left side part in 3D view"), "PREVIEW"]
    
suggestions[".*bl_category.*=.*(\"|\')"] = ["Tools", "Create", "Relations", "Animation", "Physics", "Grease Pencil"]

suggestions["class \w*\("] = ["bpy", "Panel", "Menu", "Operator"]
suggestions["class \w*\(bpy\."] = ["types"]
suggestions["class \w*\(bpy\.types\."] = ["Panel", "Menu", "Operator"]

suggestions[".*bpy\."] = ["context", "data", "ops", "types", "utils", "path", "app", "props"]

suggestions[".*bpy\.props\."] = [type_name for type_name in dir(bpy.props) if type_name[0] != "_"]
