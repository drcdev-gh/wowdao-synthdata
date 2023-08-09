export interface Profile {
	gender: string;
	ageFrom: number;
	ageTo: number;
	location: string;
	interests: string[];
	description?: string;
}

export interface Agent {
	id?: string;
	name: string;
	goal: string,
	profile: Profile;
}

export default class ApiClient {
	constructor(private baseUrl: string) {
		this.baseUrl = baseUrl;
	}

	async createAgent(agent: Agent) {
		return fetch(`${this.baseUrl}/agents`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(agent)
		}).then((res) => res.json());
	}

	async getAgents() {
		return fetch(`${this.baseUrl}/agents`).then((res) => res.json());
	}

	async getAgent(id: string) {
		return fetch(`${this.baseUrl}/agents/${id}`).then((res) => res.json());
	}

	async getAgentStatus(id: string) {
		return fetch(`${this.baseUrl}/agents/${id}/status`).then((res) => res.json());
	}

	async getAgentLogs(id: string) {
		return fetch(`${this.baseUrl}/agents/${id}/logs`).then((res) => res.json());
	}

	async deleteAgent(id: string) {
		return fetch(`${this.baseUrl}/agents/${id}`, {
			method: 'DELETE'
		}).then((res) => res.json());
	}

	async dispatchAgent(id: string) {
		return fetch(`${this.baseUrl}/agents/${id}/dispatch`, {
			method: 'POST'
		}).then((res) => res.json());
	}
}
