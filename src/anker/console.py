import click
from pprint import pprint
from click.shell_completion import CompletionItem
from typing import Iterable
from tabulate import tabulate
import importlib
import csv
import sys
from pathlib import Path

import anker.connect as connect

def find_plugins(plugin: str):
    """ Imports all class named Plugin from the folder anker/plugin """
    result = {}
    for f in Path("src/anker/" + plugin).iterdir():
        try:
            name = f.stem
            module = importlib.import_module(f"anker.{plugin}.{name}")
            result[name] = module.__dict__[plugin.capitalize()]
        except Exception as e:
            pass
    return result

models = find_plugins("card")
fetchers = find_plugins("fetcher")

# Autocompletion does not work when you print something to stdout
def autocomplete(iterable: Iterable[str]):
    """ Returns a click autocomplete function """
    def _autocomplete(ctx, param, incomplete):
        return [i for i in iterable if i.startswith(incomplete)]
    return _autocomplete

@click.command()
@click.option("-c", "--card", autocompletion=autocomplete(models.keys()), required=True, help="The card model to script the cards.")
@click.option("-f", "--fetcher", autocompletion=autocomplete(fetchers.keys()), help="The fetcher that generates inputs for the cards")
@click.option("-v", "--verbose", is_flag=True, help="Print more")
@click.option("-i", "--input", is_flag=True, help="Use stdin as the input fetcher")
@click.option("-o", "--output", type=click.File(mode='w'), default=sys.stdout, help="Write a csv to this file that could be imported manually into anki")
@click.option("-p", "--push", is_flag=True, help="Push the cards directly to Anki via ankiconnect")
def main(card, fetcher, verbose, input, output, push):

    """ ANKER
    Enable autocompletion for bash:
    eval "$(_ANKER_COMPLETE=bash_source anker)"

    or for zsh:
    eval "$(_ANKER_COMPLETE=zsh_source anker)"

    Create cards models in anker/cards/ as classes that inherit from anker.meta.MetaCard
    """

    card_writer = csv.writer(output, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    card = models[card]()
    if input:
        fetcher = "stdin"
    fetcher = fetchers[fetcher]
    input = fetcher() if hasattr(fetcher, "__call__") else fetcher

    options = {
        "allowDuplicate": False,
                "duplicateScope": "deckName",
        }
    for i in input:
        fields, params = card(i, options=options)
        if output:
            card_writer.writerow(v for _, v in fields)
        if verbose:
            click.echo(tabulate(fields, tablefmt="fancy_grid"))
        if push:
            print("Creating Note")
            print(connect.createNote(params))


if __name__ == "__main__":
    main()


