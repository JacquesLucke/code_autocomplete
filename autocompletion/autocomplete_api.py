from .. text_block import TextBlock

class AutocompleteProvider:
    def complete(self, text_block, filepath = ""):
        return []
        
class Completion:
    def __getattr__(self, name):
        if name == "name":
            return ""
        if name == "description":
            return ""
        if name == "type":
            return ""