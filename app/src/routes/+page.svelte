<script>
	import Counter from './Counter.svelte';
	import logo from '$lib/images/logo2.png';
</script>

<svelte:head>
	<title>Botify</title>
	<meta name="description" content="Fake ChatGPT agent navigation job dispatcher." />
</svelte:head>

<style>
    .logo {
        width: 480px;
        height: 480px;
    }
</style>

<section class="flex flex-col justify-center items-center grow">
    <h1 class="my-20 text-4xl font-bold">Botify</h1>
	<div class="logo">
		<span class="">
			<picture>
				<img src={logo} alt="logo" />
			</picture>
		</span>
	</div>
</section>
