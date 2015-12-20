import re
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
        for word in words:
            if word_start in word:
                    yield WordCompletion(word)

space_types = [
    "EMPTY", "VIEW_3D", "TIMELINE", "GRAPH_EDITOR", "DOPESHEET", "NLA_EDITOR",
    "IMAGE_EDITOR", "SEQUENCE_EDITOR", "CLIP_EDITOR", "TEXT_EDITOR", "NODE_EDITOR",
    "LOGIC_EDITOR", "PROPERTIES", "OUTLINER", "USER_PREFERENCES", "INFO", "FILE_BROWSER", "CONSOLE"]

region_types = ["WINDOW", "HEADER", "CHANNELS", "TEMPORARY", "UI", "TOOLS", "TOOL_PROPS", "PREVIEW"]

suggestions = {
    "bl_space_type\s*=\s*(\"|\')" : space_types,
    "bl_region_type\s*=\s*(\"|\')" : space_types,
    "bl_options\s*=.*(,|{)\s*(\"|\')" : ["REGISTER", "UNDO", "BLOCKING", "GRAB_POINTER", "PRESET", "INTERNAL"],
    "bl_category\s*=\s*(\"|\')" : ["Tools", "Create", "Relations", "Animation", "Physics", "Grease Pencil"],
    "return\s*\{\s*(\"|\')" : ["RUNNING_MODAL", "CANCELLED", "FINISHED", "PASS_THROUGH"]
}
