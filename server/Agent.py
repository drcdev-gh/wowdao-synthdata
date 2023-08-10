import enum
from enum import Enum
import sqlite3


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


class AgentStatus(Enum):
    NOT_STARTED = enum.auto()
    IN_PROGRESS = enum.auto()
    FINISHED    = enum.auto()