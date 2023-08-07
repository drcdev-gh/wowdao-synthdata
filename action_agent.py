from langchain import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.callbacks import StdOutCallbackHandler
from enum import Enum

class UserProfile:
    def __init__(self, gender, age_from, age_to, location, interest):
        self.gender     = gender
        self.age_from   = age_from
        self.age_to     = age_to
        self.location   = location
        self.interest   = interest

class ActionType(Enum):
    QUERY             = 1
    CLICK_RESULT      = 2
    CLICK_RECOMMENDED = 3
    CLICK_FREQ_BOUGHT = 4

class Action:
    def __init__(self, action_type, context, target_url):
        self.action_type = action_type
        self.context     = context
        self.target_url  = target_url

base_prompt = """
    I am creating synthetic data with the Python SDV library for ecommerce startups.
    I am using OpenAI to create the base data.

    For the following query, please generate a base dataset of {num_actions} actions that are part of a coherent user journey and print all {num_actions} actions in JSON format.
    Do not use lists in the format, instead use a postfix like "_1" or "_2" for lists.

    The actions should cover the user journey "{user_journey}".
    Include the following action categories: {action_categories}

    The actions should be taken from the point of view of a user with the following profile:
    - Gender: {gender}
    - Age Range: {age_from} - {age_to}
    - Location: {location}
    - Interest: {interest}

    Please think carefully how users with different profiles interact with the platform when making e-commerce purchases.
    Only answer with the JSON.

    Use the following JSON snippet as guideline for your output:
    "index": 0,
    "action": "search",
    "timestamp": "2023-08-01T10:00:00",
    "user_id": "user_1",
    "query": "hiking boots",
    "filters_1": "brand:North Face",
    "filters_2": "size:10",
    "product_id": "prod_123",
    "sort_option": "price_low_to_high",
    "product_1": "prod_124",
    "product_2": "prod_125"
"""

up     = UserProfile("male", "18", "27", "United States", "Hiking")
prompt = PromptTemplate.from_template(base_prompt)

chain = LLMChain(
    llm=OpenAI(max_tokens=-1),
    prompt=prompt,
    verbose=1
)

result = chain.run(
        {"num_actions":"25", "user_journey":"Buy hiking boots", "action_categories":", ".join(ub.action_categories),
        "gender":up.gender, "age_from":up.age_from, "age_to":up.age_to, "location":up.location, "interest":up.interest},
)

print(result)