#!/usr/bin/env python3
from nltk.stem import PorterStemmer

from anker.meta import MetaCard

"""
Idea: Subclass Vocabulary to create a custom card
For each field an attribute with that name that generates the content

- Auto generate skeleton ?
"""

class Vocabulary(MetaCard):
    stemmer = PorterStemmer()

    def prepare(self, inputs, **kwds):
        word, *rest = inputs.split()
        self.word = word.strip()
        self.normalized = self.word.lower()
        if rest:
            self.example = " ".join(rest)

    @property
    def stem(self):
        return self.stemmer.stem(self.normalized)

    def markup(self, sentence):
        if sentence:
            i = sentence.index(self.word)
            n = len(self.word)
            cls = self.pos if hasattr(self, "pos") else ""
            return sentence[:i] + f"<i class={cls}>" + self.word + "</i>" + sentence[i+n:]



