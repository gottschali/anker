#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from pathlib import Path

class ImageDownloader:
    BASE = "https://www.thefreedictionary.com/"
    DOWNLOAD_DIR = Path("./downloads")
    # Use a different user agent, because urllib (the requests backend) is getting blocked
    HEADERS = {'User-agent': 'Mozilla/5.0'}

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def __call__(self, word):
        soup = self.cook(word)
        if soup:
            image = self.find_image(soup)
            return image

    def cook(self, recipe):
        response = self.session.get(self.BASE + recipe)
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.find(id="MainTxt")

    @staticmethod
    def find_image(soup):
        rel = soup.find("img")
        if rel:
            return "https:" + rel["src"]

    def download(self, word, src):
        print(f"Downlaoding image for {word} from {src}")
        response = self.session.get(src, stream=True)
        path = (self.DOWNLOAD_DIR / Path(word + "." + src.split(".")[-1])).absolute()
        with open(path, "wb") as handle:
            for data in tqdm(response.iter_content()):
                handle.write(data)
        return path
