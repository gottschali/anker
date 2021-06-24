#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup


class Fetcher:
    # Use a different user agent, because urllib (the requests backend) is getting blocked
    DOMAIN = "https://www.theidioms.com"

    def __init__(self):
        self.session = requests.Session()
        HEADERS = {'User-agent': 'Mozilla/5.0'}
        self.session.headers.update(HEADERS)

    def iter_pages(self):
        PATH = self.DOMAIN + "/list/page/"
        for i in range(1, 149):
            URL = PATH + str(i)
            response = self.session.get(URL)
            yield BeautifulSoup(response.content, "html.parser")

    def __iter__(self):
        for page in self.iter_pages():
            yield from self.consume_soup(page)

    def consume_soup(self, soup):
        block = soup.find("div", class_="blocks main-block")
        dl = block.find("dl")
        for dt, dd in zip(dl.findAll("dt"), dl.findAll("dd")):
            idiom = dt.text
            meaning, *example = dd.findAll("p")
            if example:
                example = example[0]
                example = example.text.lstrip("Example: ").rstrip("Read on")
            else:
                example = ""
            meaning = meaning.text.lstrip("Meaning: ")
            yield idiom, meaning, example


if __name__ == "__main__":
    i = Idioms()
