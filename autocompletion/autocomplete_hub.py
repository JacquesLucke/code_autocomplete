from . autocomplete_api import AutocompleteProvider, Completion
from . jedi_completion import JediCompletionProvider

jedi_provider = JediCompletionProvider()

class AutocompleteHub(AutocompleteProvider):
    def complete(self, text_block, filepath = ""):
        completions = []
        completions.extend(jedi_provider.complete(text_block, filepath))
        return completions
        