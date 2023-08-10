from enum import Enum
import enum
import uuid
import json
import sqlite3
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

class UserProfile:
    def __init__(self, gender, age_from, age_to, location, interests, description=None):
        self.id = uuid.uuid1()
        self.gender     = gender
        self.age_from   = age_from
        self.age_to     = age_to
        self.location   = location
        self.interests   = interests
        self.description = description

    def persist(self):
        conn = sqlite3.connect("storage.db")
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id TEXT PRIMARY KEY,
                gender TEXT,
                age_from INTEGER,
                age_to INTEGER,
                location TEXT,
                interests TEXT,
                description TEXT
        )
        ''')

        interests_str = ', '.join(self.interests)
        c.execute('''
            INSERT INTO user_profiles (id, gender, age_from, age_to, location, interests, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(self.id), self.gender, self.age_from, self.age_to, self.location, interests_str, self.description
        ))
        conn.commit()

    def __str__(self):
        return f'Gender: {self.gender} | Age: {self.age_from}-{self.age_to} | Location: {self.location} | Interest: {self.interests} | Description: {self.description}'

class PageType(Enum):
    SEARCH_RESULTS  = enum.auto()
    PRODUCT_DETAILS = enum.auto()

class ActionType(Enum):
    QUERY_GOAL                = enum.auto()
    BACK_TO_SEARCH_RESULTS    = enum.auto()
    CLICK_SEARCH_RESULT       = enum.auto()
    CLICK_RECOMMENDED         = enum.auto()
    BUY_NOW                   = enum.auto()

class Action:
    def __init__(self, action_type, context, target_url):
        self.action_id   = uuid.uuid1()
        self.action_type = action_type
        self.context     = context
        self.target_url  = target_url

    def to_json(self):
        return json.dumps({
            'action_id': str(self.action_id),
            'action_type': self.action_type.name,
            'context': self.context,
        }, indent=4)

    def array_to_json(array):
        options = ""
        for action in array:
            options += action.to_json() + "\n"

        return options

    def __str__(self):
        return self.to_json()

class Scraper:
    def __init__(self, scraper_name):
        self.scraper_name = scraper_name

        # Connect to the database (it will be created if not exist)
        conn = sqlite3.connect('webpages.db')
        c = conn.cursor()

        # Create a table to store cached webpages
        c.execute('''
            CREATE TABLE IF NOT EXISTS webpages (
                url TEXT PRIMARY KEY,
                content BLOB
            )
        ''')

        conn.commit()
        conn.close()

    def get_initial_actions(self, goal):
        return []

    def scrape_page_into_possible_actions(self, page):
        return []

    def scrape_and_cache(self, url):
        # Check if the URL is already cached
        conn = sqlite3.connect('webpages.db')
        c = conn.cursor()
        c.execute('SELECT content FROM webpages WHERE url=?', (url,))
        cached_data = c.fetchone()
        conn.close()

        if cached_data:
            return cached_data[0]

        # If not cached, scrape the webpage
        headers = {
            'User-Agent': UserAgent().random,
            'Accept-Language': 'en-US,en;q=0.9'
        }
        req      = Request(url, headers=headers)
        response = urlopen(req)
        if response:
            response_content = response.read()

            # Cache the scraped webpage
            conn = sqlite3.connect('webpages.db')
            c = conn.cursor()
            c.execute('INSERT INTO webpages (url, content) VALUES (?, ?)', (url, response_content))
            conn.commit()
            conn.close()

            return response_content

        return None

