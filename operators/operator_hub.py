from script_auto_complete.operators.extend_word_operators import get_extend_word_operators
from script_auto_complete.operators.insert_template_operators import get_insert_template_operators
from script_auto_complete.operators.api_context_operators import get_api_context_operators
from script_auto_complete.operators.suggestions_from_before import get_suggestion_from_text_before
from script_auto_complete.operators.bpy_ops_operators import get_bpy_ops_operators
from script_auto_complete.operators.dynamic_snippets_operators import get_dynamic_snippets_operators

def get_text_operators(text_block):
    operators = []
    operators.extend(get_insert_template_operators(text_block))
    operators.extend(get_dynamic_snippets_operators(text_block))
    operators.extend(get_bpy_ops_operators(text_block))
    operators.extend(get_suggestion_from_text_before(text_block))
    operators.extend(get_api_context_operators(text_block))
    operators.extend(get_extend_word_operators(text_block))
    return operators