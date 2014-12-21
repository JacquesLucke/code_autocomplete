import bpy, re
from operator import attrgetter
import script_auto_complete.expression_utils as exp
from script_auto_complete.text_operators import *
from script_auto_complete.text_editor_utils import *

def get_dynamic_snippets_operators(text_block):
    operators = []
    for snippet in snippets:
        match = text_block.search_pattern_in_current_line(snippet.expression)
        if match:
            operators.append(DynamicSnippetOperator(snippet.get_snippet_name(match), insert_dynamic_snippet, snippet))
    return operators
    
def insert_dynamic_snippet(text_block, snippet):
    match = text_block.search_pattern_in_current_line(snippet.expression)
    if match:
        snippet.insert_snippet(text_block, match)
    
def replace_match(text_block, match, text):
    text_block.select_match_in_current_line(match)
    text_block.insert(text)
    
def create_snippet_objects():
    global snippets
    snippets = [NewClassSnippet(), NewPropertySnippet(), SetupKeymapsSnippet()]

class NewClassSnippet:
    expression = "=(p|o|m)\|(\w+)"
    
    def insert_snippet(self, text_block, match):
        replace_match(text_block, match, self.get_snippet_text(match))
    
    def get_snippet_name(self, match):
        return "New " + self.get_type(match) + " '" + self.get_name(match) + "'"
        
    def get_snippet_text(self, match):
        return "class " + self.get_name(match) + "(bpy.types." + self.get_type(match) + ")"
    
    def get_name(self, match):
        return match.group(2)
    def get_type(self, match):
        t = match.group(1)
        if t == "p": return "Panel"
        if t == "o": return "Operator"
        if t == "m": return "Menu"
        
class NewPropertySnippet:
    expression = "=(\w{3,})\|(\w+)\|(.*)"
    
    def insert_snippet(self, text_block, match):
        property_type = self.get_property_type(match)
        if property_type is None: return
        property_definition = self.get_property_definition(match)
        replace_match(text_block, match, property_definition)
    
    def get_snippet_name(self, match):
        property_type = self.get_property_type(match)
        if property_type is not None:
            return "New " + property_type
        return "Property Definition ..."
        
    def get_property_definition(self, match):
        bpy_type = self.get_bpy_type(match)
        name = self.get_property_name(match)
        property_type = self.get_property_type(match)
        default = self.get_default(match)
        
        return "bpy.types." + bpy_type + "." + name + " = bpy.props." + property_type + "(name = \"" + name + "\", default = " + default + ")"
    
    def get_property_type(self, match):
        default = self.get_default(match)
        tests = [
            ("[0-9]+\.[0-9]+", "FloatProperty"),
            ("[0-9]+", "IntProperty"),
            ("(\"|\').*(\"|\')", "StringProperty") ]
            
        for exp, property_type in tests:
            if re.match(exp, default):
                return property_type
        return None
    
    def get_bpy_type(self, match):
        return match.group(1)
        
    def get_property_name(self, match):
        return match.group(2)
        
    def get_default(self, match):
        return match.group(3)
        
class SetupKeymapsSnippet:
    expression = "=keymaps"
    
    function_lines = '''
addon_keymaps = []
def register_keymaps():
    global addon_keymaps
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name = "3D View", space_type = "VIEW_3D")
    kmi = km.keymap_items.new("transform.translate", "K", "PRESS")
    
    addon_keymaps.append(km)
    
def unregister_keymaps():
    global addon_keymaps
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()
    
'''.split("\n")
    
    def insert_snippet(self, text_block, match):
        text_block.select_match_in_current_line(match)
        text_block.delete_selection()
        lines = text_block.lines
        functions_index = self.find_index(lines, "def register()")        
        lines = lines[:functions_index] + self.function_lines + lines[functions_index:]
        register_index = self.find_index(lines, "bpy.utils.register_module(__name__)") + 1
        lines.insert(register_index, "    register_keymaps()")
        unregister_index = self.find_index(lines, "bpy.utils.unregister_module(__name__)") + 1
        lines.insert(unregister_index, "    unregister_keymaps()")
        text_block.lines = lines
        text_block.set_selection(functions_index + 1, 0, functions_index + len(self.function_lines) - 3, 100)
    
    def get_snippet_name(self, match):
        return "Setup Keymap Registration"
        
    def find_index(self, lines, text):
        for i, line in enumerate(lines):
            if text in line:
                return i
                
create_snippet_objects()  