<style>
  table {
    width: 100%;
    border-collapse: collapse;
    border: 1px solid #ccc;
    margin-top: 20px;
    font-size: 0.8em;
  }

  th, td {
    padding: 10px;
    border: 1px solid #ccc;
    text-align: left;
  }

  th {
    background-color: #393e46;
    font-weight: bold;
  }

  th.url {
    width: 10%;
  }

  .header-row {
    background-color: #393e46;
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
	import { Container, Divider } from '@svelteuidev/core';
    import { format } from 'date-fns';

	import { apiClient as api } from '$lib/api';

	let logEntries = [];

	onMount(async () => {
		logEntries = await api.getLogs();
	});

	function redirectToURL(url) {
 	   window.open(url, '_blank');
	}

</script>

<svelte:head>
	<title>Logs</title>
	<meta name="description" content="Logs" />
</svelte:head>

<section class="flex">
	<Container>
		<h1 class="text-3xl font-bold">Logs</h1>
		<Divider class="my-5" />
		{#if logEntries.length > 0}
			<table class="table table-fixed w-full">
				<thead>
					<tr class="header-row">
						<th class="w-48">Timestamp</th>
						<th class="w-24">Agent ID</th>
						<th class="w-24">Task ID</th>
						<th class="w-24">Action ID</th>
						<th class="w-48">Action Type</th>
						<th class="w-48">Goal</th>
						<th class="w-24">URL</th>
						<th class="w-24">Step</th>
					</tr>
				</thead>
				<tbody>
					{#each logEntries as row}
						<tr>
                            <td class="w-24">{format(new Date(row.timestamp * 1000), 'PPpp')}</td>
							<td class="truncate w-24">{row.agent_id}</td>
							<td class="truncate w-24">{row.task_id}</td>
							<td class="truncate w-24">{row.action_id}</td>
							<td class="w-48">{row.action_type.replace('ActionType.','')}</td>
							<td class="w-48">{row.goal}</td>
							<td class="truncated-url w-24">
								<span class="clickable-url" on:click={() => redirectToURL(row.url)}>
								 {row.url.slice(0, 30)}...
								</span>
							</td>
							<td class="w-24">{row.step}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		{:else}
			<p>Loading...</p>
		{/if}
	</Container>
</section>
