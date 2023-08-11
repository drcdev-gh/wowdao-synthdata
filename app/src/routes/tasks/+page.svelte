<script lang="ts">
	import { onMount } from 'svelte';
	import { Center, Container, Divider } from '@svelteuidev/core';
    import FaRegCheckCircle from 'svelte-icons/fa/FaRegCheckCircle.svelte'
    import FaMinusCircle from 'svelte-icons/fa/FaMinusCircle.svelte'
    import { Circle, Circle2, Circle3 } from 'svelte-loading-spinners';
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

<style>
    table, th, td {
        border: 1px solid #ccc;
        font-size: 1em;
    }

    th {
        background-color: #393e46;
        color: #fff;
    }
    th, td {
        padding: 10px;
    }

    .icons {
        width: 32px;
        height: 32px;
    }
</style>

<svelte:head>
	<title>Tasks</title>
	<meta name="description" content="Tasks" />
</svelte:head>

<section class="flex">
	<Container>
		<h1 class="text-3xl font-bold my-50">Tasks</h1>
		<Divider class="my-5" />
        <table class="table table-fixed text-left border-collapse text-sm border-solid border w-full">
            <thead>
                <tr>
                    <th class="w-32">Task Id</th>
                    <th class="w-48">Goal</th>
                    <th class="w-8">Status</th>
                </tr>
            </thead>
            <tbody>
                {#each tasks as task}
                    <tr>
                        <td class="w-32">{task.id}</td>
                        <td class="w-48">{task.goal}</td>
                        <td class="w-8">
                            {#if task.status === 'FINISHED'}
                                <div class="icons">
                                    <FaRegCheckCircle/>
                                </div>
                            {:else if task.status === 'IN_PROGRESS'}
                                <div class="icons">
                                    <Circle size={32}/>
                                </div>
                            {:else if task.status === 'NOT_STARTED'}
                                <div class="icons">
                                    <FaMinusCircle/>
                                </div>
                            {:else}
                                {task.status}
                            {/if}
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>
	</Container>
</section>
