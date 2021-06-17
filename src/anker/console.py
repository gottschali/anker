import click
import sys
from click.shell_completion import CompletionItem
from typing import Iterable
from googletrans import LANGUAGES

from .vocabulary import Vocabulary
import anker.connect as connect

# TODO csv output
# TODO Configure a function for each field
# Limitations: bilingual

class ModelFieldsException(Exception):
    pass

def autocomplete(iterable: Iterable[str]):
    """ Returns a click autocomplete function """
    def _autocomplete(ctx, param, incomplete):
        return [i for i in iterable if i.startswith(incomplete)]
    return _autocomplete

def autocomplete_language(ctx, param, incomplete):
    return [CompletionItem(language, help=code)
            for code, language in LANGUAGES.items() if language.startswith(incomplete)]

language_help = "Use a language code as used by google translate or type out the name in english. Tab completion helps you"


field_generators = ["word", "word_translation", "pos", "context", "synonyms", "antonyms", "description", "", "y"
          "ANKER_IMPORT", "phonetics", "", "", ""]

@click.command()
@click.option("-i", "--input", type=click.File(mode='r'), default=sys.stdin, help="File to read the words from")
@click.option("-c" "--context", type=click.Path(exists=True), help="Path to search for context. Can be a file or directory")
@click.option("-d", "--deck", type=click.STRING, autocompletion=autocomplete(connect.decks), default="Anker",
              help="The deck the cards shall be created in")
@click.option("-m", "--model", type=click.STRING, autocompletion=autocomplete(connect.models), default="Basic",
              help="The note model the cards shall use")
@click.option("-s", "--source", autocompletion=autocomplete_language, default="en",
              help="The source language of the word. " + language_help)
@click.option("-t", "--target",  autocompletion=autocomplete_language, default="de",
              help="Translate to this language. " + language_help)
@click.option("-g", "--generators",  n=-1, default=field_generators,
              help="For each field the note type has specify a function that generates the content")
def main(input, context, deck, model, language, target, generators):
    """ ANKER

    Takes a list of words as inputs and will automatically create anki cards for them to learn vocabulary.
    The notes will be pushed directly to anki with the anki connect plugin.

    Enable autocompletion for bash:
    eval "$(_ANKER_COMPLETE=bash_source anker)"

    or for zsh:
    eval "$(_ANKER_COMPLETE=zsh_source anker)"

    - If provided a book can be searched for context of the word.

    - Translation of the word and the context

    - Part of speech

    - Dictionary definitions

    - Phonetic

    - Audio pronunciation

    - Symbolic Image

    - Synonyms and Antonyms

    """
    # Translate to short code if necessary
    language = LANGUAGES[language] if language in LANGUAGES else language

    fields = connect.fields(model)
    if len(fields) != len(generators):
        raise ModelFieldsException(f"The generators you specified: {generators} does not match the fields ({fields}) of the Notetype {model}")

    for field, generator in zip(fields, generators):
        print(field, generator)

    for word in input:
        v = Vocabulary(word, context, language, target)

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


