import jedi
import re
from . interface import Provider, Completion
from . generate_fake_bpy import fake_package_name


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
        try:
            script = jedi.Script(source, line_index, character_index, filepath)
            completions = script.completions()
            return [JediCompletion(c) for c in completions if c.name != fake_package_name]
        except:
            return []

def get_completion_source(text_block):
    current_line_number = text_block.current_line_index + 1
    new_current_line_number = None
    character_index = len(text_block.text_before_cursor)
    filepath = text_block.filepath

    new_lines = []
    for i, line in enumerate(text_block.iter_lines()):
        line_number = i + 1
        new_lines.extend(list(iter_corrected_lines_from_line(line)))
        if line_number == current_line_number:
            new_current_line_number = len(new_lines)

    text = "\n".join(new_lines)
    return text, new_current_line_number, character_index, filepath

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