class AmazonScraper(Scraper):
    def __init__(self):
        super().__init__("Amazon")
        self.search_url = None

    def get_initial_actions(self, goal):
        self.search_url = self.generate_amazon_search_url(goal)
        return [Action(ActionType.QUERY_GOAL, goal, self.search_url)]

    def determine_page_type(self, page):
        if page.startswith("https://www.amazon.com/s?k"):
            return PageType.SEARCH_RESULTS
        return PageType.PRODUCT_DETAILS

    def scrape_page_into_possible_actions(self, page):
        actions = []
        page_type = self.determine_page_type(page)
        if page_type is PageType.SEARCH_RESULTS:
            actions.extend(self.extract_products_from_search_page(page))
        elif page_type is PageType.PRODUCT_DETAILS:
            actions.extend(self.extract_recommendations_from_product_details(page))
            actions.extend(self.extract_checkout_from_product_details(page))
            actions.append(Action(ActionType.BACK_TO_SEARCH_RESULTS, "Go back to search results", self.search_url))
        return actions

    def extract_products_from_search_page(self, page):
        LIMIT = 5
        products = []
        content  = self.scrape_and_cache(page)

        soup = BeautifulSoup(content, "lxml")
        search_results = soup.find_all(attrs={"data-component-type": "s-search-result"})
        for _, result in enumerate(search_results, start=1):
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
            product_description = None
            if escaped_text is not None and full_url is not None:
                product_description = self.add_to_str(product_description, "Product Title", escaped_text)
                product_description = self.add_to_str(product_description, "Price", price)
                product_description = self.add_to_str(product_description, "Bestseller Status", bestseller_status)
                product_description = self.add_to_str(product_description, "Star Rating", star_rating)
                product_description = self.add_to_str(product_description, "List Price", list_price)

                product = Action(ActionType.CLICK_SEARCH_RESULT, product_description, full_url)
                products.append(product)
                if len(products) >= LIMIT:
                    break

        return products

    def add_to_str(self, str, key, item):
        if item is not None:
            if str is None:
                str = key + ": " + item

            str += "; " + key + ": " + item

        return str

    def extract_recommendations_from_product_details(self, page):
        LIMIT = 5

        content  = self.scrape_and_cache(page)
        soup     = BeautifulSoup(content, "lxml")

        recommendations = []
        product_elements = soup.find_all('li', class_='a-carousel-card')

        for product_element in product_elements:
            try:
                product_title = product_element.find('a', class_='a-link-normal')['title']
                product_url = product_element.find('a', class_='a-link-normal')['href']
                full_url = "https://amazon.com" + product_url
                product_price = product_element.find('span', class_='a-size-medium').text

                product_description = None

                if product_title is not None and product_url is not None:
                    product_description = self.add_to_str(product_description, "Product Title", product_title)
                    product_description = self.add_to_str(product_description, "Product Price", product_price)
                    recommendations.append(Action(ActionType.CLICK_RECOMMENDED, product_description, full_url))
                    if len(recommendations) >= LIMIT:
                        break
            except:
                continue

        return recommendations

    def extract_checkout_from_product_details(self, page):
        content  = self.scrape_and_cache(page)
        soup     = BeautifulSoup(content, "lxml")

        product_description = ""

        feature_bullets_div = soup.find("div", id="feature-bullets")

        # Find the span element with id "productTitle"
        product_title_span = soup.find("span", id="productTitle")

        if product_title_span:
            escaped_title = product_title_span.get_text(strip=True)
            product_description = self.add_to_str(product_description, "Product Title", escaped_title)

        # Extract the bullet points
        if feature_bullets_div:
            bullet_points = feature_bullets_div.find_all("span", class_="a-list-item")

            # TODO: make sure this is working also if there's no bullet points
            bullet_points = ""
            for bullet_point in bullet_points:
                if bullet_point.get_text() != "":
                    bullet_points += bullet_point.get_text() + "; "
            product_description = self.add_to_str(product_description, "Product Description", bullet_points)

        # Find the span elements with class "a-price-range"
        price_range_spans = soup.find_all("span", class_="a-price-range")

        for price_range_span in price_range_spans:
            # Extract the price from each span
            price_elements = price_range_span.find_all("span", class_="a-price")
            for price_element in price_elements:
                price = price_element.find("span", class_="a-offscreen").get_text()
                product_description = self.add_to_str(product_description, "Price", price)

        # Find the span element with class "reviewCountTextLinkedHistogram"
        average_review_span = soup.find("span", class_="reviewCountTextLinkedHistogram")

        if average_review_span:
            title = average_review_span.get("title")
            average_review = title.split(" ")[0] if title else None
            product_description = self.add_to_str(product_description, "Average Review", average_review)

        # Find the span element with id "acrCustomerReviewText"
        ratings_span = soup.find("span", id="acrCustomerReviewText")

        if ratings_span:
            num_ratings = ratings_span.get_text().replace(" ratings", "").replace(",", "")
            product_description = self.add_to_str(product_description, "Number Ratings", num_ratings)

        return [Action(ActionType.BUY_NOW, product_description, None)]

    def generate_amazon_search_url(self, search_query):
        base_url = "https://www.amazon.com/s"
        query_params = {'k': search_query.replace(' ', '+')}  # Replace spaces with '+'
        encoded_params = '&'.join([f"{key}={value}" for key, value in query_params.items()])
        amazon_search_url = f"{base_url}?{encoded_params}"
        return amazon_search_url


class AgentStatus(Enum):
    NOT_STARTED = enum.auto()
    IN_PROGRESS = enum.auto()
    FINISHED    = enum.auto()


class Agent:
    def __init__(self, agent_id, name, user_profile):
        self.id = agent_id
        self.name = name
        self.user_profile = user_profile

    def persist(self):
        conn = sqlite3.connect("storage.db")
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT,
                user_profile_id TEXT,
                FOREIGN KEY (user_profile_id) REFERENCES user_profiles (id)
            )
        ''')

        c.execute('''
            INSERT INTO agents (id, name, user_profile_id)
            VALUES (?, ?, ?)
        ''', (
            str(self.id), self.name, str(self.user_profile.id)
        ))
        conn.commit()
