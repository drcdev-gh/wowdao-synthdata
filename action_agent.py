from langchain import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from enum import Enum
import uuid
import json
import sqlite3
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

class UserProfile:
    def __init__(self, gender, age_from, age_to, location, interest):
        self.gender     = gender
        self.age_from   = age_from
        self.age_to     = age_to
        self.location   = location
        self.interest   = interest

class PageType(Enum):
    SEARCH_RESULTS  = 1
    PRODUCT_DETAILS = 2

class ActionType(Enum):
    QUERY_GOAL        = 1
    CLICK_RESULT      = 2
    CLICK_RECOMMENDED = 3
    CHECKOUT          = 4

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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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

    def get_initial_actions(self, goal):
        return [Action(ActionType.QUERY_GOAL, goal, self.generate_amazon_search_url(goal))]

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

        return actions

    def extract_products_from_search_page(self, page):
        products = []
        content  = self.scrape_and_cache(page)

        soup = BeautifulSoup(content, "lxml")
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
            product_description = None
            if escaped_text is not None and full_url is not None:
                product_description = self.add_to_str(product_description, "Product Title", escaped_text)
                product_description = self.add_to_str(product_description, "Price", price)
                product_description = self.add_to_str(product_description, "Bestseller Status", bestseller_status)
                product_description = self.add_to_str(product_description, "Star Rating", star_rating)
                product_description = self.add_to_str(product_description, "List Price", list_price)

                product = Action(ActionType.CLICK_RESULT, product_description, full_url)
                products.append(product)

        return products  

    def add_to_str(self, str, key, item):
        if item is not None:
            if str is None:
                str = key + ": " + item

            str += "; " + key + ": " + item

        return str

    def extract_recommendations_from_product_details(self, page):
        # TODO: implement - copy/paste from amazon_scrape_test
        return []

    def extract_checkout_from_product_details(self, page):
        content  = self.scrape_and_cache(page)
        soup     = BeautifulSoup(content, "lxml")

        product_description = ""

        feature_bullets_div = soup.find("div", id="feature-bullets")

        # Find the span element with id "productTitle"
        product_title_span = soup.find("span", id="productTitle")

        if product_title_span:
            escaped_title = product_title_span.get_text(strip=True)
            product_description = self.add_to_str(product_description, "Product Title: ", escaped_title)

        # Extract the bullet points
        if feature_bullets_div:
            bullet_points = feature_bullets_div.find_all("span", class_="a-list-item")

            bullet_points = ""
            for bullet_point in bullet_points:
                if bullet_point.get_text() != "":
                    bullet_points += bullet_point.get_text() + "; "
            product_description = self.add_to_str(product_description, "Product Description: ", bullet_points)

        # Find the span elements with class "a-price-range"
        price_range_spans = soup.find_all("span", class_="a-price-range")

        for price_range_span in price_range_spans:
            # Extract the price from each span
            price_elements = price_range_span.find_all("span", class_="a-price")
            for price_element in price_elements:
                price = price_element.find("span", class_="a-offscreen").get_text()
                product_description = self.add_to_str(product_description, "Price: ", bullet_points)

        # Find the span element with class "reviewCountTextLinkedHistogram"
        average_review_span = soup.find("span", class_="reviewCountTextLinkedHistogram")

        if average_review_span:
            title = average_review_span.get("title")
            average_review = title.split(" ")[0] if title else None
            product_description = self.add_to_str(product_description, "Average Review: ", average_review)

        # Find the span element with id "acrCustomerReviewText"
        ratings_span = soup.find("span", id="acrCustomerReviewText")

        if ratings_span:
            num_ratings = ratings_span.get_text().replace(" ratings", "").replace(",", "")
            product_description = self.add_to_str(product_description, "Number Ratings: ", num_ratings)

        return [Action(ActionType.CHECKOUT, product_description, None)]

    def generate_amazon_search_url(self, search_query):
        base_url = "https://www.amazon.com/s"
        query_params = {'k': search_query.replace(' ', '+')}  # Replace spaces with '+'
        encoded_params = '&'.join([f"{key}={value}" for key, value in query_params.items()])
        amazon_search_url = f"{base_url}?{encoded_params}"
        return amazon_search_url

class Agent:
    def __init__(self, user_profile, initial_goal, scraper):
        self.user_profile          = user_profile
        self.initial_goal          = initial_goal
        self.actions_history       = []
        self.next_possible_actions = []
        self.scraper               = scraper

    def execute(self):
        if len(self.actions_history) == 0:
            self.next_possible_actions = self.scraper.get_initial_actions(self.initial_goal)

        while True:
            next_action = self.choose_from_next_actions()

            if next_action is not None:
                #print(next_action.to_json())
                self.actions_history.append(next_action)

            if next_action is not None and next_action.action_type is not ActionType.CHECKOUT:
                self.next_possible_actions = self.scraper.scrape_page_into_possible_actions(next_action.target_url)
                #print(Action.array_to_json(self.next_possible_actions))
            else:
                break

    def choose_from_next_actions(self):
        # Temporary helper for testing / TODO: remove
        if len(self.next_possible_actions) >= 1:
            return self.next_possible_actions[0]
        else:
            return None

        # TODO: Add compressed user history?
        base_prompt = """
        I am trying to create synthetic data with LLMs for ecommerce startups.
        More specifically, I am telling you to act as a consumer with this goal: {goal}
        You are currently browsing the ecommerce webpage and are presented with these options:
        {options}

        The actions should be taken from the point of view of a user with the following profile:
        - Gender: {gender}
        - Age Range: {age_from} - {age_to}
        - Location: {location}
        - Interest: {interest}

        Please think carefully how users with different profiles interact with the platform when making e-commerce purchases.
        Tell me which option you are taking by responding with the corresponding action ID only.
        """
        prompt = PromptTemplate.from_template(base_prompt)
        chain  = LLMChain(llm=OpenAI(max_tokens=-1), prompt=prompt, verbose=1)

        options = Action.array_to_json(self.next_possible_actions)

        result = chain.run(
                {"goal":self.initial_goal, "options":options,
                "gender":self.user_profile.gender,
                "age_from":self.user_profile.age_from, "age_to":self.user_profile.age_to,
                "location":self.user_profile.location, "interest":self.user_profile.interest})

        return self.find_next_action_by_id(result)

    def find_next_action_by_id(self, action_id):
        if len(self.next_possible_actions) == 0:
            return None

        for action in self.next_possible_actions:
            if action.action_id == action_id:
                return action

        return None

###

scraper = AmazonScraper()
up      = UserProfile("Male", "18", "35", "United States", "Hiking")
agent   = Agent(up, "hiking shoes", scraper)
agent.execute()

print(Action.array_to_json(agent.actions_history))