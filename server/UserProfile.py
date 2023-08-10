import sqlite3
import uuid


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