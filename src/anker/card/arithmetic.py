#!/usr/bin/env python3

from anker.meta import MetaCard, field
from anker.formatter import mathjax

class Card(MetaCard):
    deck_name = "Test"
    model_name = "Basic"
    tags = ["english::anker::arithmetic"]

    question = "<h3>What's the result? </h3> <hr> "

    def prepare(self, input):
        self.x, self.y = input

    @field
    def Front(self):
        return self.question + f"\( {self.x} * {self.y} \)"

    @field
    @mathjax
    def Back(self):
        return f"= {self.x * self.y }"
