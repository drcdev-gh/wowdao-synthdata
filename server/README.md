# SynthData Generation - Server Usage

Install requirements:
```bash
pip install -r requirements.txt
```

Export your OpenAI API key:
```bash
export OPENAI_API_KEY="..."
```

Start the server:
```bash
uvicorn main:app --reload
```

From another shell, create a new agent:
```bash
curl -X POST "http://localhost:8000/agents" -H "Content-Type: application/json" -d '{
  "name": "Test Agent",
  "profile": {
    "gender": "male",
    "ageFrom": 20,
    "ageTo": 40,
    "location": "New York",
    "interests": ["outdoors", "sports"]
  }
}'
```

Get all agents:
```bash
curl -X GET "http://localhost:8000/agents"
```

Get agent details by ID:
```bash
curl -X GET "http://localhost:8000/agents/{agent_id}"
```

Delete an agent:
```bash
curl -X DELETE "http://localhost:8000/agents/{agent_id}"
```

Get logs for an agent:
```bash
curl -X GET "http://localhost:8000/agents/{agent_id}/logs"
```

Get status of an agent:
```bash
curl -X GET "http://localhost:8000/agents/{agent_id}/status"
```
Note: 1 = Not started, 2 = In progress, 3 = Finished

Start executing an agent:
```bash
curl -X POST "http://localhost:8000/agents/{agent_id}/dispatch" -H "Content-Type: application/json" -d '{
  "goal": "Hiking Shoes"
}'
```

This will immediately return. Check the status to see when it has finished.
