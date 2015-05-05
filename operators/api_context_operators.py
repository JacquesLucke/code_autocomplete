from .. text_operators import ExtendWordOperator
from .. documentation import get_documentation
from operator import attrgetter

# bpy.context.#active_object#
def get_api_context_operators(text_block):
    documentation = get_documentation()
    parent_path = text_block.get_current_parent_path()
    attributes = documentation.get_best_matching_subattributes_of_path(parent_path)
    
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


    