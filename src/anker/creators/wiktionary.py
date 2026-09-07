#!/usr/bin/env python3
"""Scrape a single language section of an English-Wiktionary entry.

Unlike :mod:`anker.creators.webster` (Cambridge, English only) this works for any
language that has entries on en.wiktionary.org. It combines two endpoints:

* the REST ``/page/definition/`` summary -> part of speech + glosses
* the ``action=parse`` HTML -> IPA transcription and a pronunciation audio URL,
  scoped to the requested language's ``<h2>`` section so a shared spelling in
  another language is not picked up by mistake.

Everything is best effort; missing pieces come back as ``""`` / ``None``.
"""
import re
import requests
from bs4 import BeautifulSoup

_REST = "https://en.wiktionary.org/api/rest_v1/page/definition/"
_PARSE = "https://en.wiktionary.org/w/api.php"
_LANG_NAMES = {
    "it": "Italian", "de": "German", "fr": "French", "es": "Spanish",
    "en": "English", "pt": "Portuguese", "nl": "Dutch", "sl": "Slovene",
    "la": "Latin",
}


class Wiktionary:
    def __init__(self, lang="it", contact=None, session=None):
        self.lang = lang
        self.lang_name = _LANG_NAMES.get(lang, lang.title())
        self.session = session or requests.Session()
        self.session.headers.update(
            {"User-agent": f"anker/0.1 Wiktionary creator ({contact or 'anonymous'})"}
        )
        self.word = None
        self._defs = None
        self._section = None

    # -- fetch -------------------------------------------------------------
    def __call__(self, word):
        self.word = word
        self._defs = self._fetch_defs(word)
        self._section = self._fetch_section(word)
        return self

    def _fetch_defs(self, word):
        try:
            r = self.session.get(_REST + requests.utils.quote(word, safe=""), timeout=20)
            return r.json().get(self.lang) or []
        except Exception:
            return []

    def _fetch_section(self, word):
        try:
            r = self.session.get(_PARSE, timeout=20, params={
                "action": "parse", "page": word, "prop": "text",
                "format": "json", "formatversion": "2",
            })
            html = r.json()["parse"]["text"]
        except Exception:
            return None
        soup = BeautifulSoup(html, "html.parser")
        heading = None
        for h2 in soup.select("h2"):
            if h2.get("id") == self.lang_name or h2.get_text(strip=True) == self.lang_name:
                heading = h2.find_parent(class_="mw-heading") or h2
                break
        if heading is None:
            return None
        frag = BeautifulSoup("<div></div>", "html.parser")
        holder = frag.div
        for sib in heading.next_siblings:
            name = getattr(sib, "name", None)
            if name and ("mw-heading2" in (sib.get("class") or []) or name == "h2"):
                break
            holder.append(sib.extract() if hasattr(sib, "extract") else sib)
        return holder

    # -- fields ----------------------------------------------------------
    def part_of_speech(self):
        if self._defs:
            return (self._defs[0].get("partOfSpeech") or "").strip()
        return ""

    def definitions(self, limit=3):
        out = []
        for block in self._defs or []:
            for d in block.get("definitions", []):
                text = re.sub("<[^>]+>", "", d.get("definition", "")).strip()
                if text:
                    out.append(text)
        return out[:limit]

    def ipa(self):
        if not self._section:
            return ""
        node = self._section.select_one(".IPA")
        return node.get_text(strip=True) if node else ""

    def pronunciation(self):
        """URL of a pronunciation clip (mp3/ogg/wav) or ``""``."""
        if not self._section:
            return ""
        src = self._section.select_one("audio source")
        if not src or not src.get("src"):
            return ""
        url = src["src"].split("?")[0]
        return "https:" + url if url.startswith("//") else url

    def gender(self):
        """``m`` / ``f`` / ``mf`` for nouns, from the headword line."""
        if not self._section:
            return ""
        tags = [g.get_text(strip=True) for g in self._section.select(".headword-line .gender")]
        tags = [t for t in tags if t in ("m", "f", "mf", "m or f")]
        if not tags:
            return ""
        return "mf" if {"m", "f"} <= set(tags) or tags[0] in ("mf", "m or f") else tags[0]
