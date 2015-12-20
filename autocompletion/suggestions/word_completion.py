import re
from . interface import Provider, Completion


class WordCompletion(Completion):
    def __init__(self, word):
        self.name = word

    def insert(self, text_block):
        text_block.replace_current_word(self.name)


class WordCompletionProvider(Provider):
    def complete(self, text_block):
        words = text_block.get_existing_words()
        current_word = text_block.current_word
        if current_word in words: words.remove(current_word)
        words = sort_words(words, current_word)
        return [WordCompletion(word) for word in words]

def sort_words(words, current_word):
    current_word = current_word.lower()
    best_matches, other_matches = [], []
    words.sort(key = str.lower)
    for word in words:
        if word.lower().startswith(current_word):
            best_matches.append(word)
        elif current_word in word.lower():
            other_matches.append(word)
    return best_matches + other_matches
