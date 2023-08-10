<script lang="ts">
	import { onMount } from 'svelte';
	import { Center, Container, Divider } from '@svelteuidev/core';
	import { apiClient as api } from '$lib/api';
	import type { Task } from '$lib/api';

	let tasks = [];

	onMount(async function () {
        const data = await api.getTasks();
        tasks = data.map((task) => {
            return {
                id: task.id.slice(0, 8),
                goal: task.goal,
                seed: task.seed,
                status: task.status.replace('TaskStatus.', '')
            };
        });
    });
</script>

<svelte:head>
	<title>Tasks</title>
	<meta name="description" content="Tasks" />
</svelte:head>

<section class="flex">
	<Container>
		<Center><h1 class="text-3xl font-bold my-50">Tasks</h1></Center>
		<Divider class="my-5" />
        <table class="table w-full table-auto text-center">
            <thead class="table-header-group">
                <tr>
                    <th class="px-8">Id</th>
                    <th class="px-8">Goal</th>
                    <th class="px-8">Seed</th>
                    <th class="px-8">Status</th>
                </tr>
            </thead>
        </table>
        <tbody>
            {#each tasks as task}
                <tr>
                    <td class="px-8">{task.id}</td>
                    <td class="px-8">{task.goal}</td>
                    <td class="px-8">{task.seed}</td>
                    <td class="px-8">{task.status}</td>
                </tr>
            {/each}
        </tbody>
	</Container>
</section>
