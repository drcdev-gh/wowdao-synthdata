from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
import asyncio
from fastapi import BackgroundTasks

import action_agent

app = FastAPI()

class AgentDbEntry:
    def __init__(self, api_agent, agent):
        self.api_agent = api_agent
        self.agent     = agent

class Profile(BaseModel):
    gender: str
    ageFrom: int
    ageTo: int
    location: str
    interests: List[str]
    description: Optional[str] = None

class Agent(BaseModel):
    id: Optional[str] = None
    name: str
    profile: Profile

class AgentCreate(BaseModel):
    name: str
    profile: Profile

class AgentUpdate(BaseModel):
    name: str
    profile: Profile

agent_db = {}

@app.post("/agents/", response_model=Agent)
def create_agent(agent: AgentCreate):
    agent_id      = str(uuid.uuid1())
    new_api_agent = Agent(id=agent_id, **agent.dict())

    scraper       = action_agent.AmazonScraper()
    up            = action_agent.UserProfile(agent.profile.gender,
                                            agent.profile.ageFrom,
                                            agent.profile.ageTo,
                                            agent.profile.location,
                                            agent.profile.interests)
    # TODO: goal is missing as parameter
    new_agent     = action_agent.Agent(up, "hiking shoes", scraper)

    agent_db[agent_id] = AgentDbEntry(new_api_agent, new_agent)
    return new_api_agent

@app.get("/agents/", response_model=List[Agent])
def get_agents():
    ret = []
    for agent_entry in agent_db.values():
        ret.append(agent_entry.api_agent)

    return ret

@app.get("/agents/{agent_id}", response_model=Agent)
def get_agent(agent_id: str):
    if agent_id not in agent_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_db[agent_id].api_agent

@app.delete("/agents/{agent_id}", response_model=Agent)
def delete_agent(agent_id: str):
    if agent_id not in agent_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    deleted_agent = agent_db.pop(agent_id)
    # TODO: make sure that the job is stopped?
    return deleted_agent

@app.get("/agents/{agent_id}/logs")
def get_agent_log(agent_id: str):
    if agent_id not in agent_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_db[agent_id].agent.actions_history

@app.get("/agents/{agent_id}/status")
def get_agent_status(agent_id: str):
    if agent_id not in agent_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_db[agent_id].agent.status

def run_execute(agent_id):
    agent_db[agent_id].agent.execute()

@app.get("/agents/{agent_id}/dispatch")
async def dispatch_agent(agent_id: str, background_tasks: BackgroundTasks):
    if agent_id not in agent_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    if agent_db[agent_id].agent.status is action_agent.AgentStatus.IN_PROGRESS:
        return "Already running"
    if agent_db[agent_id].agent.status is action_agent.AgentStatus.FINISHED:
        return "Already done"

    background_tasks.add_task(run_execute, agent_id=agent_id)

    return "Successfully started"