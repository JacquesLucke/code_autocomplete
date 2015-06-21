from . jedi_completion import JediCompletionProvider

jedi_provider = JediCompletionProvider()

def complete(text_block):
    completions = []
    completions.extend(jedi_provider.complete(text_block))
    
    primary, secondary = [], []
    for c in completions:
        if c.type == "PARAMETER": primary.append(c)
        else: secondary.append(c)
    
    return primary + secondary