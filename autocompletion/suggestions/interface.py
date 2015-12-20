class Provider:
    def complete(self, text_block):
        return []

class Completion:
    def __getattr__(self, name):
        if name == "name":
            return ""
        if name == "description":
            return ""
        if name == "type":
            return "UNKNOWN"
        if name == "finished_statement":
            return True

    def insert(self, text_block):
        pass
