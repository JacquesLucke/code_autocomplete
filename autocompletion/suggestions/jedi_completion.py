import jedi
from . interface import Provider, Completion


class JediCompletion(Completion):
    def __init__(self, suggestion):
        self.name = suggestion.name
        self.insertion = suggestion.name
        self.description = suggestion.docstring(raw = True)
        if suggestion.type == "function": self.type = "FUNCTION"
        if suggestion.type == "class": self.type = "CLASS"
        if suggestion.type == "param":
            self.type = "PARAMETER"
        
    def insert(self, text_block):
        text_block.replace_current_word(self.insertion)
      
      
class JediCompletionProvider(Provider):
    def complete(self, text_block):
        source = text_block.text
        line_index = text_block.current_line_index + 1
        character_index = text_block.current_character_index
        filepath = text_block.filepath
        
        # jedi raises an error when trying to complete parts of the bpy module
        try:
            script = jedi.Script(source, line_index, character_index, filepath)
            completions = script.completions()
        except:
            completions = []
        
        return [JediCompletion(c) for c in completions]
        