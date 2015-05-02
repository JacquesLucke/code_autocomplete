import bpy, re
from operator import attrgetter
from .. import expression_utils as exp
from .. text_operators import *
from .. text_editor_utils import *

def get_dynamic_snippets_operators(text_block):
    operators = []
    for snippet in snippets:
        match = text_block.search_pattern_in_current_line(snippet.expression)
        if match:
            for name in snippet.get_snippet_names(match):
                operators.append(DynamicSnippetOperator(name, insert_dynamic_snippet, (snippet, name)))
    return operators
    
def insert_dynamic_snippet(text_block, snippet_and_name):
    snippet, name = snippet_and_name
    match = text_block.search_pattern_in_current_line(snippet.expression)
    if match:
        snippet.insert_snippet(text_block, match, name)
    
def replace_match(text_block, match, text):
    text_block.select_match_in_current_line(match)
    text_block.insert(text)
    
def create_snippet_objects():
    global snippets
    snippets = [
        NewPanelSnippet(),
        NewOperatorSnippet(),
        NewClassSnippet(),
        SetupKeymapsSnippet(),
        KeymapItemSnippet() ]

class NewClassSnippet:
    expression = "=(p|o|m)\|(\w+)"
    
    def insert_snippet(self, text_block, match, name):
        replace_match(text_block, match, self.get_snippet_text(match))
    
    def get_snippet_names(self, match):
        return ["New " + self.get_type(match) + " '" + self.get_name(match) + "'"]
        
    def get_snippet_text(self, match):
        return "class " + self.get_name(match) + "(bpy.types." + self.get_type(match) + ")"
    
    def get_name(self, match):
        return match.group(2)
    def get_type(self, match):
        t = match.group(1)
        if t == "p": return "Panel"
        if t == "o": return "Operator"
        if t == "m": return "Menu"
        
        
class NewPanelSnippet:
    expression = "class (\w*)\(.*Panel\):"
    
    panel_code = '''
    bl_idname = "IDNAME"
    bl_label = "LABEL"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "category"
    
    def draw(self, context):
        layout = self.layout
        '''
    
    def insert_snippet(self, text_block, match, name):
        code = self.panel_code
        code = code.replace("IDNAME", self.get_idname(match))
        code = code.replace("LABEL", self.get_label(match))
        text_block.insert(code)
        
    def get_snippet_names(self, match):
        return ["New Panel"]
        
    def get_idname(self, match):
        name = match.group(1)
        return to_lower_case_with_underscores(name)  
        
    def get_label(self, match):
        name = match.group(1)
        return to_ui_text(name) 
        
        
class NewOperatorSnippet:
    expression = "class (\w*)\(.*Operator\):"
    
    operator_code = '''
    bl_idname = "IDNAME"
    bl_label = "LABEL"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        return {"FINISHED"}
        '''
        
    modal_operator_code = '''
    bl_idname = "IDNAME"
    bl_label = "LABEL"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
        
    def modal(self, context, event):
    
        if event.type == "LEFTMOUSE":
            return {"FINISHED"}
    
        if event.type in {"RIGHTMOUSE", "ESC"}:
            return {"CANCELLED"}
            
        return {"RUNNING_MODAL"}
    
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}
        '''
        
    modal_operator_draw_code = '''
    bl_idname = "IDNAME"
    bl_label = "LABEL"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
        
    def invoke(self, context, event):
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}
        
    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type == "LEFTMOUSE":
            self.cancel(context)
            return {"FINISHED"}
            
        if event.type in {"RIGHTMOUSE", "ESC"}:
            self.cancel(context)
            return {"CANCELLED"}
            
        return {"RUNNING_MODAL"}
        
    def cancel(self, context):
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
    
    def draw_callback_px(tmp, self, context):
        pass
    '''
    
    def insert_snippet(self, text_block, match, name):
        if name == "New Operator": code = self.operator_code
        if name == "New Modal Operator": code = self.modal_operator_code
        if name == "New Modal Operator Draw": code = self.modal_operator_draw_code
        
        code = code.replace("IDNAME", self.get_idname(match))
        code = code.replace("LABEL", self.get_label(match))
        text_block.insert(code)
        
    def get_snippet_names(self, match):
        return ["New Operator", "New Modal Operator", "New Modal Operator Draw"]
        
    def get_idname(self, match):
        name = match.group(1)
        return "my_operators." + to_lower_case_with_underscores(name)  
        
    def get_label(self, match):
        name = match.group(1)
        return to_ui_text(name) 
        

