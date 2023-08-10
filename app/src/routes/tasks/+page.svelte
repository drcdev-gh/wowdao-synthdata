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
        <table class="table table-fixed text-center">
            <thead class="text-center">
                <tr>
                    <th class="w-32">Id</th>
                    <th class="w-48">Goal</th>
                    <th class="w-32">Status</th>
                </tr>
            </thead>
        </table>
        <tbody class="text-center">
            {#each tasks as task}
                <tr>
                    <td class="w-32">{task.id}</td>
                    <td class="w-48">{task.goal}</td>
                    <td class="w-32">{task.status}</td>
                </tr>
            {/each}
        </tbody>
	</Container>
</section>
