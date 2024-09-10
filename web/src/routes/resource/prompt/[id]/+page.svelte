<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { Carta, MarkdownEditor } from 'carta-md';
	import 'carta-md/default.css';
	import { emoji } from '@cartamd/plugin-emoji';
	import { slash } from '@cartamd/plugin-slash';
	import { code } from '@cartamd/plugin-code';
	import DOMPurify from 'isomorphic-dompurify';
	import { Heading } from 'flowbite-svelte';
	let promptContent = '';
	let isLoading = true;

	const carta = new Carta({
		sanitizer: DOMPurify.sanitize,
		extensions: [emoji(), slash(), code()]
	});

	onMount(async () => {
		const promptId = $page.params.id;
		try {
			const response = await fetch(`http://127.0.0.1:5432/prompts/${promptId}`);
			if (response.ok) {
				console.log('promptContent', promptContent);
				promptContent = await response.text();
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
				body: JSON.stringify({ content: promptContent })
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
	<Heading tag="h1" class="py-4">Edit Prompt</Heading>
	{#if isLoading}
		<p>Loading prompt...</p>
	{:else}
		<MarkdownEditor bind:value={promptContent} mode="tabs" theme="github" {carta} />
		<button on:click={handleSave}>Save Changes</button>
	{/if}
</main>

<style>
	:global(.carta-font-code) {
		font-family: monospace;
		font-size: 1.1rem;
	}
</style>
