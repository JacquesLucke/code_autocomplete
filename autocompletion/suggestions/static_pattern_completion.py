import re
import bpy
from . interface import Provider, Completion


class WordCompletion(Completion):
    def __init__(self, word):
        self.name = word

    def insert(self, text_block):
        text_block.replace_current_word(self.name)

class StaticPatternProvider(Provider):
    def complete(self, text_block):
        return list(iter_static_completions(text_block))

def iter_static_completions(text_block):
    for pattern, words in suggestions.items():
        word_start = text_block.get_current_text_after_pattern(pattern)
        if word_start is None: continue
        word_start = word_start.upper()

        secondaryCompletions = []
        for word in words:
            if word.upper().startswith(word_start):
                yield WordCompletion(word)
            elif word_start in word.upper():
                secondaryCompletions.append(WordCompletion(word))
        yield from secondaryCompletions

space_properties = bpy.types.Space.bl_rna.properties
space_types = sorted([item.identifier for item in space_properties["type"].enum_items])

region_types = ["WINDOW", "HEADER", "CHANNELS", "TEMPORARY", "UI", "TOOLS", "TOOL_PROPS", "PREVIEW"]

handlers = [name for name in dir(bpy.app.handlers) if not name.startswith("_")]

event_properties = bpy.types.Event.bl_rna.properties
event_types = sorted([item.identifier for item in event_properties["type"].enum_items])
event_values = sorted([item.identifier for item in event_properties["value"].enum_items])

suggestions = {
    "bl_space_type\s*=\s*(\"|\')" : space_types,
    "bl_region_type\s*=\s*(\"|\')" : region_types,
    "bl_options\s*=.*(,|{)\s*(\"|\')" : ["REGISTER", "UNDO", "BLOCKING", "GRAB_POINTER", "PRESET", "INTERNAL", "DEFAULT_CLOSED", "HIDE_HEADER"],
    "bl_category\s*=\s*(\"|\')" : ["Tools", "Create", "Relations", "Animation", "Physics", "Grease Pencil"],
    "return\s*\{\s*(\"|\')" : ["RUNNING_MODAL", "CANCELLED", "FINISHED", "PASS_THROUGH"],
    "bpy\." : ["context", "data", "ops", "types", "utils", "path", "app", "props"],
    "bpy\.app\." : ["handlers", "translations"],
    "bpy\.app\.handlers\." : handlers,
    "bpy\.props\." : [type_name for type_name in dir(bpy.props) if type_name[0] != "_"],
    "keymap_items\.new\(.*, type = (\"|\')" : event_types,
    "keymap_items\.new\(.*, value = (\"|\')" : event_values
}
