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
        for word in words:
            if word_start in word.upper():
                yield WordCompletion(word)

space_types = [
    "EMPTY", "VIEW_3D", "TIMELINE", "GRAPH_EDITOR", "DOPESHEET", "NLA_EDITOR",
    "IMAGE_EDITOR", "SEQUENCE_EDITOR", "CLIP_EDITOR", "TEXT_EDITOR", "NODE_EDITOR",
    "LOGIC_EDITOR", "PROPERTIES", "OUTLINER", "USER_PREFERENCES", "INFO", "FILE_BROWSER", "CONSOLE"]

region_types = ["WINDOW", "HEADER", "CHANNELS", "TEMPORARY", "UI", "TOOLS", "TOOL_PROPS", "PREVIEW"]

handlers = [
    "frame_change_post", "frame_change_post", "frame_change_pre",
    "game_pre", "load_post", "load_pre", "render_cancel", "render_complete",
    "render_init", "render_post", "render_pre", "render_stats", "render_write",
    "save_post", "save_pre", "scene_update_post", "scene_update_pre", "version_update"]

suggestions = {
    "bl_space_type\s*=\s*(\"|\')" : space_types,
    "bl_region_type\s*=\s*(\"|\')" : space_types,
    "bl_options\s*=.*(,|{)\s*(\"|\')" : ["REGISTER", "UNDO", "BLOCKING", "GRAB_POINTER", "PRESET", "INTERNAL"],
    "bl_category\s*=\s*(\"|\')" : ["Tools", "Create", "Relations", "Animation", "Physics", "Grease Pencil"],
    "return\s*\{\s*(\"|\')" : ["RUNNING_MODAL", "CANCELLED", "FINISHED", "PASS_THROUGH"],
    "bpy\." : ["context", "data", "ops", "types", "utils", "path", "app", "props"],
    "bpy\.app\." : ["handlers", "translations"],
    "bpy\.app\.handlers\." : handlers,
    "bpy\.props\." : [type_name for type_name in dir(bpy.props) if type_name[0] != "_"]
}
