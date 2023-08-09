<script>
	import {
		Button,
		Container,
		Modal,
        Grid,
		Group,
		InputWrapper,
		RadioGroup,
		TextInput,
		Textarea
	} from '@svelteuidev/core';
    import Api, { Agent, Profile } from '$lib/api';

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

    const apiClient = new Api();

    function handleCreate() {
      const profile = {
        gender, ageFrom, ageTo, location, interests, description
      };

      const agent = {
        name, profile
      };

      apiClient.createAgent(agent).then((agent) => {
        console.log(agent);
      });
    }

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
	</Container>
    <Container>
    </Container>
</section>
