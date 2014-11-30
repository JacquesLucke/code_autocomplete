from script_auto_complete.operators.extend_word_operators import get_extend_word_operators
from script_auto_complete.operators.insert_template_operators import get_insert_template_operators
from script_auto_complete.operators.context_word_operators import get_context_word_operators

def get_text_operators():
    operators = []
    operators.extend(get_insert_template_operators())
    operators.extend(get_context_word_operators())
    operators.extend(get_extend_word_operators())
    return operators