#!/usr/bin/env python3
from collections import OrderedDict

class FieldClass(type):

    def __prepare__(name, bases, **kwds):
        return OrderedDict()

    def __new__(metacls, name, bases, namespace):
        result = type.__new__(metacls, name, bases, namespace)
        result._creators = [v for v in namespace.values() if hasattr(v, "_field")]
        return result

def register_field(name):
    def decorator(func):
        func._field = name
        return func
    return decorator

class Metacard(metaclass=FieldClass):

    def prepare(self, inputs, **kwds):
        pass

    def __call__(self, inputs):
        self.prepare(inputs)
        fields = {}
        for creator in self._creators:
            fields[creator._field] = creator(self)
        return fields


class ExampleCard(Metacard):

    def prepare(self, inputs):
        self.word = inputs

    @register_field("English")
    def English(self):
        return self.word

    @register_field("German")
    def German(self):
        return self.word.upper()

    @register_field("POS")
    def pos(self):
        return "n"

e = ExampleCard()
print(e("petal"))
