#!/usr/bin/env python3
from anker.meta import MetaCard
from anker.connect import fieldNames
from collections import OrderedDict

class Card(MetaCard):
    """May be used as a pass though if the cards are already created and only have to be pushed to Anki.
    For example you exported to csv, made some changes and then use the CSV fetcher and this Proxy card"""
    deck_name = "Eng"
    model_name = "English"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def prepare(self, inputs):
        self.row = inputs

    def _fields(self):
        # Overloads fields creation
        field_names = fieldNames(self.model_name)
        print(field_names, self.row)
        return OrderedDict((k, r) for k, r in zip(field_names, self.row))
