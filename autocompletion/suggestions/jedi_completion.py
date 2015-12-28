import re
from . interface import Provider, Completion
from . generate_fake_bpy import fake_package_name

try: import jedi
except: print("jedi library not found")

def jedi_module_found():
    return "jedi" in globals()

class JediCompletion(Completion):
    def __init__(self, suggestion):
        self.name = suggestion.name
        self.description = suggestion.docstring()
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
        # or when the jedi module is not found
        try:
            script = jedi.Script(source, line_index, character_index, filepath)
            completions = script.completions()
            ignored_words = (fake_package_name, "_bpy_path")
            return [JediCompletion(c) for c in completions if c.name not in ignored_words]
        except:
            return []

def get_completion_source(text_block):
    new_lines = []
    corrected_line_number = 0
    for line_number, line in enumerate(text_block.iter_lines()):
        new_lines.extend(list(iter_corrected_lines_from_line(line)))
        if line_number == text_block.current_line_index:
            corrected_line_number = len(new_lines)
    text = "\n".join(new_lines)

    filepath = text_block.filepath
    character_index = len(text_block.text_before_cursor)
    return text, corrected_line_number, character_index, filepath

def iter_corrected_lines_from_line(line):
    if "bpy" in line:
        line = line.replace("import bpy", "import {} as bpy".format(fake_package_name))
        line = line.replace("from bpy", "from {}".format(fake_package_name))
    yield line

    if "def draw(self, context):" in line:
        indentation = line.index("d") + 4
        yield " " * indentation + "context = bpy.__private__.context.Context()"
        yield " " * indentation + "self.layout = bpy.__private__.uilayout.UILayout()"

    if "def execute(self, context):" in line or \
       "def poll(cls, context):" in line:
        indentation = line.index("d") + 4
        yield " " * indentation + "context = bpy.__private__.context.Context()"

    if "def invoke(self, context, event):" in line or \
       "def modal(self, context, event):" in line:
        indentation = line.index("d") + 4
        yield " " * indentation + "context = bpy.__private__.context.Context()"
        yield " " * indentation + "event = bpy.__private__.event.Event()"
