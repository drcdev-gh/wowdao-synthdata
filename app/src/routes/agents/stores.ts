import { writable } from 'svelte/store';
import type { Agent } from '$lib/api';
import { apiClient as api } from '$lib/api';
import { error } from '@sveltejs/kit'

export function getAgentsStore() {
	const { subscribe, set, update } = writable<Agent[]>([]);
	return {
		subscribe,
        init: async () => {
            const agents = await api.getAgents();
            set(agents);
        },
		create: async (agent: Agent) => {
            update(agents => [...agents, agent]);
            await api.createAgent(agent);
        },
        delete: async (agent: Agent) => {
            if (!agent.id) {
                throw error(403, 'Agent id is not set');
            }
            update(agents => agents.filter(a => a.id !== agent.id));
            await api.deleteAgent(agent.id);
        }
	};
}