def to_lower_case_with_underscores(name):
    words = get_words_from_variable(name)
    words = [word.lower() for word in words]
    output = "_".join(words)
    return output  
    
def to_ui_text(name):
    words = get_words_from_variable(name)
    words = [word.capitalize() for word in words]
    output = " ".join(words)
    return output      
        
def get_words_from_variable(name):
    words = []
    current_word = ""
    for char in name:
        if char.islower():
            current_word += char
        if char.isupper():
            if current_word.isupper() or len(current_word) == 0:
                current_word += char
            else:
                words.append(current_word)
                current_word = char
        if char == "_":
            words.append(current_word)
            current_word = ""
            
    words.append(current_word)
    words = [word for word in words if len(word) > 0]
    return words  
    
        
class SetupKeymapsSnippet:
    expression = "=keymaps"
    
    keymap_registration_code = '''addon_keymaps = []
def register_keymaps():
    global addon_keymaps
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name = "3D View", space_type = "VIEW_3D")
    
    addon_keymaps.append(km)
    
def unregister_keymaps():
    global addon_keymaps
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()
'''
    
    def insert_snippet(self, text_block, match, name):
        text_block.select_match_in_current_line(match)
        text_block.delete_selection()
        text_block.insert(self.keymap_registration_code)
    
    def get_snippet_names(self, match):
        return ["Setup Keymap Registration"]
        
                
class KeymapItemSnippet:
    expression = "=key\|(\w+)((\|shift|\|(strg|ctrl)|\|alt)*)"
    
    # keep order
    types = ["Normal", "Menu", "Pie"]
    type_names = ["Key for Operator", "Key for Menu", "Key for Pie Menu"]
                
    def insert_snippet(self, text_block, match, name):
        item_type = self.get_type(name)
        
        text = "kmi = " + self.get_new_item_string(match, item_type)
        replace_match(text_block, match, text)
        
        if item_type == "Normal":
            text_block.select_text_in_current_line("transform.translate")
        elif item_type in ["Menu", "Pie"]:
            text_block.line_break()
            text_block.insert(self.get_property_set_string(match, item_type))
            
    def get_new_item_string(self, match, t):
        operator_name = self.get_default_operator_name(match, t)
        key = self.get_key(match)
        extra_keys = self.get_optional_key_string(match)
        return "km.keymap_items.new(\""+operator_name+"\", type = \""+key+"\", value = \"PRESS\""+extra_keys+")"
          
    def get_snippet_names(self, match):
        return self.type_names
        
    def get_key(self, match):
        return match.group(1).upper()
        
    def get_optional_key_string(self, match):
        text = ""
        if self.use_strg(match): text += ", ctrl = True"
        if self.use_shift(match): text += ", shift = True"
        if self.use_alt(match): text += ", alt = True"
        return text
        
    def get_default_operator_name(self, match, t):
        if t == "Menu": return "wm.call_menu"
        if t == "Pie": return "wm.call_menu_pie"   
        return "transform.translate"
        
    def get_property_set_string(self, match, t):
        if t in ["Menu", "Pie"]: return "kmi.properties.name = "
        return ""
        
    def get_type(self, name):
        return self.types[self.type_names.index(name)]
        
    def use_strg(self, match):
        return "|strg" in match.group(2) or "|ctrl" in match.group(2)
        
    def use_shift(self, match):
        return "|shift" in match.group(2)
        
    def use_alt(self, match):
        return "|alt" in match.group(2)
        
create_snippet_objects()  