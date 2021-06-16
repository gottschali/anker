import click

from vocabulary import Vocabulary
from connect import buildNote

# TODO API for
# - phonetic
# - examples ?
# - trivia

@click.command()
@click.argument("input", type=click.File('r'))
@click.argument("source", type=click.Path(exists=True))
@click.option("-l", "--language", default="en")
@click.option("-t", "--target", default="de")
def main(input, source, language, target):
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
        print(buildNote(v))
        print("=== Built Note === ")


if __name__ == "__main__":
    main()


