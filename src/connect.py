#!/usr/bin/env python3

import json
import requests

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
    payload = json.dumps(request(action, **params)).encode('utf-8')
    print(payload)
    url = 'http://localhost:8765'
    try:
        response = requests.get(url, data=payload)
        result = json.loads(response.content.decode("utf-8"))
        if len(result) != 2:
            raise Exception('response has an unexpected number of fields')
        if 'error' not in result:
            raise Exception('response is missing required error field')
        if 'result' not in result:
            raise Exception('response is missing required result field')
        if result['error'] is not None:
            raise Exception(result['error'])
        return result['result']
    except requests.exceptions.ConnectionError:
        raise Exception("Connnection Error: Is the Anki running and the AnkiConnect addon installed and configured to run on ", url)

def buildNote(vocab):
    params = {
        "note": {
            "deckName": "Test",
            "modelName": "English",
            "fields": {
                "English": vocab.word,
                "German": vocab.translate_word() or "",
                "POS": vocab.pos or "",
                "Example": vocab.context or "",
                "NotEnglish": ", ".join(vocab.synonyms) or "",
                "Extra": ", ".join(vocab.antonyms),
                "EE": "<ul>" + "".join("<li>" + v + "</li>" for v in vocab.definitions or ()) + "</ul>",
                "NotGerman": "",
                "Reverse": "y",
                "Family": "ANKER IMPORT",
                "Phonetics": vocab.phonetics or "",
                "Image": "",
                "Mnemonic": "",
                "Audio": "",
            },
            "options": {
                "allowDuplicate": True,
                "duplicateScope": "deckName",
            },
            "tags": [
                "english::anker"
            ],
        }
    }
    if vocab.pronunciation:
        params["note"]["audio"] = [{
            "url": vocab.pronunciation,
            "filename": vocab.word + ".mp3",
            "fields": [
                "Audio"
            ]
        }]
    if vocab.image:
        params["note"]["picture"] = [{
            "url": vocab.image,
            "filename": vocab.word + ".png",
            "fields": [
                "Image"
            ]
        }]

    return invoke("addNote", **params)
