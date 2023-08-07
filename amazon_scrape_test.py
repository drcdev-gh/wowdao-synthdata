from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pickle
import os

def save_content_to_file(content, filename):
    with open(filename, 'wb') as file:
        file.write(content)

def load_content_from_file(filename):
    with open(filename, 'rb') as file:
        return file.read()

def browse_url(url, query, save_filename):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
    }

    if os.path.exists(save_filename):
        response_content = load_content_from_file(save_filename)
    else:
        req = Request(url, headers=headers)
        response = urlopen(req)
        response_content = response.read()
        save_content_to_file(response_content, save_filename)

    soup = BeautifulSoup(response_content, "lxml")
    search_results = soup.find_all(attrs={"data-component-type": "s-search-result"})
    for result in search_results:
        # Extract HREF URL
        href_element = result.find("a", class_="a-link-normal")
        if href_element:
            href_url = href_element['href']
            full_url = "https://amazon.com" + href_url
        else:
            full_url = None
        
        # Extract escaped text (title)
        title_element = result.find("span", class_="a-size-base-plus")
        escaped_text = title_element.get_text() if title_element else None

        # Extract price
        price_element = result.find("span", class_="a-offscreen")
        price = price_element.get_text() if price_element else None

        # Extract list price
        list_price_element = result.find("span", class_="a-price a-text-price")
        list_price = list_price_element.find("span", class_="a-offscreen").get_text() if list_price_element else None

        # Extract bestseller status
        bestseller_element = result.find("span", class_="a-badge-label")
        bestseller_status = bestseller_element.get_text() if bestseller_element else "Not a Bestseller"

        # Extract star rating
        star_rating_element = result.find("i", class_="a-icon-star-small")
        star_rating = star_rating_element.find("span", class_="a-icon-alt").get_text() if star_rating_element else None

        # Print or store the extracted information
        print("HREF URL:", full_url)
        print("Escaped Text:", escaped_text)
        print("Price:", price)
        print("List Price:", list_price)
        print("Bestseller Status:", bestseller_status)
        print("Star Rating:", star_rating)
        print("\n")

    return soup

browse_url("https://www.amazon.com/s?k=hiking+shoes&crid=2656PWPB66Y05&sprefix=hiking+shoes%2Caps%2C289&ref=nb_sb_noss_1", "buy hiking shoes", "data.pkl")