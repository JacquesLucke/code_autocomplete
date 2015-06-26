import jedi
import re
from . interface import Provider, Completion
from . generate_fake_bpy import fake_package_name


class JediCompletion(Completion):
    def __init__(self, suggestion):
        self.name = suggestion.name
        self.description = suggestion.docstring(raw = True)
        if suggestion.type == "function": self.type = "FUNCTION"
        if suggestion.type == "class": self.type = "CLASS"
        if suggestion.type == "param":
            self.type = "PARAMETER"
        
    def insert(self, text_block):
        text_block.replace_current_word(self.name)
      
      
class JediCompletionProvider(Provider):
    def complete(self, text_block):
        source, line_index, character_index, filepath = get_completion_source(text_block)
        
        # jedi raises an error when trying to complete parts of the bpy module
        try:
            script = jedi.Script(source, line_index, character_index, filepath)
            completions = script.completions()
            return [JediCompletion(c) for c in completions if c.name != fake_package_name]
        except:
            return []
        
def get_completion_source(text_block):
    text = text_block.text
    text = replace_import_statements(text)
    current_line = text_block.text_before_cursor
    current_line = replace_import_statements(current_line)
    
    line_index = text_block.current_line_index + 1
    character_index = len(current_line)
    filepath = text_block.filepath
    return text, line_index, character_index, filepath
    
def replace_import_statements(text):
    text = text.replace("import bpy", "import {} as bpy".format(fake_package_name))
    text = re.sub("from bpy", "from {}".format(fake_package_name), text)
    return text