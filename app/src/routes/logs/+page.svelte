<script>
	import { onMount } from 'svelte';
	import { Container } from '@svelteuidev/core';
	import SvelteTable from 'svelte-table';

	onMount(async function () {
		// TODO: Load logs to table.
	});
</script>

<svelte:head>
	<title>Logs</title>
	<meta name="description" content="Logs" />
</svelte:head>

<section class="flex flex-col justify-center grow">
	<Container>
		<h1 class="text-3xl font-bold">Logs</h1>
	</Container>
</section>
