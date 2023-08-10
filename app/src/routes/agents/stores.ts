import { writable } from 'svelte/store';
import type { Agent } from '$lib/api';
import { apiClient as api } from '$lib/api';

export function getAgentsStore() {
	const { subscribe, set, update } = writable<Agent[]>([]);
	return {
		subscribe,
		init: async () => {
			const agents = await api.getAgents();
			set(agents);
		},
		create: async (agent: Agent): Promise<Agent> => {
			const newAgent = await api.createAgent(agent);
			update((agents) => [...agents, newAgent]);
			return newAgent;
		},
		delete: async (agent: Agent) => {
			if (!agent.id) {
				throw new Error('Agent id is not set');
			}
			update((agents) => agents.filter((a) => a.id !== agent.id));
			await api.deleteAgent(agent.id);
		}
	};
}
