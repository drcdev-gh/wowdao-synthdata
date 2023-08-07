from langchain import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.callbacks import StdOutCallbackHandler
from enum import Enum
import uuid

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
    CHECKOUT          = 5

class Action:
    def __init__(self, action_type, context, target_url):
        self.action_id   = uuid.uuid1()
        self.action_type = action_type
        self.context     = context
        self.target_url  = target_url

class Scraper:
    def __init__(self, scraper_name):
        self.scraper_name = scraper_name

    def get_initial_actions(self):
        return []

    def scrape_page_into_possible_actions(self, page):
        return []

class Agent:
    def __init__(self, user_profile, initial_goal, scraper):
        self.user_profile          = user_profile
        self.initial_goal          = initial_goal
        self.actions_history       = []
        self.next_possible_actions = []
        self.scraper               = scraper

    def execute(self):
        if len(self.next_possible_actions) == 0:
            self.next_possible_actions = self.scraper.get_initial_actions()
        else:
            while True:
                next_action = self.choose_from_next_actions()
                if next_action is not None and next_action.action_type is not ActionType.CHECKOUT:
                    self.next_possible_actions = self.scraper.scrape_page_into_possible_actions(next_action.target_url)
                else:
                    break

    def choose_from_next_actions(self):
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

        result = chain.run(
                {"num_actions":"25", "goal":"Buy hiking boots",
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

#up     = UserProfile("male", "18", "27", "United States", "Hiking")
#prompt = PromptTemplate.from_template(base_prompt)
#
#chain = LLMChain(
#    llm=OpenAI(max_tokens=-1),
#    prompt=prompt,
#    verbose=1
#)
#
#result = chain.run(
#        {"num_actions":"25", "user_journey":"Buy hiking boots", "action_categories":", ".join(ub.action_categories),
#        "gender":up.gender, "age_from":up.age_from, "age_to":up.age_to, "location":up.location, "interest":up.interest},
#)
#
#print(result)