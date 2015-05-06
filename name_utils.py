import re

def get_valid_variable_name(name):
    return re.sub("\W+", "", name)

def get_lower_case_with_underscores(name):
    words = get_words(name)
    words = [word.lower() for word in words]
    output = "_".join(words)
    return output    
    
def get_separated_capitalized_words(name):
    words = get_words(name)
    words = [word.capitalize() for word in words]
    output = " ".join(words)
    return output      
    
def get_words(name):
    words = []
    current_word = ""
    for char in name:
        if char.islower():
            current_word += char
        if char.isupper():
            if current_word.isupper() or len(current_word) == 0:
                current_word += char
            else:
                words.append(current_word)
                current_word = char
        if char == "_":
            words.append(current_word)
            current_word = ""
            
    words.append(current_word)
    words = [word for word in words if len(word) > 0]
    return words  