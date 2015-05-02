import bpy
from . text_block import TextBlock

class SelectWholeString(bpy.types.Operator):
    bl_idname = "script_auto_complete.select_whole_string"
    bl_label = "Select Whole String"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        text = getattr(context.space_data, "text", None)
        if not text: return {"CANCELLED"}
    
        text_block = TextBlock(text)
        
        line = text_block.current_line_index
        character_index = text_block.current_character_index
        
        string_letter = text_block.get_string_definition_type(line, character_index)
        if string_letter is None: return {"CANCELLED"}
        start, end = text_block.get_range_surrounded_by_letter(line, string_letter, character_index)
        if start != end:
            text_block.set_selection_in_line(start, end)
            
        return {"FINISHED"}
