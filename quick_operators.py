import bpy
from . text_block import TextBlock

class SolveWhitespaceInconsistency(bpy.types.Operator):
    bl_idname = "script_auto_complete.correct_whitespaces"
    bl_label = "Correct Whitespaces"
    bl_description = "Convert whitespaces to spaces or tabs"
    
    def execute(self, context):
        if context.edit_text.use_tabs_as_spaces:
            bpy.ops.text.convert_whitespace(type = "SPACES")
        else:
            bpy.ops.text.convert_whitespace(type = "TABS")
        return { "FINISHED" } 

class SelectWholeString(bpy.types.Operator):
    bl_idname = "script_auto_complete.select_whole_string"
    bl_label = "Select Whole String"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        text = getattr(context.space_data, "text", None)
        if not text: return {"CANCELLED"}
    
        text_block = TextBlock(text)
        
        line_text = text_block.current_line
        character_index = text_block.current_character_index
        
        string_letter = text_block.get_string_definition_type(line_text, character_index)
        if string_letter is None: return {"CANCELLED"}
        start, end = text_block.get_range_surrounded_by_letter(line_text, string_letter, character_index)
        if start != end:
            text_block.set_selection_in_line(start, end)
            
        return {"FINISHED"}
        
class SwitchLines(bpy.types.Operator):
    bl_idname = "script_auto_complete.switch_lines"
    bl_label = "Switch Lines"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        text = getattr(context.space_data, "text", None)
        if not text: return {"CANCELLED"}
    
        text_block = TextBlock(text)
        
        line_index = text_block.current_line_index
        if line_index < 1: return {"CANCELLED"}
        line_text = text_block.lines[line_index]
        line_text_before = text_block.lines[line_index - 1]
        
        text_block.set_line_text(line_index, line_text_before)
        text_block.set_line_text(line_index - 1, line_text)
        
        return {"FINISHED"}
               
               
def right_click_menu_extension(self, context):
    layout = self.layout
    layout.separator()
    layout.operator("text.comment")
    layout.operator("text.uncomment")
    
bpy.types.TEXT_MT_toolbox.append(right_click_menu_extension)                   