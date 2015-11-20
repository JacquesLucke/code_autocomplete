import re
import bpy
import textwrap
from . interface import Provider, Completion
from . rna_utils import make_operator_description, join_lines


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


class OperatorCompletionProvider(Provider):
    def complete(self, text_block):
        current_word = text_block.current_word
        parents = text_block.parents_of_current_word

        if parents[:2] == ["bpy", "ops"]:
            if len(parents) == 2:
                return to_completions(get_category_completions(current_word))
            if len(parents) == 3:
                return list(iter_operator_completions(current_word, category_name = parents[2]))
        return []

def to_completions(words):
    return [WordCompletion(word) for word in words]

def get_category_completions(current_word):
    return [category for category in dir(bpy.ops) if category.startswith(current_word)]

def iter_operator_completions(current_word, category_name):
    category = getattr(bpy.ops, category_name, None)
    if category is None: return
    for operator_name in dir(category):
        if current_word not in operator_name: continue
        yield OperatorCompletion(category, operator_name)
