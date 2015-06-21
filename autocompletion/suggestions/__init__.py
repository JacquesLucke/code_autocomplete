from . jedi_completion import JediCompletionProvider

jedi_provider = JediCompletionProvider()

def complete(text_block):
    completions = []
    completions.extend(jedi_provider.complete(text_block))
    return completions