#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from pathlib import Path

class ImageDownloader:
    BASE = "https://www.thefreedictionary.com/"
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
        return soup.find(id="MainTxt")

    def image(self):
        if self.soup:
            rel = self.soup.find("img")
            if rel:
                return "https:" + rel["src"]
