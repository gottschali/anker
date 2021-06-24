#!/usr/bin/env python3
import subprocess
from nltk import sent_tokenize

def context(word, source):
    """ Searches the path source for occurences of a word """
    args = ["rg", "--ignore-case", word, source]
    with subprocess.Popen(args, stdout=subprocess.PIPE) as p:
        output, error = p.communicate()
        if error:
            raise Exception(error)
        output = output.decode("utf-8")
        # Only take the first match if there are multiple
        match = output.split("\n")[0]
        sentences = sent_tokenize(match)
        for sentence in sentences:
            if word in sentence:
                return sentence
