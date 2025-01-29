<script lang="ts">
	import { Drawer, Button } from 'flowbite-svelte';
	import { GridSolid } from 'flowbite-svelte-icons';
	import { sineIn } from 'svelte/easing';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import '../app.postcss';

	let hidden = true;
	let transitionParams = {
		x: -320,
		duration: 200,
		easing: sineIn
	};
</script>

<div class="app">
	<Button class="fixed left-4 top-4 z-20" on:click={() => (hidden = false)}>
		<GridSolid class="h-5 w-5" />
	</Button>

	<Drawer transitionType="fly" {transitionParams} bind:hidden id="sidebar-drawer">
		<Sidebar />
	</Drawer>

	<main class="relative flex-1 p-4 lg:pl-64">
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
</style>
