#!/usr/bin/env python3
"""Fetch existing Anki notes as card inputs, so anker can *migrate* a deck
instead of only building one from scratch.

Yields ``dict`` rows: ``{"noteId", "modelName", "tags", "fields"}`` where
``fields`` maps field name -> value. Configure with environment variables
(``anker``'s CLI cannot pass fetcher arguments):

    ANKER_SRC_QUERY   Anki search picking the notes to read
                      (default: 'deck:Languages::Italiano tag:duolingo')
    ANKER_SRC_LIMIT   optional cap on how many notes to yield

A card's ``prepare`` then reads what it needs, e.g. ``inputs["fields"]["Front"]``.
"""
import os
from anker.connect import invoke

DEFAULT_QUERY = "deck:Languages::Italiano tag:duolingo"


class Fetcher:
    def __init__(self, query=None, limit=None):
        self.query = query or os.environ.get("ANKER_SRC_QUERY", DEFAULT_QUERY)
        env_limit = os.environ.get("ANKER_SRC_LIMIT")
        self.limit = limit if limit is not None else (int(env_limit) if env_limit else None)

    def note_ids(self):
        ids = invoke("findNotes", query=self.query) or []
        return ids[: self.limit] if self.limit else ids

    def __iter__(self):
        ids = self.note_ids()
        # notesInfo is happy with a few thousand ids in one call
        for info in invoke("notesInfo", notes=ids) or []:
            yield {
                "noteId": info["noteId"],
                "modelName": info["modelName"],
                "tags": info.get("tags", []),
                "fields": {k: v["value"] for k, v in info["fields"].items()},
            }

    def __len__(self):
        return len(self.note_ids())
