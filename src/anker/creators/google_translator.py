#!/usr/bin/env python3

from googletrans import Translator

translator = Translator()

# Needs context
def translate_context(vocab):
    if hasattr(vocab, "context"):
        translation = translator.translate(vocab.context, src=vocab.language, dest=vocab.target)
        return translation.text

def translate_word(vocab):
    translation = translator.translate(vocab.normalized, src=vocab.language, dest=vocab.target)
    return translation.text
