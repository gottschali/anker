#!/usr/bin/env python3
from anker.meta import Metacard, field

class ExampleCard(Metacard):
    _field_Reverse = "y"
    picture_field = "German"
    audio_field = "pos"

    def prepare(self, inputs):
        self.word = inputs

    @field
    def English(self):
        return self.word

    @field("German")
    def german_(self):
        return self.word.upper()

    @field
    def pos(self):
        return "n"

# e = ExampleCard()
# print(e("petal"))
