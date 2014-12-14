import re

def get_parent_words(text):
    parents = []
    while True:
        parent = get_parent_word(text)
        if parent == None: break
        text = text[:-len(get_current_word(text))-1]
        parents.append(parent)
    parents.reverse()
    return parents
    
def get_text_after_match(pattern, text):
    match = None
    for match in re.finditer(pattern, text):
        pass
    if match:
        return text[match.end():]

def get_current_word(text):
    match = re.search("(?!\w*\W).*", text)
    if match: 
        return match.group()
    return ""
    
def get_parent_word(text):
    match = re.search("(\w+)\.(?!.*\W)", text)
    if match:
        return match.group(1)
    return None