<script>
	import Counter from './Counter.svelte';
	import logo from '$lib/images/logo.svg';
</script>

<svelte:head>
	<title>WOWDAO - FakeAgent</title>
	<meta name="description" content="Fake ChatGPT agent navigation job dispatcher." />
</svelte:head>

<section class="flex flex-col justify-center items-center grow">
	<h1>
		<span class="">
			<picture>
				<img src={logo} />
			</picture>
		</span>
	</h1>
	<h1>About</h1>
	<p>This is a hackathon demo for WOWDAO.</p>
</section>
