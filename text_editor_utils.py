import bpy, re

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
        
        self.cursor_position = (
            self.character_width * self.character_index,
            self.height - self.line_height * self.visible_line_index - self.line_height / 2 )
            
        self.scale = self.line_height / 20
        
def active_text_block_exists():
    return bpy.context.space_data.text is not None
    
def select_text_by_replacing(text):
    space = bpy.context.space_data
    space.find_text = text
    space.replace_text = ""
    space.use_find_wrap = True
    space.use_find_all = False
    bpy.ops.text.replace()
    bpy.ops.text.replace()
    
def get_existing_words():
    existing_words = []
    text = bpy.context.space_data.text.as_string()
    all_existing_words = set(re.sub("[^\w]", " ", text).split())
    for word in all_existing_words:
        if not word.isdigit(): existing_words.append(word)
    return existing_words