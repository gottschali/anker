#!/usr/bin/env python3
import subprocess
import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import wordnet
from googletrans import Translator

from .webster import Webster
from .image_downloader import ImageDownloader

class Vocabulary:
    translator = Translator()
    stemmer = PorterStemmer()
    webster = Webster()
    image_downloader = ImageDownloader()

    def __init__(self, word, source, language, target):
        self.word = word.strip()
        self.normalized = self.word.lower()
        self.source = source
        self.language = language
        self.target = target
        self.context = self.get_context(source)
        self.syno_and_antonyms()
        self.pronunciation, self.phonetics, self.definitions = self.webster(self.normalized)
        self.image = self.image_downloader(self.normalized)

    def __repr__(self):
        return f"Vocabulary({self.word}, {self.source})"

    def get_context(self, source):
        args = ["rg", "--ignore-case", self.normalized, source]
        with subprocess.Popen(args, stdout=subprocess.PIPE) as p:
            output, error = p.communicate()
            if error:
                raise Exception(error)
            output = output.decode("utf-8")
            # Only take the first match if there are multiple
            match = output.split("\n")[0]
            sentences = nltk.sent_tokenize(match)
            for sentence in sentences:
                if self.normalized in sentence:
                    self.context = sentence
                    return self.markup(sentence)

    def markup(self, sentence):
        i = sentence.index(self.normalized)
        n = len(self.normalized)
        return sentence[:i] + f"<i class={self.pos}>" + self.normalized + "</i>" + sentence[i+n:]

    def syno_and_antonyms(self):
        self.synonyms = []
        self.antonyms = []
        for syn in wordnet.synsets(self.normalized):
	        for l in syn.lemmas():
		        self.synonyms.append(l.name())
		        if l.antonyms():
			        self.antonyms.append(l.antonyms()[0].name())


    @property
    def stem(self):
        return self.stemmer.stem(self.normalized)

    def translate_context(self):
        if self.context:
            translation = self.translator.translate(self.context, src=self.language, dest=self.target)
            return translation.text

    def translate_word(self):
        translation = self.translator.translate(self.normalized, src=self.language, dest=self.target)
        return translation.text


    @property
    def pos(self):
        if self.context:
            tokens = nltk.word_tokenize(self.context)
            tagged = nltk.pos_tag(tokens)
            try:
                _, tag = tagged[tokens.index(self.normalized)]
            except ValueError:
                print("WARNING: No exact match found! ", tokens, self.normalized, self.word)
                for i, t in enumerate(tokens):
                    if self.normalized in t:
                        _, tag = tagged[i]
                        break

            # Map the POS to simpler ones
            if tag.startswith('RB'):
                return "adv"
            elif tag.startswith('JJ'):
                return "adj"
            elif tag.startswith('NN'):
                return "n"
            elif tag.startswith('VB'):
                return "v"
            elif tag.startswith("JJ") or tag.startswith("IN"):
                return "conj"
