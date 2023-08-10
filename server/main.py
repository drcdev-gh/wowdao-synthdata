from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from fastapi import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

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


class TaskResponse(BaseModel):
    id: str
    agent_id: str
    status: str

    @classmethod
    def from_agent_task(cls, agent_task: agent_task.AgentTask):
        return cls(id=agent_task.id,
                   agent_id=agent_task.agent_id,
                   status=str(agent_task.status))


class AgentCreate(BaseModel):
    name: str
    profile: UserProfileData


class AgentTaskMetaData(BaseModel):
    goal: str
    seed: Optional[str] = None


# TODO: Make DBs persistent using sqlite.
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
async def get_logs():
    # TODO: comply with frontend types.
    ret = []
    for task_entry in TASK_DB.values():
        ret.extend(task_entry.get_action_history())
    return ret
