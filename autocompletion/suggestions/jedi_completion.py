import jedi
from . interface import Provider, Completion


class JediCompletion(Completion):
    def __init__(self, suggestion):
        self.name = suggestion.name
      
      
class JediCompletionProvider(Provider):
    def complete(self, text_block):
        source = text_block.text
        line_index = text_block.current_line_index + 1
        character_index = text_block.current_character_index
        filepath = text_block.filepath
        
        script = jedi.Script(source, line_index, character_index, filepath)
        completions = script.completions()
        
        return [JediCompletion(c) for c in completions]
        