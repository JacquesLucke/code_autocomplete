from script_auto_complete.operators.extend_word_operators import get_extend_word_operators

def get_text_operators():
    operators = []
    operators.extend(get_extend_word_operators())
    return operators