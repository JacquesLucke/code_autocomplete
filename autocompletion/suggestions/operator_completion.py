import re
import bpy
import textwrap
from . interface import Provider, Completion
from . rna_utils import (get_enum_items,
                         get_property_default,
                         get_enum_items_string,
                         get_operator_parameters,
                         make_operator_description,
                         get_readable_property_type)


class WordCompletion(Completion):
    def __init__(self, word):
        self.name = word

    def insert(self, text_block):
        text_block.replace_current_word(self.name)

class OperatorCompletion(Completion):
    def __init__(self, category, operator_name):
        self.operator = getattr(category, operator_name)
        self.name = operator_name

    def insert(self, text_block):
        text_block.replace_current_word(self.name)

    @property
    def description(self):
        return make_operator_description(self.operator)

class ParameterCompletion(Completion):
    def __init__(self, parameter):
        self.name = parameter.identifier + " = "
        self.type = "OPERATOR_PARAMETER"
        self.description = "{} ({}) = {}\n\n{}\n{}".format(
                                parameter.name,
                                get_readable_property_type(parameter),
                                get_property_default(parameter),
                                parameter.description,
                                get_enum_items_string(parameter, 70))

    def insert(self, text_block):
        text_block.replace_current_word(self.name)


class OperatorCompletionProvider(Provider):
    def complete(self, text_block):
        current_word = text_block.current_word
        parents = text_block.parents_of_current_word
        operator = get_current_operator(text_block)

        if parents[:1] == ["bpy"]:
            if len(parents) == 1 and "ops".startswith(current_word):
                return [WordCompletion("ops")]

        operator = get_current_operator(text_block)
        if operator is not None:
            return list(iter_operator_inner_completions(operator, text_block))

        completions = []
        completions.extend(iter_operator_completion_after_pattern(text_block, "bpy\.ops\."))
        completions.extend(iter_operator_completion_after_pattern(text_block, "\.operator\((\"|\')"))
        completions.extend(iter_operator_completion_after_pattern(text_block, "keymap_items\.new\((\"|\')"))
        return completions

# pattern#text#.#move#
def iter_operator_completion_after_pattern(text_block, pattern = ""):
    operator_start = text_block.get_current_text_after_pattern(pattern)
    if operator_start is None: return
    if "." not in operator_start:
        yield from get_category_completions(operator_start)
    else:
        category, operator_name_start  = operator_start.split(".", maxsplit = 1)[:2]
        yield from iter_operator_completions(operator_name_start, category_name = category)

# bpy.ops.#text#
def get_category_completions(current_word):
    return [WordCompletion(category) for category in dir(bpy.ops) if category.startswith(current_word)]

# bpy.ops.text.#move#
def iter_operator_completions(current_word, category_name):
    category = getattr(bpy.ops, category_name, None)
    if category is None: return
    for operator_name in dir(category):
        if current_word not in operator_name: continue
        yield OperatorCompletion(category, operator_name)

def get_current_operator(text_block):
    function_path = text_block.get_current_function_path()
    if function_path is None: return None

    parts = function_path.split(".")
    if len(parts) != 4: return None
    if not function_path.startswith("bpy.ops"): return None
    category_name, operator_name = parts[2:]
    category = getattr(bpy.ops, category_name, None)
    if category is None: return None
    operator = getattr(category, operator_name, None)
    return operator

# bpy.ops.text.move(#type# = "#NEXT_CHARACTER#")
def iter_operator_inner_completions(operator, text_block):
    yield from iter_parameter_completions(operator, text_block)
    yield from iter_enum_parameter_completions(operator, text_block)

# bpy.ops.text.move(#type# = "NEXT_CHARACTER")
def iter_parameter_completions(operator, text_block):
    word_start = text_block.get_current_text_after_pattern("[\(\,]\s*")
    if word_start is None: return
    for parameter in get_operator_parameters(operator):
        if word_start in parameter.identifier:
            yield ParameterCompletion(parameter)

# bpy.ops.text.move(type = "#NEXT_CHARACTER#")
def iter_enum_parameter_completions(operator, text_block):
    for parameter in get_operator_parameters(operator):
        pattern = parameter.identifier + "\s*=\s*(\"|\')"
        word_start = text_block.get_current_text_after_pattern(pattern)
        if word_start is None: continue
        word_start = word_start.upper()
        for enum_item in get_enum_items(parameter):
            if word_start in enum_item.upper():
                completion = WordCompletion(enum_item)
                yield completion
