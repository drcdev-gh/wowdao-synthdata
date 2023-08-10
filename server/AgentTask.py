import enum
import logging
import sqlite3
import uuid

from langchain import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

from Action import Action, ActionType
from Agent import Agent
from Scraper import Scraper

logger = logging.getLogger('uvicorn')

class TaskStatus(enum.Enum):
    NOT_STARTED = enum.auto()
    IN_PROGRESS = enum.auto()
    FINISHED    = enum.auto()

class AgentTask:
    def __init__(self, agent: Agent, scraper: Scraper, initial_goal, seed=None):
        self.id = uuid.uuid1()
        self.agent = agent
        self.initial_goal = initial_goal
        self.actions_history = []
        self.next_possible_actions = []
        self.scraper: Scraper = scraper
        # TODO needed?
        if seed is None:
            self.seed = uuid.uuid1()
        else:
            self.seed = seed
        self.status = TaskStatus.NOT_STARTED

    def persist(self):
        # TODO: not persisting scraper
        conn = sqlite3.connect("storage.db")
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS agent_tasks (
                id TEXT PRIMARY KEY,
                agent_id TEXT,
                initial_goal TEXT,
                seed TEXT,
                status INTEGER,
                FOREIGN KEY (agent_id) REFERENCES agents (id)
            )
        """)

        c.execute('''
            INSERT INTO agent_tasks (id, agent_id, initial_goal, seed, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            str(self.id), str(self.agent.id), self.initial_goal, str(self.seed), self.status.value
        ))
        conn.commit()

    def load_history(self):
        if len(self.actions_history) > 0:
            return

        conn = sqlite3.connect("storage.db")
        c = conn.cursor()

        c.execute('''
            SELECT name FROM sqlite_master WHERE type='table' AND name=?
        ''', ("logs",))
        if c.fetchone() is None:
            return

        c.execute('''
            SELECT agent_id, task_id, action_id, action_type, context, target_url, step
            FROM logs
            WHERE task_id = ?
            ORDER BY step
        ''', (str(self.id),))

        rows = c.fetchall()
        history = []

        for row in rows:
            agent_id, task_id, action_id, action_type, context, target_url, step = row
            action = Action(action_type, context, target_url)
            action.action_id = action_id
            action.step = step
            history.append(action)

        conn.close()
        self.actions_history = history

    def save_history(self):
        conn = sqlite3.connect("storage.db")
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                agent_id TEXT,
                task_id TEXT,
                action_id TEXT PRIMARY KEY,
                action_type TEXT,
                context TEXT,
                target_url TEXT,
                step INTEGER
            )
        """)

        for step, action in enumerate(self.actions_history, start=1):
            c.execute('''
                INSERT INTO logs (agent_id, task_id, action_id, action_type, context, target_url, step)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(self.agent.id), str(self.id), str(action.action_id), str(action.action_type.value), str(action.context), str(action.target_url), step
            ))
            conn.commit()
            # TODO: This is really ugly and should be somewhere else, but I'm too lazy
            action.step = step
        conn.close()

    def execute(self):
        self.status = TaskStatus.IN_PROGRESS

        if len(self.actions_history) == 0:
            self.next_possible_actions = self.scraper.get_initial_actions(self.initial_goal)

        while True:
            next_action = self.choose_from_next_actions()
            #logger.info(f"Agent: {self.agent.id} Task: {self.id} Action: {str(next_action)}")

            if next_action is not None:
                #print(next_action.to_json())
                self.actions_history.append(next_action)

            if next_action is not None and next_action.action_type is not ActionType.BUY_NOW:
                self.next_possible_actions = self.scraper.scrape_page_into_possible_actions(next_action.target_url)
                #print(Action.array_to_json(self.next_possible_actions))
            else:
                break
        logger.info(f'Task {self.id} finished')

        self.save_history()
        self.status = TaskStatus.FINISHED
        self.persist_status_update()

    def persist_status_update(self):
        conn = sqlite3.connect("storage.db")
        c = conn.cursor()

        c.execute('''
            UPDATE agent_tasks
            SET status = ?
            WHERE id = ?
        ''', (self.status.value, str(self.id)))

        conn.commit()
        conn.close()

    def choose_from_next_actions(self):
        if len(self.next_possible_actions) == 1:
            return self.next_possible_actions[0]

        base_prompt = """
        I am trying to create synthetic data with LLMs for ecommerce startups.
        More specifically, I am telling you to act as a consumer with this goal: {goal}
        You are currently browsing the ecommerce webpage and are presented with these options:
        {options}

        You have previously taken the following actions. You want to choose the best option to buy (with a BUY_NOW action) after a maximum of {steps} steps:
        {previous_actions}

        The actions should be taken from the point of view of a user with the following profile:
        - Gender: {gender}
        - Age Range: {age_from} - {age_to}
        - Location: {location}
        - Interests: {interests}

        Please think carefully how users with different profiles interact with the platform when making e-commerce purchases.
        Tell me which option you are taking by responding with the corresponding action ID only.
        """
        prompt = PromptTemplate.from_template(base_prompt)
        chain  = LLMChain(llm=OpenAI(max_tokens=-1), prompt=prompt)#, verbose=1)

        options          = Action.array_to_json(self.next_possible_actions)
        previous_actions = Action.array_to_json(self.actions_history)

        result = chain.run(
                {"goal": self.initial_goal,
                 "options": options,
                 "steps": "10",
                 "previous_actions": previous_actions,
                 "gender": self.agent.user_profile.gender,
                 "age_from": self.agent.user_profile.age_from,
                 "age_to": self.agent.user_profile.age_to,
                 "location": self.agent.user_profile.location,
                 "interests": ", ".join(self.agent.user_profile.interests)})

        return self.find_next_action_by_id(result)

    def find_next_action_by_id(self, action_id):
        if len(self.next_possible_actions) == 0:
            return None

        for action in self.next_possible_actions:
            if str(action.action_id).strip() == str(action_id).strip():
                return action

        return None

    def get_action_history(self):
        return Action.array_to_json(self.actions_history)