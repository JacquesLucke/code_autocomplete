import bpy, keyword
from script_auto_complete.text_editor_utils import *
from script_auto_complete.operators.text_operators import *
from script_auto_complete.operators.context_words import *


def get_context_word_operators():
    operators = []
    text_before = get_text_since_last_dot()
    word_start = get_word_start()
    pairs = get_before_after_pairs()
    for before, after_list in pairs.items():
        if text_before.endswith(before):
            for after in after_list:
                if after.startswith(word_start):
                    operators.append(ExtendWordOperator(after))
    return operators
    