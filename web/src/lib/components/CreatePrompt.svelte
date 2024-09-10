<script lang="ts">
	import { onMount } from 'svelte';
	import { Button, Label, Input } from 'flowbite-svelte';
	import { Carta, MarkdownEditor } from 'carta-md';
	import 'carta-md/default.css'; /* Default theme */
	import { emoji } from '@cartamd/plugin-emoji';
	import { slash } from '@cartamd/plugin-slash';
	import { code } from '@cartamd/plugin-code';
	import DOMPurify from 'isomorphic-dompurify';

	let topic = '';
	let isLoading = false;
	let promptResult = '';
	let value = promptResult;

	async function handleSubmit() {
		isLoading = true;
		promptResult = '';
		try {
			const response = await fetch('http://127.0.0.1:5432/create_prompt', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ topic })
			});

			if (response.ok) {
				const reader = response.body?.getReader();
				const decoder = new TextDecoder();

				while (reader?.read) {
					const { done, value } = await reader?.read();
					if (done) break;
					promptResult += decoder.decode(value);
				}
			} else {
				console.error('Failed to create prompt');
			}
		} catch (error) {
			console.error('Error:', error);
		} finally {
			isLoading = false;
		}
	}

	const carta = new Carta({
		sanitizer: DOMPurify.sanitize,
		extensions: [
			// attachment({
			// 	async upload() {
			// 		return 'some-url-from-server.xyz';
			// 	}
			// }),
			emoji(),
			slash(),
			code()
		]
	});
</script>

<form on:submit|preventDefault={handleSubmit} class="flex flex-col space-y-4">
	<div>
		<Label for="topic" class="mb-2">Prompt Topic</Label>
		<Input id="topic" placeholder="Enter prompt topic" bind:value={topic} required />
	</div>
	<Button type="submit" disabled={isLoading}>
		{#if isLoading}
			Creating Prompt...
		{:else}
			Create Prompt
		{/if}
	</Button>
</form>

{#if promptResult}
	<div class="mt-4">
		<h3 class="mb-2 text-lg font-semibold">Generated Prompt:</h3>
		<p class="whitespace-pre-wrap">{promptResult}</p>
		<MarkdownEditor bind:value={promptResult} mode="tabs" theme="github" {carta} />
	</div>
{/if}

<style>
	/* Set your monospace font (Required to have the editor working correctly!) */
	:global(.carta-font-code) {
		font-family: '...', monospace;
		font-size: 1.1rem;
	}
</style>
