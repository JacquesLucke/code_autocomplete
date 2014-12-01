import bpy, inspect, re
from script_auto_complete.operators.text_operators import *
from script_auto_complete.text_editor_utils import *

def get_api_context_operators():
    operators = []
    last_word = get_last_word()
    word_start = get_word_start()
    words = get_properties_after_name(last_word)
    secondary_operators = []
    for word in words:
        if word[0].startswith(word_start):
            operators.append(ExtendWordOperator(word[0], word[1]))
        elif word_start in word[0]:
            secondary_operators.append(ExtendWordOperator(word[0], word[1]))
    return operators + secondary_operators
   
    
members = inspect.getmembers(bpy.types)

api_classes = {}
for member in members:
    api_classes[member[0]] = member[1]
def insert_name(name):
    if name not in sub_property_names:
        sub_property_names[name] = set()
def assign_pointer_to_name(name, target_class_name):
    global sub_property_names
    insert_name(name)
    for sub_property in api_classes[target_class_name].bl_rna.properties:
        sub_property_names[name].update([(sub_property.identifier, sub_property.description)])
    for sub_property in api_classes[target_class_name].bl_rna.functions:
        sub_property_names[name].update([(sub_property.identifier, sub_property.description)])
        
def get_properties_after_name(name):
    properties = sub_property_names.get(name)
    if properties is None: return []
    
    return sorted(list(properties))
    


sub_property_names = {}

for member in reversed(members):
    member_properties = member[1].bl_rna.properties
    for member_property in member_properties:
        if member_property.type == "POINTER":
            assign_pointer_to_name(member_property.identifier, member_property.fixed_type.identifier)
        if member_property.type == "COLLECTION":
            try:
                assign_pointer_to_name(member_property.identifier, member_property.srna.identifier)
            except: pass
                
            
assign_pointer_to_name("context", "Context") 
assign_pointer_to_name("active_object", "Object") 
assign_pointer_to_name("data", "BlendData") 

    