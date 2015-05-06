import re
from .. text_operators import InsertTextOperator

def get_insert_template_operators(text_block):
    operators = []
    text_before = text_block.text_before_cursor
    for name, pattern, snippet in templates:
        if re.match(pattern, text_before) is not None:
            operators.append(InsertTextOperator(name, snippet))
    return operators
    
    
templates = []
        