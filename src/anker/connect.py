#!/usr/bin/env python3

import json
import requests

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

class AnkiConnectionError(Exception):
    pass

def invoke(action, **params):
    payload = json.dumps(request(action, **params)).encode('utf-8')
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
    except Exception as e:
        if isinstance(e, requests.exceptions.ConnectionError):
            raise AnkiConnectionError("Is the Anki running and the AnkiConnect addon installed and configured to run on ", url)
        else:
            # Probably duplicate
            print(e)

decks = invoke('deckNames')
models = invoke('modelNames')
fieldNames = lambda model: invoke('modelFieldNames', modelName=model)

def createNote(params):
    return invoke("addNote", **params)

