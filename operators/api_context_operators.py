import bpy, inspect, re
from script_auto_complete.operators.text_operators import *

def get_api_context_operators():
    operators = []
    last_word = get_last_word()
    word_start = get_word_start()
    words = get_words_after_name(last_word)
    secondary_operators = []
    for word in words:
        if word.startswith(word_start):
            operators.append(ExtendWordOperator(word))
        elif word_start in word:
            secondary_operators.append(ExtendWordOperator(word))
    return operators + secondary_operators
    
    
def get_word_start():
    text_block = bpy.context.space_data.text
    text_line = text_block.current_line
    text = text_line.body
    character_index = text_block.current_character
    return text[get_word_start_index(text, character_index):character_index]
    
word_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789"
def get_word_start_index(text, character_index):
    for i in reversed(range(0, character_index)):
        if text[i].upper() not in word_characters:
            return i + 1
    return 0
    

def get_last_word():
    text_block = bpy.context.space_data.text
    text_line = text_block.current_line
    character_index = text_block.current_character
    line = text_line.body[:character_index]
    
    is_word_before = False
    word_before = ""
    for char in reversed(line):
        if is_word_before:
            if is_variable_char(char): word_before = char + word_before
            else: break
        else:
            if char == ".":
                is_word_before = True
                continue
            if is_variable_char(char): continue
            else: break
    return word_before

variable_chars = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789")
def is_variable_char(char):
    return char.upper() in variable_chars

    
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
        sub_property_names[name].update([sub_property.identifier])
    for sub_property in api_classes[target_class_name].bl_rna.functions:
        sub_property_names[name].update([sub_property.identifier])
# def assign_collection_to_name(name, collection_class_name):
    # global sub_property_names
    # insert_name(name)
    # sub_property_names[name].update(["get
        
def get_words_after_name(name):
    words = sub_property_names.get(name)
    if words is None: return []
    
    return sorted(list(words))
    


sub_property_names = {}

for member in reversed(members):
    member_properties = member[1].bl_rna.properties
    for member_property in member_properties:
        if member_property.type == "POINTER":
            assign_pointer_to_name(member_property.identifier, member_property.fixed_type.identifier)
        if member_property.type == "COLLECTION":
            try:
                assign_pointer_to_name(member_property.identifier, member_property.srna.identifier)
                print(member_property.identifier, member_property.srna.identifier)
            except: pass
                
            
assign_pointer_to_name("context", "Context") 
assign_pointer_to_name("active_object", "Object") 
assign_pointer_to_name("data", "BlendData") 

    