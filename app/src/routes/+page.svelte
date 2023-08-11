<script>
	import Counter from './Counter.svelte';
	import logo from '$lib/images/logo2.png';
</script>

<svelte:head>
	<title>WOWDAO - FakeAgent</title>
	<meta name="description" content="Fake ChatGPT agent navigation job dispatcher." />
</svelte:head>

<style>
    .logo {
        width: 480px;
        height: 480px;
    }
</style>

<section class="flex flex-col justify-center items-center grow">
	<div class="logo">
		<span class="">
			<picture>
				<img src={logo} alt="logo" />
			</picture>
		</span>
	</div>
</section>
