#!/usr/bin/env python3
"""Migrate the ``Languages::Italiano`` Duolingo deck (a ``Basic (and reversed
card)`` note per word: Italian on the front, English on the back) into the rich
``Language`` note type.

Enrichment sources, all best-effort:

* :class:`anker.creators.wiktionary.Wiktionary` -- part of speech, IPA, gender,
  fuller English definitions, and a native pronunciation clip when one exists
* :class:`anker.creators.mymemory.MyMemory` -- the missing Italian->German gloss
* :func:`anker.creators.google_tts.google_tts` -- synthesised audio fallback

Pair it with the ``ankiconnect`` fetcher::

    ANKER_SRC_QUERY='deck:Languages::Italiano tag:duolingo -note:Language' \\
        anker -c italian_vocab -f ankiconnect -o italiano.csv

For a resumable, rate-limited bulk run use ``scripts/migrate_italiano.py`` instead.
"""
import re

from anker.meta import MetaCard, field
from anker.creators.wiktionary import Wiktionary
from anker.creators.mymemory import MyMemory
from anker.creators.google_tts import google_tts

_ARTICLES = ("il ", "lo ", "la ", "i ", "gli ", "le ", "l'", "un ", "uno ", "una ", "un'")
_POS_MAP = {
    "Noun": "n", "Verb": "v", "Adjective": "adj", "Adverb": "adv",
    "Preposition": "prep", "Conjunction": "conj", "Pronoun": "pron",
    "Numeral": "num", "Interjection": "interj", "Article": "art",
    "Proper noun": "n",
}


def strip_article(term):
    low = term.lower()
    for art in _ARTICLES:
        if low.startswith(art):
            return term[len(art):].strip()
    return term.strip()


class Card(MetaCard):
    deck_name = "Languages::Italiano"
    model_name = "Language"
    tags = ["duolingo", "anker-migrated"]

    # Targets the Language model *after* the German->Translation and EE->Definition
    # field rename. If your model still has the old names, change the two
    # @field("Translation") / @field("Definition") decorators below back to
    # @field("German") / @field("EE").

    src_lang = "it"
    contact = None          # e-mail for the Wiktionary UA / MyMemory quota
    audio_field = "Audio"
    make_reverse = False    # user studies it -> de/en; no German -> Term card

    _field_Lang = "Italian"
    _field_Family = "Duolingo"

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._wik = Wiktionary(lang=self.src_lang, contact=self.contact)
        self._mm = MyMemory(email=self.contact)

    # -- per-input work -------------------------------------------------
    def prepare(self, inputs, **kwds):
        f = inputs["fields"] if isinstance(inputs, dict) else {"Front": inputs[0], "Back": inputs[1]}
        self.src_note_id = inputs.get("noteId") if isinstance(inputs, dict) else None
        self.term = re.sub(r"<[^>]+>", "", f.get("Front", "")).strip()
        self.english = re.sub(r"<[^>]+>", "", f.get("Back", "")).strip()
        self.lemma = strip_article(self.term)

        self._wik(self.lemma)
        self.pos = _POS_MAP.get(self._wik.part_of_speech(), "")
        self.ipa = self._wik.ipa()
        self.gender = self._wik.gender()
        self.defs = self._wik.definitions(3)
        self.native_audio = self._wik.pronunciation()
        self.german = self._mm.translate(self.term, self.src_lang, "de")

    # -- fields ------------------------------------------------------------
    @field
    def Term(self):
        return self.term

    @field
    def POS(self):
        return self.pos

    @field
    def Phonetics(self):
        return f"/{self.ipa.strip('/')}/" if self.ipa else ""

    @field("Translation")
    def _translation(self):
        parts = []
        if self.german:
            parts.append(f"<b>{self.german}</b>")
        if self.english:
            parts.append(f'<span class="dim">{self.english}</span>')
        return "<br>".join(parts)

    @field("Definition")
    def _definition(self):
        extra = [d for d in self.defs if d.lower() != self.english.lower()]
        return "; ".join(extra)

    @field
    def Extra(self):
        bits = []
        if self.gender:
            bits.append(f'<span class="gender">{self.gender}</span>')
        bits.append(
            f'<a href="https://en.wiktionary.org/wiki/{self.lemma}#Italian">wiktionary</a>'
        )
        return " · ".join(bits)

    @field
    def Audio(self):
        return self.native_audio or google_tts(self.lemma, self.src_lang)

    @field
    def Reverse(self):
        return "y" if self.make_reverse else ""
