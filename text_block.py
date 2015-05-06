import bpy, re

class TextBlock:
    def __init__(self, text_block):
        if text_block is None: raise AttributeError()
        self.text_block = text_block
        
    @classmethod
    def get_active(cls):
        text = getattr(bpy.context.space_data, "text", None)
        if text: return TextBlock(text)
        return None  
        
    @property
    def filepath(self):
        return self.text_block.filepath
        
    @property
    def use_tabs_as_spaces(self):
        return self.text_block.use_tabs_as_spaces
        
    @property
    def current_line(self):
        return self.text_block.current_line.body
    @current_line.setter
    def current_line(self, text):
        self.text_block.current_line.body = text
        
    @property
    def cursor_position(self):
        return self.current_line_index, self.current_character_index
    @cursor_position.setter
    def cursor_position(self, position):
        self.current_line_index = position[0]
        self.current_character_index = position[1]
       
    @property
    def current_character_index(self):
        return self.get_character_index()
    @current_character_index.setter
    def current_character_index(self, index):
        self.set_cursor_position_horizontal(index)
        
    @property
    def current_line_index(self):
        return self.get_line_index()
    @current_line_index.setter
    def current_line_index(self, index):
        self.set_cursor_position_vertical(index)
        
    @property
    def line_amount(self):
        return len(self.text_block.lines)
        
    @property
    def text_before_cursor(self):
        return self.current_line[:self.current_character_index]
        
    @property
    def current_word(self):
        return self.get_last_word(self.text_before_cursor)
    
    @property
    def selected_text(self):
        wm = bpy.context.window_manager
        clipboard = wm.clipboard
        bpy.ops.text.copy()
        text = wm.clipboard
        wm.clipboard = clipboard
        return text
        
    @property
    def lines(self):
        return self.get_all_lines()     
    @lines.setter
    def lines(self, lines):
        cursor_position = self.cursor_position
        text = "\n".join(lines)
        self.text_block.from_string(text)
        self.cursor_position = cursor_position
        
    def get_all_lines(self):
        lines = []
        for line in self.text_block.lines:
            lines.append(line.body)
        return lines
    
    def set_line_text(self, line_index, text):
        self.text_block.lines[line_index].body = text
    
    # 'bpy.context.sce' -> 'sce'
    def get_last_word(self, text):
        match = re.search("(?!\w*\W).*", text)
        if match: return match.group()
        return ""
        
    @property
    def parents_of_current_word(self):
        return self.get_parent_words(self.text_before_cursor)
    
    # 'bpy.context.sce' -> ['bpy', 'context']    
    def get_parent_words(self, text):
        parents = []
        text = self.text_before_cursor
        while True:
            parent = self.get_parent_word(text)
            if parent is None: break
            text = text[:-len(self.get_last_word(text))-1]
            parents.append(parent)
        parents.reverse()
        return parents
        
    @property
    def parent_of_current_word(self):
        return self.get_parent_word(self.text_before_cursor)
    
    # 'bpy.context.sce' -> 'context'
    def get_parent_word(self, text):
        match = re.search("(\w+)\.(?!.*\W)", text)
        if match:
            return match.group(1)
        return None
        
    @property
    def text(self):
        return self.text_block.as_string()
        
    def get_existing_words(self):
        existing_words = []
        existing_parts = set(re.sub("[^\w]", " ", self.text).split())
        for part in existing_parts:
            if not part.isdigit(): existing_words.append(part)
        return existing_words
            
    def insert(self, text):
        self.make_active()
        bpy.ops.text.insert(text = text)
        
    def get_current_text_after_pattern(self, pattern):
        return self.get_text_after_pattern(pattern, self.text_before_cursor)
        
    def get_text_after_pattern(self, pattern, text):
        match = self.get_last_match(pattern, text)
        if match:
            return text[match.end():]
            
    def get_last_match(self, pattern, text):
        match = None
        for match in re.finditer(pattern, text): pass
        return match
        
    def search_pattern_in_current_line(self, pattern):
        return re.search(pattern, self.current_line)
        
    def replace_current_word(self, new_word):
        self.delete_current_word()
        self.insert(new_word)
        
    def delete_current_word(self):
        match = re.search("\w*$", self.text_before_cursor)
        if match:
            length = match.end() - match.start()
            for i in range(length):
                self.remove_character_before_cursor()
    
    # "this.is.a.test(type = 'myt" -> "this.is.a.test"
    def get_current_function_path(self):
        text = self.text_before_cursor
        open_bracket_index = self.get_current_open_bracket_index(text)
        if open_bracket_index == -1: return None
        text_before = text[:open_bracket_index-1]
        match = re.search(r"(\w[\w\.]+\w)$", text_before)
        if match:
            return match.group(1)
        return None
            
    # "test = this.is.anoth" -> "this.is" | "test = this.is.anoth." -> "this.is.anoth"     
    def get_current_parent_path(self):
        path = self.get_current_path()
        if self.text_before_cursor.endswith("."): return path
        match = re.search(r"([\w\.]+)\.(?!.*\.)", path)
        if match:
            return match.group(1)
        return ""
    
    # "test = this.is.anoth" -> "this.is.anoth"
    def get_current_path(self):
        text_before = self.text_before_cursor
        match = re.search("(\w[\w\.]+\w)\.?$", text_before)
        if match:
            return match.group(1)
        return ""
    
    # "    event.type = 't" -> "event.type"
    def get_current_line_assign_variable_path(self):
        text_before = self.text_before_cursor
        match = re.fullmatch("\s*([\w\.]+)\s*=.*", text_before)
        if match:
            return match.group(1)
        return None
    
    # "if event.type == "A" and event.value != 'RE" -> "event.value"
    def get_current_compare_variable_path(self):
        text_before = self.text_before_cursor
        match = self.get_last_match("([\w\.]+)\s*(==|<|>|!=|(not )?in \[)", text_before)
        if match:
            return match.group(1)
        return None
        
    def get_current_open_bracket_index(self, text):
        close_bracket_counter = 0
        current_open_bracket_index = -1
        
        for i, c in enumerate(reversed(text)):
            if c == ")": close_bracket_counter += 1
            elif c == "(":
                if close_bracket_counter > 0: close_bracket_counter -= 1
                else: 
                    current_open_bracket_index = len(text) - i
                    break   
        return current_open_bracket_index
                
    def select_match_in_current_line(self, match):
        if match:
            self.set_selection_in_line(match.start() + 1, match.end() + 1)
                
    def delete_selection(self):
        self.insert(" ")
        self.remove_character_before_cursor()
     
    def get_string_definition_type(self, text, current_index):
        string_letter = None
        for i in range(current_index):
            letter = text[i]
            if letter == '"':
                if string_letter == '"':
                    string_letter = None
                elif string_letter is None: 
                    string_letter = letter
            if letter == "'":
                if string_letter == "'":
                    string_letter = None
                elif string_letter is None: 
                    string_letter = letter
        return string_letter

    def get_range_surrounded_by_letter(self, text, letter, current_index):
        text_before = text[:current_index]
        text_after = text[current_index:]
        
        start_index = text_before.rfind(letter) + 1
        end_index = text_after.find(letter) + len(text_before)
        
        if 0 < start_index < end_index:
            return start_index+1, end_index+1
        return current_index, current_index 
        
    def select_text_in_current_line(self, text):
        line = self.current_line
        start = line.find(text)
        if start != -1:
            end = start + len(text)
            self.set_selection_in_line(start + 1, end + 1)
        
    def set_selection_in_line(self, start, end):
        line = self.current_line_index
        if start > end: start, end = end, start
        self.set_selection(line, start, line, end)
        
    def set_selection(self, start_line, start_character, end_line, end_character):
        self.set_cursor_position(start_line, start_character, select = False)
        self.set_cursor_position(end_line, end_character, select = True)
        
    def set_cursor_position(self, line_index, character_index, select = False):
        self.set_cursor_position_vertical(line_index, select)
        self.set_cursor_position_horizontal(character_index, select)
        
    def set_cursor_position_horizontal(self, target_index, select = False):
        self.move_cursor_to_line_end(select)
        self.move_cursor_left_to_target_index(target_index, select)
            
    def move_cursor_left_to_target_index(self, target_index, select):
        target_index = max(1, target_index)
        while self.get_character_index(select) >= target_index:
            self.move_cursor_left(select)
        
    def set_cursor_position_vertical(self, target_line, select = False):
        move_function = self.move_cursor_up
        if target_line > self.get_line_index(select):
            move_function = self.move_cursor_down
        move_amount = abs(self.current_line_index - target_line)
        for i in range(move_amount):
            move_function(select)
            
    def get_character_index(self, select = False):
        if select: return self.text_block.select_end_character
        return self.text_block.current_character
    def get_line_index(self, select = False):
        return self.text_block.current_line_index
            
    def move_cursor_to_line_begin(self, select = False):
        self.move_cursor("LINE_BEGIN", select)
    def move_cursor_to_line_end(self, select = False):
        self.move_cursor("LINE_END", select)  
        
    # note: this may change the character index more than one (if there is TAB)
    def move_cursor_right(self, select = False):
        self.move_cursor("NEXT_CHARACTER", select)
    def move_cursor_left(self, select = False):
        self.move_cursor("PREVIOUS_CHARACTER", select)   
        
    def move_cursor_up(self, select = False):
        self.move_cursor("PREVIOUS_LINE", select)
    def move_cursor_down(self, select = False):
        self.move_cursor("NEXT_LINE", select)
        
    def move_cursor(self, type, select = False):
        self.make_active()
        if select: bpy.ops.text.move_select(type = type)
        else: bpy.ops.text.move(type = type)
        
    def remove_character_before_cursor(self):
        self.make_active()
        bpy.ops.text.delete(type = "PREVIOUS_CHARACTER")
        
    def line_break(self):
        self.make_active()
        bpy.ops.text.line_break()
        
    def make_active(self):
        bpy.context.space_data.text = self.text_block
        
     