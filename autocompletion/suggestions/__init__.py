from . jedi_completion import JediCompletionProvider
from . word_completion import WordCompletionProvider
from ... settings import get_preferences

jedi_provider = JediCompletionProvider()
word_provider = WordCompletionProvider()

def complete(text_block):
    setting = get_preferences().completion_providers

    completions = []
    if setting.use_jedi_completion: completions.extend(jedi_provider.complete(text_block))
    if setting.use_word_completion: completions.extend(word_provider.complete(text_block))

    primary, secondary = [], []
    for c in completions:
        if c.type == "PARAMETER": primary.append(c)
        else: secondary.append(c)

    return primary + secondary
