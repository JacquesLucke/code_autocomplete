from . extend_word_operators import get_extend_word_operators
from . api_context_operators import get_api_context_operators
from . suggestions_from_before import get_suggestion_from_text_before
from . bpy_ops_operators import get_bpy_ops_operators
from . parameter_operators import get_parameter_operators
from . dynamic_snippets_operators import get_dynamic_snippets_operators
from . assign_or_compare_operators import get_assign_or_compare_operators

def get_text_operators(text_block):
    operators = []
    operators.extend(get_dynamic_snippets_operators(text_block))
    operators.extend(get_assign_or_compare_operators(text_block))
    operators.extend(get_parameter_operators(text_block))
    operators.extend(get_bpy_ops_operators(text_block))    
    operators.extend(get_suggestion_from_text_before(text_block))
    operators.extend(get_api_context_operators(text_block))
    operators.extend(get_extend_word_operators(text_block))
    return operators