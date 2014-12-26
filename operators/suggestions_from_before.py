import bpy
from script_auto_complete.text_operators import ExtendWordOperator
from script_auto_complete.documentation import WordDescription, get_documentation
from operator import attrgetter

def get_suggestion_from_text_before(text_block):
    operators = []
    text_before = text_block.text_before_cursor
    for pattern, suggested_words in suggestions.items():
        word_start = text_block.get_current_text_after_pattern(pattern)
        if word_start is None: continue
        word_start = word_start.upper()
        for suggestion in suggested_words:
            create_operator_from_suggestion(operators, word_start, suggestion)
    operators.sort(key = attrgetter("display_name"))
    return operators
    
def create_operator_from_suggestion(operators, word_start, suggestion):
    if isinstance(suggestion, tuple):
        if suggestion[0].upper().startswith(word_start):
            operators.append(ExtendWordOperator(suggestion[0], additional_data = WordDescription(suggestion[0], suggestion[1])))
    elif suggestion.upper().startswith(word_start):
        operators.append(ExtendWordOperator(suggestion))
   
    
suggestions = {}

space_types = [
    "EMPTY", "VIEW_3D", "TIMELINE", "GRAPH_EDITOR", "DOPESHEET", "NLA_EDITOR", "IMAGE_EDITOR", "SEQUENCE_EDITOR", "CLIP_EDITOR",
    "TEXT_EDITOR", "NODE_EDITOR", "LOGIC_EDITOR", "PROPERTIES", "OUTLINER", "USER_PREFERENCES", "INFO", "FILE_BROWSER", "CONSOLE" ]
suggestions["\sbl_space_type *= *(\"|\')"] = space_types
 
region_types = ["WINDOW", "HEADER", "CHANNELS", "TEMPORARY", "UI",
    ("TOOLS", "e.g. left sidebar in 3D view"), ("TOOL_PROPS", "e.g. lower part of the left side part in 3D view"), "PREVIEW"]
suggestions["\s*bl_region_type *= *(\"|\')"] = region_types
    
suggestions["\s*bl_category *= *(\"|\')"] = ["Tools", "Create", "Relations", "Animation", "Physics", "Grease Pencil"]

suggestions[r"\s*bl_options *=.*\W(\"|\')"] = ["REGISTER", "UNDO", "BLOCKING", "GRAB_POINTER", "PRESET", "INTERNAL"]

suggestions["\s*return *\{ *(\"|\')"] = ["RUNNING_MODAL", "CANCELLED", "FINISHED", "PASS_THROUGH"]

suggestions["class \w*\("] = ["bpy", "Panel", "Menu", "Operator"]
suggestions["class \w*\(bpy\."] = ["types"]
suggestions["class \w*\(bpy\.types\."] = ["Panel", "Menu", "Operator"]

suggestions[".*bpy\."] = ["context", "data", "ops", "types", "utils", "path", "app", "props"]

suggestions[".*bpy\.props\."] = [type_name for type_name in dir(bpy.props) if type_name[0] != "_"]

suggestions["kmi\.properties\.name\s*=\s*(\"|\')"] = get_documentation().get_menu_names()