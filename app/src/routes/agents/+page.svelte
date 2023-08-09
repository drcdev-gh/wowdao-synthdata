<script lang="ts">
	import { onMount } from 'svelte';
	import {
		Button,
        Center,
		Container,
		Modal,
		Group,
		InputWrapper,
		RadioGroup,
        Title,
        Text,
		TextInput,
		Textarea
	} from '@svelteuidev/core';
	import SvelteTable from 'svelte-table';
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
	let ageFrom = '';
	let ageTo = '';
	let location = '';
	let interests = [];
	let description = '';

	function handleCreate() {
		const profile: Profile = {
			gender,
			ageFrom,
			ageTo,
			location,
			interests,
			description
		};

		const agent: Agent = {
			name,
			profile
		};

		api.createAgent(agent).then((agent) => {
			console.log(agent);
            // close modal.
            opened = false;
		});
	}

	const columns = [
		{ key: 'name', title: 'Name', value: (v) => v.name },
		{ key: 'age', title: 'Age', value: (v) => `${v.profile.ageFrom} - ${v.profile.ageTo}` },
		{ key: 'location', title: 'Location', value: (v) => v.profile.location },
		{ key: 'interests', title: 'Interests', value: (v) => v.profile.interests.join(', ') },
		{ key: 'description', title: 'Description', value: (v) => v.profile.description }
	];

    const agents = getAgentsStore();

	onMount(async () => {
      await agents.init();
	});
</script>

<svelte:head>
	<title>Agents</title>
	<meta name="description" content="Agents list." />
</svelte:head>

<Modal {opened} title="Create Agent profile." on:close={handleClose}>
	<TextInput label="Name" bind:name radius="sm" />
	<RadioGroup label="Gender" bind:gender items={genders} />
	<TextInput label="Age From" bind:ageFrom radius="sm" />
	<TextInput label="Age To" bind:ageTo radius="sm" />
	<TextInput label="Location" bind:location radius="sm" />
	<Textarea
		label="Interests"
		placeholder="games,sports,football,hiphop"
		description="comma separated list of interests"
		radius="sm"
	/>
	<Textarea
		label="Description"
		description="Additional description of imaginary user"
		radius="sm"
		size="xl"
	/>
	<Button on:click={handleCreate}>Create</Button>
</Modal>

<section class="flex flex-col justify-center grow">
	<Container>
		<Button on:click={toggleOpen}>Create Agent</Button>
        <Center>
            <Title order={1} class="mb-10">List of Agents</Title>
        </Center>
		<SvelteTable rows={$agents} {columns} classNameRow="my-10" classNameCell="px-10"/>
	</Container>
</section>
