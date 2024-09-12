<script lang="ts">
	import { onMount } from 'svelte';
	import type { Voice } from '$lib/types/Voices';
	import { Heading, Button, Label, Input, P, Select, GradientButton } from 'flowbite-svelte';
	import { MarkdownEditor } from 'carta-md'; // Ensure MarkdownEditor is imported

	let topic = '';
	let prompt = '';
	let script = '';
	let voices: Voice[] = [];
	let selectedVoiceId: string | null = null;
	let isLoading = false;
	let podcastUrl = '';
	let randomTopics: string[] = []; // Array to hold random topics
	let step = 0; // Track the current step in the wizard
	let podcastTitle = '';
	let waiting = false;
	let stepsSeen = [0];

	console.log('stepsSeen', stepsSeen);

	$: (() => {
		step; // when step changes
		if (!stepsSeen.includes(step)) {
			stepsSeen.push(step);
			console.log('add new step', stepsSeen);
		}
	})();

	const gradientColors = [
		'purpleToBlue',
		'cyanToBlue',
		'greenToBlue',
		'purpleToPink',
		'pinkToOrange',
		'tealToLime',
		'redToYellow'
	];
	type GradientColor =
		| 'purpleToBlue'
		| 'cyanToBlue'
		| 'greenToBlue'
		| 'purpleToPink'
		| 'pinkToOrange'
		| 'tealToLime'
		| 'redToYellow';
	function getRandomGradient(): GradientColor {
		return gradientColors[Math.floor(Math.random() * gradientColors.length)] as GradientColor;
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

	async function fetchVoices() {
		const response = await fetch('http://127.0.0.1:5432/voices');
		if (response.ok) {
			const data = await response.json();
			voices = data.voices; // Populate the voices array
		} else {
			console.error('Failed to fetch voices');
		}
	}

	async function handleCreatePodcast() {
		if (!selectedVoiceId || !script) return;

		isLoading = true; // Set loading state
		const response = await fetch('http://127.0.0.1:5432/create_podcast', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				title: podcastTitle,
				script,
				voice_id: selectedVoiceId
			})
		});

		if (response.ok) {
			const data = await response.json();
			podcastUrl = `http://127.0.0.1:5432/audio/${data.podcast_filename}`; // Adjust based on your API response
			step = 4;
		} else {
			console.error('Failed to create podcast');
		}

		isLoading = false; // Reset loading state
	}

	async function handleGenerateScript() {
		step = 2;
		waiting = true;
		// Call the API to create the script based on the prompt
		const response = await fetch('http://127.0.0.1:5432/generate_script', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ prompt, topic }) // Send the prompt result to generate the script
		});

		if (response.ok && response.body?.getReader) {
			const reader = response.body.getReader();
			const decoder = new TextDecoder('utf-8');
			let done = false;

			while (!done) {
				const { value, done: streamDone } = await reader.read();
				done = streamDone;
				script += decoder.decode(value, { stream: true });
				// Process the streamed text as needed
			}
		} else {
			console.error('Failed to generate script:', response.statusText);
		}

		waiting = false;
	}

	function selectRandomTopic(randomTopic: string) {
		topic = randomTopic; // Set the selected random topic
	}

	async function createPrompt() {
		podcastTitle = topic;
		step = 1;
		waiting = true;

		// Logic to create prompt and script
		const response = await fetch('http://127.0.0.1:5432/create_prompt', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ topic }) // Send the topic to create a prompt
		});

		if (response.ok && response.body?.getReader) {
			const reader = response.body.getReader();
			const decoder = new TextDecoder('utf-8');
			let done = false;

			while (!done) {
				const { value, done: streamDone } = await reader.read();
				done = streamDone;
				prompt += decoder.decode(value, { stream: true });
			}
		} else {
			console.error('Failed to create prompt');
		}

		waiting = false;
	}

	onMount(() => {
		fetchRandomTopics(); // Fetch topics when the component mounts
		fetchVoices(); // Fetch voices when the component mounts
	});
</script>

