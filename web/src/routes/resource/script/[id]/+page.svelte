<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { Carta, MarkdownEditor } from 'carta-md';
	import '$lib/card-md.css';
	import { emoji } from '@cartamd/plugin-emoji';
	import { slash } from '@cartamd/plugin-slash';
	import { code } from '@cartamd/plugin-code';
	import DOMPurify from 'isomorphic-dompurify';
	import { Heading } from 'flowbite-svelte';
	let content = '';
	let isLoading = true;

	const carta = new Carta({
		sanitizer: DOMPurify.sanitize,
		extensions: [emoji(), slash(), code()]
	});

	onMount(async () => {
		const id = $page.params.id;
		try {
			const response = await fetch(`http://127.0.0.1:5432/scripts/${id}`);
			if (response.ok) {
				content = await response.text();
			} else {
				console.error('Failed to fetch prompt content');
			}
		} catch (error) {
			console.error('Error:', error);
		} finally {
			isLoading = false;
		}
	});

	async function handleSave() {
		const promptId = $page.params.id;
		try {
			const response = await fetch(`http://127.0.0.1:5432/prompts/${promptId}`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ content })
			});
			if (response.ok) {
				alert('Prompt saved successfully');
			} else {
				console.error('Failed to save prompt');
			}
		} catch (error) {
			console.error('Error:', error);
		}
	}
</script>

<main>
	<Heading tag="h1" class="py-4">Edit Script</Heading>
	{#if isLoading}
		<p>Loading script...</p>
	{:else}
		<MarkdownEditor bind:value={content} mode="tabs" theme="github" {carta} />
		<button on:click={handleSave}>Save Changes</button>
	{/if}
</main>

<style>
	:global(.carta-font-code) {
		font-family: monospace;
		font-size: 1.1rem;
	}
</style>
