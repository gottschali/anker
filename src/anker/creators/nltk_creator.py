#!/usr/bin/env python3

from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet

class Nltk:
    def __call__(self, word):
        self.word = word
        self._syns_computed = False

    def synonyms(self):
        if not self._syns_computed:
            self._syns_computed = True
            self.synonyms_and_antonyms()
        return self._synonyms

    def antonyms(self):
        if not self._syns_computed:
            self._syns_computed = True
            self.synonyms_and_antonyms()
        return self._antonyms

    def synonyms_and_antonyms(self):
        self._antonyms = []
        self._synonyms = []
        for syn in wordnet.synsets(self.word):
            for l in syn.lemmas():
                self._synonyms.append(l.name())
                if l.antonyms():
                    self._antonyms.append(l.antonyms()[0].name())


    def pos(self, context=None):
        src = context if context else self.word
        tokens = word_tokenize(src)
        tagged = pos_tag(tokens)
        try:
            _, tag = tagged[tokens.index(self.word)]
            return tag
        except ValueError:
            # No exact mach found
            for i, t in enumerate(tokens):
                if self.word in t:
                    _, tag = tagged[i]
                    return tag
