import bpy
        
random_select_sequence = "random select sequence"

class InsertTextOperator:
    def __init__(self, name, text):
        self.display_name = name
        self.insert_text = text
        self.align = "CENTER"
        
    def execute(self, text_block):
        line_index = text_block.current_line_index
        text_parts = []
        for i, text_line in enumerate(text_block.lines):
            text_parts.append(text_line.body)
            if i == line_index:
                text_parts.append(self.insert_text + random_select_sequence)
        text = "\n".join(text_parts)
        text_block.from_string(text)
        select_text_by_replacing(random_select_sequence)
        