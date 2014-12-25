from script_auto_complete.text_operators import ExtendWordOperator
from script_auto_complete.documentation import get_documentation
from operator import attrgetter

def get_api_context_operators(text_block):
    documentation = get_documentation()
    parent_word = text_block.parent_of_current_word
    attributes = documentation.get_possible_subattributes_of_property(parent_word)
    
    current_word = text_block.current_word.lower()
    operators = []
    secondary_operators = []
    for attribute in attributes:
        attribute_name = attribute.name.lower()
        if attribute_name.startswith(current_word):
            operators.append(ExtendWordOperator(attribute.name, additional_data = attribute))
        elif current_word in attribute_name:
            secondary_operators.append(ExtendWordOperator(attribute.name, additional_data = attribute))
            
    operators.sort(key = attrgetter("display_name"))
    secondary_operators.sort(key = attrgetter("display_name"))
    return operators + secondary_operators


    