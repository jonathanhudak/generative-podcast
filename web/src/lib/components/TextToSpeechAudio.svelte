<script lang="ts">
	import { onMount } from 'svelte';

	export let voiceId: string;
	export let onAudioCreated: (audioBlob: Blob) => void;
	export let initialText: string = '';

	let audioUrl: string | null = null;
	let audioElement: HTMLAudioElement;
	let isLoading = false;
	let error: string | null = null;
	let text: string = initialText;
	let isEditing = !initialText;

	onMount(() => {
		if (initialText) {
			if (audioUrl) {
				audioElement.src = audioUrl;
				audioElement.load();
			} else {
				generateAudio();
			}
		}
	});

	async function generateAudio() {
		isLoading = true;
		error = null;

		try {
			const response = await fetch('http://localhost:5432/text_to_speech', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ voice_id: voiceId, text })
			});

			if (!response.ok) {
				throw new Error('Failed to generate audio');
			}

			const result = await response.json();
			const audioResponse = await fetch(`http://localhost:5432/audio/${result.podcast_filename}`);
			const audioBlob = await audioResponse.blob();

			audioUrl = URL.createObjectURL(audioBlob);
			onAudioCreated(audioBlob);
			isEditing = false;
		} catch (err: any) {
			error = err.message;
		} finally {
			isLoading = false;
		}
	}

	function handleSubmit(event: Event) {
		event.preventDefault();
		if (text.trim()) {
			generateAudio();
		}
	}

	function handleEdit() {
		isEditing = true;
	}
</script>

{#if isEditing}
	<form on:submit={handleSubmit}>
		<textarea bind:value={text} placeholder="Enter text for speech synthesis" rows="4" cols="50" />
		<button type="submit" disabled={isLoading || !text.trim()}>Generate Audio</button>
	</form>
{:else}
	<div>
		<audio bind:this={audioElement} src={audioUrl} controls>
			Your browser does not support the audio element.
		</audio>
		<button on:click={handleEdit}>Edit</button>
	</div>
{/if}

{#if isLoading}
	<p>Generating audio...</p>
{:else if error}
	<p>Error: {error}</p>
{/if}

<style>
	form {
		display: flex;
		flex-direction: column;
		gap: 10px;
		margin-bottom: 15px;
	}

	textarea {
		width: 100%;
		padding: 5px;
	}

	button {
		align-self: flex-start;
		padding: 5px 10px;
	}
</style>
