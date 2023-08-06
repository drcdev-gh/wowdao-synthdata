# TODO: Make it look at a specific e-commerce webpage and extract the possible actions from there.
# Add those as input to the base prompt

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class Link:
    def __init__(self, text, url):
        self.text = text
        self.url = url

    def __repr__(self):
        return (str(self.text) + ": " + str(self.url))

def browse_url(url, query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    req = Request(url, headers=headers)
    response = urlopen(req)
    soup = BeautifulSoup(response, "lxml")

    #links = []

    #for link in soup.find_all("a"):
    #    link_text = link.get_text()
    #    link_url = urljoin(url, link.get("href"))  # Construct the full URL

    #    if link_text and link_url:  # Only include if both link text and URL are available
    #        links.append({"text": link_text, "url": link_url})

    #print(str(links))

browse_url("https://www.amazon.com/s?k=hiking+shoes&ref=nb_sb_noss", "buy hiking shoes")