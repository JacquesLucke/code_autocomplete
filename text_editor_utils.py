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
     
     
def get_word_start():
    text_block = bpy.context.space_data.text
    text_line = text_block.current_line
    text = text_line.body
    character_index = text_block.current_character
    return text[get_word_start_index(text, character_index):character_index]
    
word_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789"
def get_word_start_index(text, character_index):
    for i in reversed(range(0, character_index)):
        if text[i].upper() not in word_characters:
            return i + 1
    return 0
    
  
def get_text_since_last_dot():
    text_block = bpy.context.space_data.text
    text_line = text_block.current_line
    character_index = text_block.current_character
    line = text_line.body[:character_index]
    index = line.rfind(".")
    if index > 0:
        line = line[:index]
    return line
     
     
def get_last_word():
    text_block = bpy.context.space_data.text
    text_line = text_block.current_line
    character_index = text_block.current_character
    line = text_line.body[:character_index]
    
    is_word_before = False
    word_before = ""
    for char in reversed(line):
        if is_word_before:
            if is_variable_char(char): word_before = char + word_before
            else: break
        else:
            if char == ".":
                is_word_before = True
                continue
            if is_variable_char(char): continue
            else: break
    return word_before

variable_chars = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789")
def is_variable_char(char):
    return char.upper() in variable_chars
    
    
        
def active_text_block_exists():
    return getattr(bpy.context.space_data, "text", None) is not None
    
def set_text_cursor_position(line_index, character_index):
    current_line_index = bpy.context.space_data.text.current_line_index
    line_changes = abs(current_line_index - line_index)
    
    if current_line_index > line_index: move_direction = "PREVIOUS_LINE"
    else: move_direction = "NEXT_LINE"
    
    for i in range(line_changes):
        bpy.ops.text.move(type = move_direction)
        
    bpy.ops.text.move(type = "LINE_BEGIN")
    for i in range(character_index):
        bpy.ops.text.move(type = "NEXT_CHARACTER")
    
def get_existing_words():
    existing_words = []
    text = bpy.context.space_data.text.as_string()
    all_existing_words = set(re.sub("[^\w]", " ", text).split())
    for word in all_existing_words:
        if not word.isdigit(): existing_words.append(word)
    return existing_words