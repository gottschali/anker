#!/usr/bin/env python3
"""Pronunciation audio via Google Translate's public ``translate_tts`` endpoint.

Returns a URL string. ``MetaCard.__build`` turns a field named by ``audio_field``
into an AnkiConnect media object, so a card only has to expose this URL:

    audio_field = "Audio"

    @field
    def Audio(self):
        return google_tts(self.term, "it")

The endpoint caps each request at ~200 characters and is best-effort: it will
rate-limit under heavy bulk use, so callers should space requests out and be
ready to retry / skip.
"""
import urllib.parse

_BASE = "https://translate.google.com/translate_tts"


def google_tts(text, lang="en"):
    if not text:
        return ""
    text = text.strip()[:200]
    q = urllib.parse.urlencode(
        {"ie": "UTF-8", "client": "tw-ob", "tl": lang, "q": text}
    )
    return f"{_BASE}?{q}"


class GoogleTTS:
    def __init__(self, lang="en"):
        self.lang = lang

    def __call__(self, text, lang=None):
        return google_tts(text, lang or self.lang)
