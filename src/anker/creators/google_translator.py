#!/usr/bin/env python3

from googletrans import Translator

translator = Translator()

def translate(text, src, dest):
    translation = translator.translate(text, src=src, dest=dest)
    return translation.text
