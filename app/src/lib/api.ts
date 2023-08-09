import dummyData from './dummyData.json';
import { PUBLIC_API_BASE_URL } from '$env/static/public';

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

export class ApiClient {
	constructor(private baseUrl: string) {
		this.baseUrl = baseUrl;
	}

	async createAgent(agent: Agent): Promise<Agent> {
		return fetch(`${this.baseUrl}/agents`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(agent)
		}).then((res) => res.json());
	}

	async getAgents(): Promise<Agent[]> {
		// return fetch(`${this.baseUrl}/agents`).then((res) => res.json());
		return Promise.resolve(dummyData);
	}

	async getAgent(id: string): Promise<Agent> {
		return fetch(`${this.baseUrl}/agents/${id}`).then((res) => res.json());
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

export const apiClient = new ApiClient(PUBLIC_API_BASE_URL);
