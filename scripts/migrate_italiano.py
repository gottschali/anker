#!/usr/bin/env python3
"""Resumable, rate-limited migration of the Duolingo ``Languages::Italiano`` deck
into the ``Language`` note type.

    python scripts/migrate_italiano.py --dry-run --limit 25   # preview -> out/*.jsonl
    python scripts/migrate_italiano.py --limit 100            # migrate first 100
    python scripts/migrate_italiano.py                        # migrate the rest

For every source note it:
  1. builds a ``Language`` note via anker's ``italian_vocab`` card (Wiktionary +
     MyMemory + Google TTS enrichment),
  2. ``addNote``s it (skipping ones already migrated, tracked in the state file),
  3. tags the source note ``migrated-to-language`` and suspends its cards
     (``--no-suspend`` to skip) -- nothing is deleted; a later pass trashes the
     originals once you've spot-checked.

State + a full JSONL action log live under ``out/`` so re-runs are idempotent.
"""
import argparse
import json
import pathlib
import sys
import time
import urllib.request

SRC_QUERY = "deck:Languages::Italiano tag:duolingo -note:Language -tag:migrated-to-language"
OUT = pathlib.Path(__file__).resolve().parent.parent / "out"
STATE = OUT / "italiano_state.json"
LOG = OUT / "italiano_migration.jsonl"
ANKI = "http://127.0.0.1:8765"


def invoke(action, **params):
    req = urllib.request.Request(
        ANKI, json.dumps({"action": action, "version": 6, "params": params}).encode(),
        {"Content-Type": "application/json"},
    )
    r = json.load(urllib.request.urlopen(req))
    if r.get("error"):
        raise RuntimeError(f"{action}: {r['error']}")
    return r["result"]


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"done": {}}          # srcNoteId -> newNoteId (or null if failed)


def save_state(s):
    OUT.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(s, indent=1))


def log(entry):
    OUT.mkdir(exist_ok=True)
    with LOG.open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--no-suspend", action="store_true")
    ap.add_argument("--sleep", type=float, default=1.0, help="pause between notes (s)")
    ap.add_argument("--contact", default="aligottschall22@gmail.com")
    args = ap.parse_args()

    sys.path.insert(0, str(OUT.parent / "src"))
    from anker.card.italian_vocab import Card

    Card.contact = args.contact
    card = Card()

    state = load_state()
    ids = invoke("findNotes", query=SRC_QUERY)
    todo = [i for i in ids if str(i) not in state["done"]]
    if args.limit:
        todo = todo[: args.limit]
    print(f"{len(ids)} match query, {len(todo)} to process this run "
          f"({'DRY RUN' if args.dry_run else 'LIVE'})")

    infos = {n["noteId"]: n for n in invoke("notesInfo", notes=todo)}
    ok = fail = 0
    for k, nid in enumerate(todo, 1):
        info = infos[nid]
        row = {
            "noteId": nid,
            "modelName": info["modelName"],
            "tags": info.get("tags", []),
            "fields": {f: v["value"] for f, v in info["fields"].items()},
        }
        try:
            fields, params = card(row, options={"allowDuplicate": False,
                                                "duplicateScope": "deckName"})
            fields = dict(fields)
        except Exception as e:
            fail += 1
            log({"src": nid, "error": f"build: {e}"})
            print(f"  [{k}/{len(todo)}] {row['fields'].get('Front','?')!r}  BUILD ERROR {e}")
            continue

        preview = {kk: vv for kk, vv in fields.items() if vv}
        print(f"  [{k}/{len(todo)}] {row['fields'].get('Front','?')!r:24} -> "
              f"{preview.get('Translation','')[:48]!r}  pos={preview.get('POS','')} "
              f"ipa={preview.get('Phonetics','')}")

        if args.dry_run:
            log({"src": nid, "dry_run": True, "fields": fields})
            ok += 1
            time.sleep(args.sleep)
            continue

        try:
            new_id = invoke("addNote", note=params["note"])
        except RuntimeError as e:
            fail += 1
            state["done"][str(nid)] = None
            log({"src": nid, "error": f"addNote: {e}", "fields": fields})
            print(f"        addNote failed: {e}")
            time.sleep(args.sleep)
            continue

        invoke("addTags", notes=[nid], tags="migrated-to-language")
        if not args.no_suspend:
            invoke("suspend", cards=info["cards"])
        state["done"][str(nid)] = new_id
        log({"src": nid, "new": new_id, "fields": fields,
             "suspended_src_cards": [] if args.no_suspend else info["cards"]})
        save_state(state)
        ok += 1
        time.sleep(args.sleep)

    if not args.dry_run:
        save_state(state)
    print(f"\ndone: {ok} ok, {fail} failed. log -> {LOG}")


if __name__ == "__main__":
    main()
