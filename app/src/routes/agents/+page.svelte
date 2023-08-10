<script lang="ts">
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';
	import {
		Button,
		Center,
		Container,
		Divider,
		Modal,
		Group,
		NativeSelect,
		InputWrapper,
		RadioGroup,
		Title,
		Text,
		TextInput,
		Textarea
	} from '@svelteuidev/core';
	import { toast } from '@zerodevx/svelte-toast';
	import { apiClient as api } from '$lib/api';
	import type { Agent, Profile } from '$lib/api';
	import { getAgentsStore } from './stores';

	let opened = false;

	function toggleOpen() {
		opened = !opened;
	}

	function handleClose() {
		opened = false;
	}

	const genders = [
		{ label: 'Male', value: 'male' },
		{ label: 'Female', value: 'female' }
	];

	let name = '';
	let gender = 'male';
	let ageFrom: number = 0;
	let ageTo: number = 0;
	let location = '';
	let interests = '';
	let description = '';

	function handleCreate() {
		const profile: Profile = {
			gender,
			ageFrom: parseInt(ageFrom),
			ageTo: parseInt(ageTo),
			location,
			interests: interests.split(',').map((interest) => interest.trim()),
			description
		};

		const agent: Agent = {
			name,
			profile
		};

		console.log(`Creating agent: ${JSON.stringify(agent)}`);

		agents
			.create(agent)
			.then((agent) => {
				console.log(`Successfully created: ${JSON.stringify(agent)}`);
				toast.push(`Successfully created: ${agent.name}`, {
					theme: {
						'--toastColor': 'mintcream',
						'--toastBackground': 'rgba(72,187,120,0.9)',
						'--toastBarBackground': '#2F855A'
					}
				});
			})
			.catch((err) => {
				console.log(`Error: ${err}`);
				toast.push(`Error: ${err}`, {
					theme: {
						'--toastColor': 'mintcream',
						'--toastBackground': '#ffcbcb',
						'--toastBarBackground': '#ffb5b5'
					}
				});
			})
			.finally(() => {
				// close modal.
				opened = false;
			});
	}

	let dispatchModalOpen = false;
	let dispatchAgent;
	let goal;
	let tasknr;

	function handleDispatchToggle(agent: Agent) {
		dispatchAgent = agent;
		dispatchModalOpen = !dispatchModalOpen;
	}

	function handleDispatchClose() {
		dispatchAgent = null;
		dispatchModalOpen = false;
	}

	function handleDispatchClick() {
		api
			.dispatchAgentTask(dispatchAgent.id, goal, tasknr)
			.then((status) => {
				toast.push(`Dispatched task for agent: ${dispatchAgent.name}`, {
					theme: {
						'--toastColor': 'mintcream',
						'--toastBackground': 'rgba(72,187,120,0.9)',
						'--toastBarBackground': '#2F855A'
					}
				});
			})
			.catch((err) => {
				toast.push(`Error: ${err}`, {
					theme: {
						'--toastColor': 'mintcream',
						'--toastBackground': '#ffcbcb',
						'--toastBarBackground': '#ffb5b5'
					}
				});
			})
			.finally(() => {
				dispatchModalOpen = false;
			});
	}

	const agents = getAgentsStore();

	onMount(async () => {
		await agents.init();
	});
</script>

<svelte:head>
	<title>Agents</title>
	<meta name="description" content="Agents list." />
</svelte:head>

<Modal opened={dispatchModalOpen} title="Set goal for agent" on:close={handleDispatchClose}>
	<TextInput label="Goal" bind:value={goal} radius="sm" />
	<TextInput label="Number of tasks to spawn" bind:value={tasknr} radius="sm" />
	<Button class="mt-10" on:click={handleDispatchClick}>Start Task</Button>
</Modal>

<Modal {opened} title="Create Agent" on:close={handleClose}>
	<TextInput label="Name" bind:value={name} radius="sm" />
	<RadioGroup label="Gender" bind:value={gender} items={genders} />
	<TextInput label="Age From" bind:value={ageFrom} radius="sm" />
	<TextInput label="Age To" bind:value={ageTo} radius="sm" />
	<TextInput label="Location" bind:value={location} radius="sm" />
	<Textarea
		label="Interests"
		placeholder="games,sports,football,hiphop"
		description="comma separated list of interests"
		radius="sm"
		bind:value={interests}
	/>
	<Textarea
		label="Description"
		description="Additional description of imaginary user"
		radius="sm"
		size="xl"
		bind:value={description}
	/>
	<Button on:click={handleCreate}>Create</Button>
</Modal>

<section class="flex flex-col justify-center grow">
	<Container>
		<Button on:click={toggleOpen}>Create Agent</Button>
		<Divider class="my-5" />
		<table class="table-auto text-center">
			<thead>
                <tr>
                    <th class="px-8">Name</th>
                    <th class="px-8">Gender</th>
                    <th class="px-8">Age</th>
                    <th class="px-8">Location</th>
                    <th class="px-8">Interests</th>
                    <th class="px-8">Description</th>
                    <th class="px-10">New Task</th>
                </tr>
			</thead>
			<tbody>
				{#each $agents as agent}
					<tr>
						<td class="px-5">{agent.name}</td>
						<td class="px-5">{agent.profile.gender}</td>
						<td class="px-5">{agent.profile.ageFrom} - {agent.profile.ageTo}</td>
						<td>{agent.profile.location}</td>
						<td>{agent.profile.interests.join(', ')}</td>
						<td>{agent.profile.description}</td>
						<td class="flex justify-center">
							<Button on:click={() => handleDispatchToggle(agent)}>New Task</Button>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</Container>
</section>
