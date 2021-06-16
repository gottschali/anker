import click

from .vocabulary import Vocabulary
import anker.connect as connect

# TODO API for
# - phonetic
# - examples ?
# - trivia
#
def autocomplete_deck(ctx, param, incomplete):
    return [d for d in connect.decks if d.starswith(incomplete)]

def autocomplete_model(ctx, param, incomplete):
    return [d for d in connect.models if d.starswith(incomplete)]

@click.command()
@click.argument("input", type=click.File('r'))
@click.argument("source", type=click.Path(exists=True))
@click.argument("deck", type=click.STRING, autocompletion=autocomplete_deck, default="Anker")
@click.argument("model", type=click.STRING, autocompletion=autocomplete_model, default="Basic")
@click.option("-l", "--language", default="en")
@click.option("-t", "--target", default="de")
def main(input, source, deck, model, language, target):
    for word in input:
        v = Vocabulary(word, source, language, target)
        print(v)
        print("POS: ", v.pos)
        print("STEM: ", v.stem)
        print("CONTEXT: ", v.context)
        print("TRANS_CONTEXT:", v.translate_context())
        print("TRANS_WORD:", v.translate_word())
        print("SYNONYMS", v.synonyms)
        print("ANTONYMS", v.antonyms)
        print("IMAGE", v.image)
        print("PHONETICS", v.phonetics)
        print("PRONUNCIATION", v.pronunciation)
        print("DEFINITIONS", v.definitions)
        print("=== Building Note === ")

        print(connect.buildNote(deck, model, v))
        print("=== Built Note === ")


if __name__ == "__main__":
    main()