<div class="">
	{#if step === 0 || stepsSeen.includes(0)}
		{#if step !== 0}
			<Heading tag="h2" class="mb-4" customSize="text-3xl font-extrabold">1. Topic {topic}</Heading>
		{:else}
			<!-- Step 1: Select Random Topic or Enter Topic -->
			<div>
				<Heading tag="h2" class="mb-4" customSize="text-3xl font-extrabold">1. Topic</Heading>
				<div class="grid-cols-2 gap-4 lg:grid">
					<form
						on:submit|preventDefault={createPrompt}
						class="mt-4 flex max-w-md grow grow flex-col space-y-4"
					>
						<div>
							<Label for="topic" class="mb-1 text-lg lg:text-xl dark:text-gray-400"
								>Enter a great podcast topic or choose one</Label
							>
							<Input id="topic" placeholder="Enter prompt topic" bind:value={topic} required />
						</div>
						<GradientButton
							outline
							color="purpleToBlue"
							type="submit"
							disabled={isLoading}
							class="w-fit"
						>
							{#if isLoading}
								Creating Script Prompt...
							{:else}
								Create a Script Prompt
							{/if}
						</GradientButton>
					</form>
					<div class="flex flex-wrap gap-2">
						{#each randomTopics as randomTopic}
							<GradientButton
								color={getRandomGradient()}
								on:click={() => selectRandomTopic(randomTopic)}>{randomTopic}</GradientButton
							>
						{/each}

						<GradientButton outline on:click={fetchRandomTopics}>Load more</GradientButton>
					</div>
				</div>
			</div>
		{/if}
	{/if}

	{#if step === 1 || stepsSeen.includes(1)}
		<!-- Step 2: Show Prompt and Script -->
		<div class="grid gap-4">
			<div>
				<Heading tag="h2" class="mb-4" customSize="text-3xl font-extrabold"
					>2. The Script Prompt</Heading
				>
				<P>This prompt will be used to generate a script for your podcast.</P>
			</div>
			<P>{prompt}</P>
			{#if !waiting && step === 1}
				<div>
					<GradientButton outline color="purpleToBlue" on:click={handleGenerateScript} class="w-fit"
						>Generate script</GradientButton
					>
				</div>
			{/if}
		</div>
	{/if}

	{#if step === 2 || stepsSeen.includes(2)}
		<div class="">
			<Heading tag="h2" class="mb-4" customSize="text-3xl font-extrabold">3. The Script</Heading>
			<P>{script}</P>
			{#if !waiting && step === 2}
				<div>
					<GradientButton outline color="purpleToBlue" on:click={() => (step = 3)} class="w-fit"
						>Let's turn this script into a podcast</GradientButton
					>
				</div>
			{/if}
		</div>
	{/if}

	{#if step === 3}
		<div class="">
			<Label for="podcastTitle" class="mb-1 text-lg lg:text-xl dark:text-gray-400"
				>Podcast Title:</Label
			>
			<Input id="podcastTitle" bind:value={podcastTitle} placeholder="Enter podcast title" />
			<Label for="voiceSelect" class="mb-1 text-lg lg:text-xl dark:text-gray-400"
				>Select a voice:</Label
			>
			<Select id="voiceSelect" bind:value={selectedVoiceId}>
				{#each voices as voice}
					<option value={voice.voice_id}>{voice.name}</option>
				{/each}
			</Select>
			<div>
				<GradientButton
					outline
					class="w-fit"
					color="purpleToBlue"
					on:click={handleCreatePodcast}
					disabled={isLoading || !selectedVoiceId}
				>
					{#if isLoading}
						Creating Podcast...
					{:else}
						Create Podcast
					{/if}
				</GradientButton>
			</div>
		</div>
	{/if}

	{#if podcastUrl && step === 4}
		<!-- Step 4: Play Podcast -->
		<div class="mt-4">
			<Heading tag="h2" class="mb-4" customSize="text-3xl font-extrabold"
				>4. Your Podcast: {podcastTitle}</Heading
			>
			<audio controls>
				<source src={podcastUrl} type="audio/mpeg" />
				Your browser does not support the audio element.
			</audio>
		</div>
	{/if}
</div>

<style>
	/* Add any additional styles here */
</style>
