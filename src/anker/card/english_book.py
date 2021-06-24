#!/usr/bin/env python3
from pathlib import Path

from .vocabulary import Vocabulary

from anker.meta import field

from anker.creators.context import context
from anker.creators.nltk_creator import Nltk
from anker.creators.google_translator import translate
from anker.creators.webster import Webster
from anker.creators.image_downloader import ImageDownloader

from anker.formatter import html_list, list_to_string

class Card(Vocabulary):
    deck_name = "Eng"
    model_name = "English"
    tags = ["english::vocab::to_kill_a_mockingbird"]

    examples_path = Path("~/Anki/books/to-kill-a-mockingbird.txt").expanduser()
    src_lang = "en"
    dest_lang = "de"

    picture_field = "Image"
    audio_field = "Audio"

    _field_Reverse = "y"
    _field_Family = "To kill a mockingbird"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.webster = Webster()
        self.image_downloader = ImageDownloader()
        self.nltk = Nltk()

    def hook(self):
        self.webster(self.normalized)
        self.image_downloader(self.normalized)
        self.nltk(self.normalized)

    @field
    def English(self):
        return self.word

    @field
    def German(self):
        return translate(self.word, self.src_lang, self.dest_lang)

    @field
    def POS(self):
        tag = self.nltk.pos()
        # Map the POS to simpler ones
        if tag.startswith('RB'):
            return "adv"
        elif tag.startswith('JJ'):
            return "adj"
        elif tag.startswith('NN'):
            return "n"
        elif tag.startswith('VB'):
            return "v"
        elif tag.startswith("JJ") or tag.startswith("IN"):
            return "conj"

    @field
    def Example(self):
        if hasattr(self, "example"):
            return self.markup(self.example)
        else:
            return self.markup(context(self.word, self.examples_path))

    @field
    @list_to_string
    def NotEnglish(self):
        return self.nltk.synonyms()

    @field
    @list_to_string
    def Extra(self):
        return self.nltk.antonyms()

    @field
    @html_list
    def EE(self):
        return self.webster.definitions()

    @field
    def Phonetics(self):
        return self.webster.phonetics()

    @field
    def Audio(self):
        return self.webster.pronunciation()

    @field
    def Image(self):
        return self.image_downloader.image()

