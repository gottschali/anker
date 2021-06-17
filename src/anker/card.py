#!/usr/bin/env python3
from .vocabulary import Vocabulary

"""
Idea: Subclass Vocabulary to create a custom card
For each field an attribute with that name that generates the content

TODO
- empty fields can be left out
- sometimes a function not needed (data attribute ?)

- Inheritance, keep them stored in nice location

- Auto generate skeleton
"""

class Card(Vocabulary):

    def English(self):
        self.word

    def German(self):
        return word_translation

    def POS(self):
        return pos

    def Example(self):
        return context

    def NotEnglish(self):
        return synonyms

    def Extra(self):
        return antonyms

    def EE(self):
        return description

    def NotGerman(self):
        return ""

    def Reverse(self):
        return "y"

    def Family(self):
        return "ANKER IMPORT"

    def Phonetics(self):
        return phonetics

    def Image(self):
        return ""

    def Mnemonic(self):
        return ""

    def Audio(self):
        return ""
