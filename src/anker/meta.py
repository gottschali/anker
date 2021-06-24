#!/usr/bin/env python3
from collections import OrderedDict
from uuid import uuid4
from anker.connect import fieldNames
from abc import ABCMeta, abstractmethod

"""
3 options to register a field

- Class attribute prefixed with _field
e.g. for the field Family

class English(Vocab):
    _field_Family = "English Vocabulary"

suited for static content

- Class method decorated with @field
e.g. the field German

class English(Vocab):
    @field
    def German(self):
        return self.word.translate("german")

suited for dynamic content

- Decorator with field name as argument

e.g. the field 'more examples'
class English(Vocab):
    @field('more examples')
    def more_examples(self):
        return find_contex(self.word)

- suited if the field name is not a valid python identifier
  The name of the decorated function does not matter

"""

class FieldClass(type):
    """ Need to use a metaclass to override class instantiation
    and register decorated field functions. """
    __metaclass__ = ABCMeta

    def __prepare__(name, bases, **kwds):
        return OrderedDict()

    @abstractmethod
    def prepare(self, inputs, **kwds):
        pass

    def __new__(metacls, name, bases, namespace):
        result = type.__new__(metacls, name, bases, namespace)
        result._creators = [v for v in namespace.values() if hasattr(v, "_field")]
        return result

def field(arg):
    """
    Registers a method as a field creator.
    It take the name of the function as the name of the field
    or if given the argument of the decorator
    """
    # The hack is to set the _field attribute.
    if hasattr(arg, '__call__'): # Works for methods
        arg._field = arg.__name__
        return arg
    else: # Is this needed ?
        def wrapped(expr):
            expr._field = arg
            return expr
        return wrapped


class MetaCard(metaclass=FieldClass):
    """ All cards need to inherit from this class """
    # Set some default values that may be overridden
    deck_name = "Anker"
    model_name = "Basic"
    tags = ["anker"] # TODO Give a timestamp as subtag

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"{type(self).__name__}()"

    def hook(self):
        pass

    def _fields(self):

        # TODO construct object in __init__ and only call methods each step
        field_names = fieldNames(self.model_name)
        fields = OrderedDict((k, "") for k in field_names)
        for creator in self._creators:
            fields[creator._field] = creator(self) or ""

        for attr in dir(self):
            sentinel = "_field_"
            if attr.startswith(sentinel):
                field_name = attr.lstrip(sentinel)
                fields[field_name] = getattr(self, attr) or ""

        return fields

    def __build(self, fields, *args, **kwargs):
        """ Build the parameters for an AnkiConnect Note object"""
        options = kwargs.get("options", {})
        params = {
            "note": {
                "deckName": self.deck_name,
                "modelName": self.model_name,
                "options": options,
                "tags": self.tags,
            }
        }
        for media in ("audio", "picture", "video"):
            media_attr = media + "_field"
            if hasattr(self, media_attr):
                field = getattr(self, media_attr)
                url = fields.pop(field)
                params["note"][media] = [{
                    "url": url,
                    "filename": str(uuid4()),
                    "fields": [ field ]
                }]

        params["note"]["fields"] = fields
        return fields, params

    def __call__(self, inputs, *args, **kwargs):
        self.prepare(inputs)

        self.hook()
        fields, params = self.__build(self._fields(), *args, **kwargs)

        fields = list(fields.items())
        return fields, params
