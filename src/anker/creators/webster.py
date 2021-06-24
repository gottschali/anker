#!/usr/bin/env python3D
import requests
import re
from bs4 import BeautifulSoup

# TODO abstract if self.soup

class Webster:
    ROOT = "https://dictionary.cambridge.org"
    BASE = ROOT + "/dictionary/english/"
    # Use a different user agent, because urllib (the requests backend) is getting blocked
    HEADERS = {'User-agent': 'Mozilla/5.0'}

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def __call__(self, word):
        self.soup = self.cook(word)

    def cook(self, recipe):
        response = self.session.get(self.BASE + recipe)
        soup = BeautifulSoup(response.content, "html.parser")
        if soup:
            return soup.find("article")

    def pronunciation(self):
        if self.soup:
            t = self.soup.find_all("source", src=lambda x: x and re.search(r"uk.*?mp3", x))
            if t:
                return self.ROOT + t[0]["src"]

    def phonetics(self):
        if self.soup:
            div = self.soup.find("span", class_="uk dpron-i")
            if div:
                return div.find("span", class_="ipa").get_text()

    def definitions(self):
        if self.soup:
            return [d.get_text() for d in self.soup.find_all("div", class_="def ddef_d db")]
