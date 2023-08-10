from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from fastapi import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import datetime

import action_agent
import agent_task

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserProfileData(BaseModel):
    gender: str
    ageFrom: int
    ageTo: int
    location: str
    interests: List[str]
    description: Optional[str] = None

    @classmethod
    def from_user_profile(cls, user_profile: action_agent.UserProfile):
        return cls(
            gender=user_profile.gender,
            ageFrom=user_profile.age_from,
            ageTo=user_profile.age_to,
            location=user_profile.location,
            interests=user_profile.interests,
            description=user_profile.description
        )


class AgentResponse(BaseModel):
    id: Optional[str] = None
    name: str
    profile: UserProfileData

    @classmethod
    def from_agent(cls, agent: action_agent.Agent):
        return cls(id=agent.id, name=agent.name, profile=UserProfileData.from_user_profile(agent.user_profile))


class LogResponse(BaseModel):
    timestamp: int
    agent_id: str
    task_id: str
    action_id: str
    action_type: str
    goal: str
    seed: str
    url: str
    step: int

    @classmethod
    def from_action_history_entry(cls, action_history_entry: action_agent.Action,
                                  task: agent_task.AgentTask):
        # TODO: fix the dummy entries
        return cls(timestamp=int(round(datetime.datetime.now().timestamp())),
                   agent_id=str(task.agent.id),
                   task_id=str(task.id),
                   action_id=str(action_history_entry.action_id),
                   action_type=str(action_history_entry.action_type),
                   goal=task.initial_goal,
                   seed=str(task.seed),
                   url=action_history_entry.target_url,
                   step=1)

class TaskResponse(BaseModel):
    id: str
    agent_id: str
    status: str

    @classmethod
    def from_agent_task(cls, agent_task: agent_task.AgentTask):
        return cls(id=str(agent_task.id),
                   agent_id=str(agent_task.agent.id),
                   status=str(agent_task.status))

class AgentCreate(BaseModel):
    name: str
    profile: UserProfileData

class AgentTaskMetaData(BaseModel):
    goal: str
    seed: Optional[str] = None

AGENT_DB: List[action_agent.Agent] = {}
TASK_DB: List[agent_task.AgentTask] = {}

@app.post("/agents", response_model=AgentResponse)
def create_agent(agent_data: AgentCreate):
    agent_id      = str(uuid.uuid1())
    profile       = action_agent.UserProfile(agent_data.profile.gender,
                                             agent_data.profile.ageFrom,
                                             agent_data.profile.ageTo,
                                             agent_data.profile.location,
                                             agent_data.profile.interests,
                                             agent_data.profile.description)
    new_agent     = action_agent.Agent(agent_id, agent_data.name, profile)
    AGENT_DB[agent_id] = new_agent
    profile.persist()
    new_agent.persist()
    return AgentResponse.from_agent(new_agent)


@app.get("/agents", response_model=List[AgentResponse])
def get_agents():
    ret = []
    for agent_entry in AGENT_DB.values():
        ret.append(AgentResponse.from_agent(agent_entry))
    return ret


@app.get("/agents/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str):
    if agent_id not in AGENT_DB:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse.from_agent(AGENT_DB[agent_id])


@app.delete("/agents/{agent_id}", response_model=AgentResponse)
def delete_agent(agent_id: str):
    if agent_id not in AGENT_DB:
        raise HTTPException(status_code=404, detail="Agent not found")
    deleted_agent = AGENT_DB.pop(agent_id)
    return deleted_agent


def run_agent_task(task):
    task.execute()

@app.post("/agents/{agent_id}/dispatch")
async def dispatch_agent(agent_id: str, metadata: AgentTaskMetaData, background_tasks: BackgroundTasks):
    if agent_id not in AGENT_DB:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = AGENT_DB[agent_id]
    # TODO: support different types of scrape source.
    task = agent_task.AgentTask(agent, action_agent.AmazonScraper(), metadata.goal, metadata.seed)
    TASK_DB[task.id] = task
    task.persist()
    background_tasks.add_task(run_agent_task, task)
    return "Successfully started"


@app.get("/tasks")
async def get_tasks() -> List[TaskResponse]:
    # TODO: comply with frontend types.
    ret = []
    for task_entry in TASK_DB.values():
        ret.append(TaskResponse.from_agent_task(task_entry))
    return ret


@app.get("/logs")
async def get_logs() -> List[LogResponse]:
    ret = []
    for task_entry in TASK_DB.values():
        for action_entry in task_entry.actions_history:
            ret.append(LogResponse.from_action_history_entry(action_history_entry=action_entry, task=task_entry))

    return ret

def table_exists(table_name):
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    c.execute('''
        SELECT name FROM sqlite_master WHERE type='table' AND name=?
    ''', (table_name,))
    return c.fetchone() is not None

def restore_instances():
    if not (table_exists('agents') and table_exists('user_profiles')):
        return
    
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()

    c.execute('''
    SELECT agents.id, agents.name, user_profiles.gender, user_profiles.age_from,
           user_profiles.age_to, user_profiles.location, user_profiles.interests,
           agent_tasks.id, agent_tasks.initial_goal, agent_tasks.seed, agent_tasks.status
        FROM agents
        JOIN user_profiles ON agents.user_profile_id = user_profiles.id
        LEFT JOIN agent_tasks ON agent_tasks.agent_id = agents.id
    ''')
    rows = c.fetchall()
    for row in rows:
        agent_id, agent_name, gender, age_from, age_to, location, interests_str, agent_task_id, initial_goal, seed, status = row
        interests = interests_str.split(', ')
        user_profile = action_agent.UserProfile(gender, age_from, age_to, location, interests)
        agent = action_agent.Agent(agent_id, agent_name, user_profile)

        if agent_task_id:
            agenttask = agent_task.AgentTask(agent, action_agent.AmazonScraper(), initial_goal, seed)
            agenttask.id = agent_task_id
            agenttask.status = status
            agenttask.load_history()
            if agent_task_id not in TASK_DB:
                TASK_DB[agent_task_id] = agenttask
        
        if agent_id not in AGENT_DB:
            AGENT_DB[agent_id] = agent

# Call the restore_instances function
restore_instances()