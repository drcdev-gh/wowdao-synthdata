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

def browse_search_url(url, query, save_filename):
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
    for index, result in enumerate(search_results, start=1):
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

def browse_product_url(url, query, save_filename):
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

    feature_bullets_div = soup.find("div", id="feature-bullets")

    # Find the span element with id "productTitle"
    product_title_span = soup.find("span", id="productTitle")

    if product_title_span:
        escaped_title = product_title_span.get_text(strip=True)
        print("Escaped Product Title:", escaped_title)
    else:
        print("Product title not found.")

    # Extract the bullet points
    if feature_bullets_div:
        bullet_points = feature_bullets_div.find_all("span", class_="a-list-item")

        for bullet_point in bullet_points:
            print(bullet_point.get_text())

    # Find the span elements with class "a-price-range"
    price_range_spans = soup.find_all("span", class_="a-price-range")

    for price_range_span in price_range_spans:
        # Extract the price from each span
        price_elements = price_range_span.find_all("span", class_="a-price")
        for price_element in price_elements:
            price = price_element.find("span", class_="a-offscreen").get_text()
            print("Price:", price)

    # Find the span element with class "reviewCountTextLinkedHistogram"
    average_review_span = soup.find("span", class_="reviewCountTextLinkedHistogram")

    if average_review_span:
        title = average_review_span.get("title")
        average_review = title.split(" ")[0] if title else None
        print("Average Review:", average_review)
    else:
        print("Average review not found.")

    # Find the span element with id "acrCustomerReviewText"
    ratings_span = soup.find("span", id="acrCustomerReviewText")

    if ratings_span:
        num_ratings = ratings_span.get_text().replace(" ratings", "").replace(",", "")
        print("Number of Customer Ratings:", num_ratings)
    else:
        print("Number of customer ratings not found.")

    product_elements = soup.find_all('li', class_='a-carousel-card')

    for product_element in product_elements:
        product_title = product_element.find('a', class_='a-link-normal')['title']
        product_url = product_element.find('a', class_='a-link-normal')['href']
        full_url = "https://amazon.com" + product_url
        product_price = product_element.find('span', class_='a-size-medium').text

        print("Product Title:", product_title)
        print("Product URL:", full_url)
        print("Product Price:", product_price)
        print()

#browse_search_url("https://www.amazon.com/s?k=hiking+shoes&crid=2656PWPB66Y05&sprefix=hiking+shoes%2Caps%2C289&ref=nb_sb_noss_1", "buy hiking shoes", "data.pkl")
browse_product_url("https://www.amazon.com/Merrell-Mens-Moab-Hiking-Walnut/dp/B098KH1P14/ref=sr_1_4?crid=1A3PW70CV50M5&keywords=hiking+shoes&qid=1691476527&sprefix=hiking+shoe%2Caps%2C202&sr=8-4", "buy hiking shoes", "data2.pkl")