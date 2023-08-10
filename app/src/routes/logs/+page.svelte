<style>
  table {
    width: 100%;
    border-collapse: collapse;
    border: 1px solid #ccc;
    margin-top: 20px;
  }

  th, td {
    padding: 10px;
    border: 1px solid #ccc;
    text-align: left;
  }

  th {
    background-color: #f2f2f2;
    font-weight: bold;
  }

  th.url {
    width: 10%;
  }

  .header-row {
    background-color: #333;
    color: #fff;
  }

  .loading {
    font-style: italic;
    color: #999;
  }

  .truncated-url {
    max-width: 100px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .clickable-url {
    color: blue;
    text-decoration: underline;
    cursor: pointer;
  }
</style>

<script>
	import { onMount } from 'svelte';
	import { Container } from '@svelteuidev/core';
	import SvelteTable from 'svelte-table';

	import { apiClient as api } from '$lib/api';

	let logEntries = [];

	onMount(async () => {
		logEntries = await api.getLogs();
		console.log(logEntries)
	});

	function redirectToURL(url) {
 	   window.open(url, '_blank');
	}

</script>

<svelte:head>
	<title>Logs</title>
	<meta name="description" content="Logs" />
</svelte:head>

<section class="flex flex-col justify-center grow">
	<Container>
		<h1 class="text-3xl font-bold">Logs</h1>
		{#if logEntries.length > 0}
			<table>
				<thead>
					<tr class="header-row">
						<th>Timestamp</th>
						<th>Agent ID</th>
						<th>Task ID</th>
						<th>Action ID</th>
						<th>Action Type</th>
						<th>Goal</th>
						<th class="url">URL</th>
						<th>Step</th>
					</tr>
				</thead>
				<tbody>
					{#each logEntries as row}
						<tr>
							<td>{row.timestamp}</td>
							<td>{row.agent_id}</td>
							<td>{row.task_id}</td>
							<td>{row.action_id}</td>
							<td>{row.action_type}</td>
							<td>{row.goal}</td>
							<td class="truncated-url">
								<span class="clickable-url" on:click={() => redirectToURL(row.url)}>
								 {row.url.slice(0, 30)}...
								</span>
							</td>
							<td>{row.step}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		{:else}
			<p>Loading...</p>
		{/if}
	</Container>
</section>