#!/usr/bin/env python3
from anker.meta import MetaCard, field

class Card(MetaCard):
    deck_name = "Default"
    model_name = "English"
    tags = ["english::idioms"]

    _field_Family = "Idioms"

    def prepare(self, inputs, **kwds):
        self.idiom, self.meaning, self.example = inputs

    @field
    def English(self):
        return self.idiom

    @field
    def EE(self):
        return self.meaning

    @field
    def Example(self):
        return self.example
