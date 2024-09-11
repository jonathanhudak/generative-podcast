<script lang="ts">
	import { onMount } from 'svelte';
	import { Heading, Button, Label, Input, P } from 'flowbite-svelte';
	import { GradientButton } from 'flowbite-svelte'; // Import GradientButton
	import { BrainOutline, ArrowRightOutline } from 'flowbite-svelte-icons'; // Import BrainOutline icon
	import { Carta, MarkdownEditor } from 'carta-md';
	import 'carta-md/default.css'; /* Default theme */
	import { emoji } from '@cartamd/plugin-emoji';
	import { slash } from '@cartamd/plugin-slash';
	import { code } from '@cartamd/plugin-code';
	import DOMPurify from 'isomorphic-dompurify';

	let topic = '';
	let isLoading = false;
	let promptResult = '';
	let randomTopics: string[] = []; // Array to hold random topics

	const gradientColors = [
		'purpleToBlue',
		'cyanToBlue',
		'greenToBlue',
		'purpleToPink',
		'pinkToOrange',
		'tealToLime',
		'redToYellow'
	];
	function getRandomGradient() {
		return gradientColors[Math.floor(Math.random() * gradientColors.length)];
	}

	async function fetchRandomTopics() {
		try {
			const response = await fetch('http://127.0.0.1:5432/random_topics');
			const data = await response.json();
			randomTopics = data.topics; // Populate the random topics
		} catch (error) {
			console.error('Error fetching topics:', error);
		}
	}

	onMount(() => {
		fetchRandomTopics(); // Fetch topics when the component mounts
	});

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
		extensions: [emoji(), slash(), code()]
	});
</script>

<div class="grid-cols-2 gap-4 lg:grid">
	{#if !promptResult}
	<form on:submit|preventDefault={handleSubmit} class="flex max-w-md grow flex-col space-y-4">
		<div>
			<Label for="topic" class="mb-1 text-lg lg:text-xl dark:text-gray-400"
				>Enter a topic you have always been curious to learn about or choose one.</Label
			>
			<Input id="topic" placeholder="Enter prompt topic" bind:value={topic} required />
		</div>
		<Button type="submit" disabled={isLoading}>
			{#if isLoading}
				Creating Script Prompt...
			{:else}
				Create a Script Prompt
			{/if}

			<ArrowRightOutline class="ms-2 h-6 w-6" />
		</Button>
	</form>
	{/if}

	{#if randomTopics.length > 0 && !promptResult}
		<div class="flex flex-wrap gap-2">
			{#each randomTopics as randomTopic}
				<GradientButton color={getRandomGradient()} on:click={() => (topic = randomTopic)}>
					{randomTopic}
				</GradientButton>
			{/each}
			<GradientButton outline color="purpleToBlue" on:click={fetchRandomTopics}>
				Load more
			</GradientButton>
		</div>
	{/if}
</div>

{#if promptResult}
	<div class="mt-4 grid gap-2">
		<Heading tag="h2" class="mb-4" customSize="text-3xl font-extrabold">1. The Prompt</Heading>
		<Heading tag="h3" customSize="text-2xl font-extrabold">{topic}</Heading>
		<P>This prompt will be used to produce a script for your podcast. Edit it or leave it as-is.</P>
		<MarkdownEditor bind:value={promptResult} mode="tabs" theme="github" {carta} />
		<GradientButton outline color="purpleToBlue">Generate script</GradientButton>
	</div>
{/if}

<style>
	/* Set your monospace font (Required to have the editor working correctly!) */
	:global(.carta-font-code) {
		font-family: '...', monospace;
		font-size: 1.1rem;
	}
</style>
