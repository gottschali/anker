#!/usr/bin/env python3D
import requests
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
from pathlib import Path


class Webster:
    ROOT = "https://dictionary.cambridge.org"
    BASE = ROOT + "/dictionary/english/"
    DOWNLOAD_DIR = Path("./downloads")
    # Use a different user agent, because urllib (the requests backend) is getting blocked
    HEADERS = {'User-agent': 'Mozilla/5.0'}

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def __call__(self, word):
        soup = self.cook(word)
        if soup:
            pronunciation = self.find_pronunciation(soup)
            # pronunciation = self.download(word, pronunciation)
            ipa = self.find_phonetics(soup)
            defs = self.find_definitions(soup)
            return pronunciation, ipa, defs
        return None, None, None

    def cook(self, recipe):
        response = self.session.get(self.BASE + recipe)
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.find("article")

    def find_pronunciation(self, soup):
        t = soup.find_all("source", src=lambda x: x and re.search(r"uk.*?mp3", x))
        if t:
            return self.ROOT + t[0]["src"]

    @staticmethod
    def find_phonetics(soup):
        div = soup.find("span", class_="uk dpron-i")
        if div:
            return div.find("span", class_="ipa").get_text()

    @staticmethod
    def find_definitions(soup):
        return [d.get_text() for d in soup.find_all("div", class_="def ddef_d db")]

    def download(self, word, src):
        print(f"Downlaoding pronunciation {word} from {src}")
        response = self.session.get(src, stream=True)
        path = (self.DOWNLOAD_DIR / Path(word + ".mp3")).absolute()
        with open(path, "wb") as handle:
            for data in tqdm(response.iter_content()):
                handle.write(data)
        return path
