import bpy, re
from script_auto_complete.text_operators import *
from script_auto_complete.text_editor_utils import *
from script_auto_complete.documentation import *
from operator import attrgetter

def get_suggestion_from_text_before():
    operators = []
    text_before = get_text_before()
    for key, values in suggestions.items():
        match = re.match(key, text_before)
        if match is None: continue
        word_start = text_before[match.end():].upper()
        for value in values:
            if isinstance(value, tuple):
                if value[0].upper().startswith(word_start):
                    operators.append(ExtendWordOperator(value[0], additional_data = WordDescription(value[0], value[1])))
            elif value.upper().startswith(word_start):
                operators.append(ExtendWordOperator(value))
    operators.sort(key = attrgetter("display_name"))
    return operators

    
suggestions = {}

suggestions[".*bl_space_type.*=.*(\"|\')"] = [
    "EMPTY", "VIEW_3D", "TIMELINE", "GRAPH_EDITOR", "DOPESHEET", "NLA_EDITOR", "IMAGE_EDITOR", "SEQUENCE_EDITOR", "CLIP_EDITOR",
    "TEXT_EDITOR", "NODE_EDITOR", "LOGIC_EDITOR", "PROPERTIES", "OUTLINER", "USER_PREFERENCES", "INFO", "FILE_BROWSER", "CONSOLE" ]
    
suggestions[".*bl_region_type.*=.*(\"|\')"] = ["WINDOW", "HEADER", "CHANNELS", "TEMPORARY", "UI",
    ("TOOLS", "e.g. left sidebar in 3D view"), ("TOOL_PROPS", "e.g. lower part of the left side part in 3D view"), "PREVIEW"]
    
suggestions[".*bl_category.*=.*(\"|\')"] = ["Tools", "Create", "Relations", "Animation", "Physics", "Grease Pencil"]

suggestions["class \w*\("] = ["bpy", "types", "Panel", "Menu", "Operator"]
suggestions["class \w*\(bpy\."] = ["types"]
suggestions["class \w*\(bpy\.types\."] = ["Panel", "Menu", "Operator"]
