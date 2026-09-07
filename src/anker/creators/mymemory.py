#!/usr/bin/env python3
"""Translate via the MyMemory API (https://mymemory.translated.net/doc/spec.php).

A maintained, key-less replacement for the ``googletrans`` creator, which broke
against Google's endpoints. Anonymous use is limited to ~5000 chars/day; passing
``email`` raises that to ~50000/day. Results carry a ``match`` score in [0, 1];
low scores usually mean the phrase was assembled from segments.
"""
import time
import requests

_ENDPOINT = "https://api.mymemory.translated.net/get"


class MyMemory:
    def __init__(self, email=None, min_interval=0.5, session=None):
        self.email = email
        self.min_interval = min_interval
        self.session = session or requests.Session()
        self._last = 0.0

    def _throttle(self):
        wait = self.min_interval - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        self._last = time.monotonic()

    def translate(self, text, src, dest):
        """Return the best translation of ``text`` from ``src`` to ``dest``
        (ISO-639-1 codes, e.g. ``it`` -> ``de``), or ``""`` on failure."""
        if not text:
            return ""
        self._throttle()
        params = {"q": text, "langpair": f"{src}|{dest}"}
        if self.email:
            params["de"] = self.email
        try:
            r = self.session.get(_ENDPOINT, params=params, timeout=20)
            data = r.json()
        except Exception:
            return ""
        rd = data.get("responseData") or {}
        best = (rd.get("translatedText") or "").strip()
        # MyMemory echoes an ALL-CAPS error string in translatedText on quota etc.
        if not best or best.upper().startswith(("MYMEMORY WARNING", "QUERY LENGTH LIMIT")):
            return ""
        return best

    def __call__(self, text, src, dest):
        return self.translate(text, src, dest)
