<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let x: number;
	export let y: number;
	export let items: { label: string; action: string }[];

	const dispatch = createEventDispatcher();

	function handleAction(action: string) {
		dispatch('action', action);
	}
</script>

<div class="context-menu" style="left: {x}px; top: {y}px;">
	{#each items as item}
		<button on:click={() => handleAction(item.action)}>{item.label}</button>
	{/each}
</div>

<style>
	.context-menu {
		position: fixed;
		background-color: white;
		border: 1px solid #ccc;
		box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
		z-index: 1000;
	}

	.context-menu button {
		display: block;
		width: 100%;
		padding: 8px 12px;
		text-align: left;
		background: none;
		border: none;
		cursor: pointer;
	}

	.context-menu button:hover {
		background-color: #f0f0f0;
	}
</style>
