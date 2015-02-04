import bpy

class TextEditorInfo:
    def __init__(self):
        context = bpy.context
        
        space = context.space_data
        region = context.region

        text_block = space.text
        
        self.visible_lines = space.visible_lines
        self.top_line_index = space.top
        self.text_block = text_block
        self.line_index = text_block.current_line_index
        self.character_index = text_block.current_character
        
        self.width = region.width
        self.height = region.height
        
        self.line_height = self.height / self.visible_lines
        self.character_width = self.line_height * 0.436
        
        self.visible_line_index = self.line_index - self.top_line_index
        
        if hasattr(space, "region_location_from_cursor"): # this function is supported from 2.74
            self.cursor_position = list(space.region_location_from_cursor(self.line_index, self.character_index))
            self.cursor_position[0] -= self.character_width * 2
            self.cursor_position[1] += self.line_height
        else:
            self.cursor_position = (
                self.character_width * self.character_index,
                self.height - self.line_height * self.visible_line_index - self.line_height / 2 )
            
        self.scale = self.line_height / 20 
        
def active_text_block_exists():
    return getattr(bpy.context.space_data, "text", None) is not None