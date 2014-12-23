class ExtendWordOperator:
    def __init__(self, target_word, additional_data = None, align = "LEFT"):
        self.target_word = target_word
        self.display_name = target_word
        self.additional_data = additional_data
        self.align = align
        
    def execute(self, text_block):
        text_block.replace_current_word(self.target_word)


class InsertTextOperator:
    def __init__(self, name, text):
        self.display_name = name
        self.insert_text = text
        self.align = "CENTER"
        
    def execute(self, text_block):
        text_block.insert(self.insert_text)
        
        
class DynamicSnippetOperator:
    def __init__(self, name, function, additional_data):
        self.display_name = name
        self.function = function
        self.additional_data = additional_data
        self.align = "CENTER"
        
    def execute(self, text_block):
        self.function(text_block, self.additional_data)       