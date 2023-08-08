<script>
	import '../app.css';
	import Header from './Header.svelte';
	import { SvelteUIProvider } from '@svelteuidev/core';
</script>

<SvelteUIProvider withNormalizeCSS withGlobalStyles themeObserver={'dark'}>
	<div class="app">
		<Header />
		<main>
			<slot />
		</main>
	</div>
</SvelteUIProvider>

<style>
	.app {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}

	main {
		flex: 1;
		display: flex;
		flex-direction: column;
		padding: 1rem;
		width: 100%;
		max-width: 64rem;
		margin: 0 auto;
		box-sizing: border-box;
	}
</style>
