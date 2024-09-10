<script lang="ts">
	import Sidebar from '$lib/components/Sidebar.svelte';
	import '../app.postcss';
	import 'flowbite/dist/flowbite.css';
	import 'carta-md/default.css';
</script>

<div class="app">
	<Sidebar />
	<main>
		<slot />
	</main>
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
	}
	.app {
		display: flex;
		min-height: 100vh;
	}
	main {
		flex: 1;
		padding: 1rem;
	}
</style>
