<script lang="ts">
	import { onMount } from 'svelte';
	import { v4 as uuidv4 } from 'uuid';
	import TextToSpeechAudio from '$lib/components/TextToSpeechAudio.svelte';

	let audioContext: AudioContext;
	interface Track {
		id: string;
		file: string;
		startTime: number;
		duration: number;
		isTextToSpeech: boolean;
		text?: string;
	}
	let tracks: Track[] = [];
	let timelineName = '';
	let audioBuffers: { [key: string]: AudioBuffer } = {};
	let isPlaying = false;
	let currentTime = 0;
	let duration = 0;
	let showNewTrackOptions = false;

	onMount(() => {
		audioContext = new window.AudioContext();
	});

	async function handleFileUpload(event: Event) {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];
		if (file) {
			const arrayBuffer = await file.arrayBuffer();
			const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
			const trackId = uuidv4();
			audioBuffers[trackId] = audioBuffer;
			tracks = [
				...tracks,
				{
					id: trackId,
					file: file.name,
					startTime: 0,
					duration: audioBuffer.duration,
					isTextToSpeech: false
				}
			];
			updateDuration();
		}
	}

	function updateDuration() {
		duration = Math.max(...tracks.map((track) => track.startTime + track.duration), 0);
	}

	function handleTrackStartTimeChange(trackId: string, newStartTime: number) {
		tracks = tracks.map((track) =>
			track.id === trackId ? { ...track, startTime: parseFloat(newStartTime.toString()) } : track
		);
		updateDuration();
	}

	async function playTimeline() {
		if (isPlaying) return;
		isPlaying = true;
		currentTime = 0;

		const startTime = audioContext.currentTime;
		tracks.forEach((track) => {
			const source = audioContext.createBufferSource();
			source.buffer = audioBuffers[track.id];
			source.connect(audioContext.destination);
			source.start(startTime + track.startTime);
		});

		while (isPlaying && currentTime < duration) {
			currentTime = audioContext.currentTime - startTime;
			await new Promise((resolve) => setTimeout(resolve, 100));
		}

		isPlaying = false;
	}

	function stopTimeline() {
		isPlaying = false;
		audioContext.close();
		audioContext = new window.AudioContext();
	}

	async function saveTimeline() {
		const response = await fetch('http://localhost:5432/audio-timelines', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				name: timelineName,
				tracks: tracks
			})
		});

		if (response.ok) {
			const result = await response.json();
			console.log('Timeline saved:', result);
			alert('Timeline saved successfully!');
		} else {
			console.error('Failed to save timeline');
			alert('Failed to save timeline');
		}
	}

	function addTextToSpeechTrack() {
		const trackId = uuidv4();
		tracks = [
			...tracks,
			{
				id: trackId,
				file: 'Text to Speech',
				startTime: 0,
				duration: 0,
				isTextToSpeech: true,
				text: ''
			}
		];
		showNewTrackOptions = false;
	}

	function addEmptyTrack() {
		const trackId = uuidv4();
		tracks = [
			...tracks,
			{ id: trackId, file: 'Empty Track', startTime: 0, duration: 0, isTextToSpeech: false }
		];
		showNewTrackOptions = false;
	}

	function handleAudioCreated(trackId: string, audioBlob: Blob) {
		const url = URL.createObjectURL(audioBlob);
		const audio = new Audio(url);
		audio.addEventListener('loadedmetadata', () => {
			tracks = tracks.map((track) =>
				track.id === trackId ? { ...track, duration: audio.duration } : track
			);
			updateDuration();
		});

		// Convert Blob to ArrayBuffer
		audioBlob.arrayBuffer().then((arrayBuffer) => {
			audioContext.decodeAudioData(arrayBuffer).then((decodedData) => {
				audioBuffers[trackId] = decodedData;
			});
		});
	}

	function toggleNewTrackOptions() {
		showNewTrackOptions = !showNewTrackOptions;
	}
</script>

<div class="audio-timeline-editor">
	<h2>Audio Timeline Editor</h2>
	<input type="text" bind:value={timelineName} placeholder="Timeline Name" />
	<button on:click={toggleNewTrackOptions}>Add New Track</button>
	{#if showNewTrackOptions}
		<div class="new-track-options">
			<button on:click={addEmptyTrack}>Add Empty Track</button>
			<button on:click={addTextToSpeechTrack}>Add Text-to-Speech Track</button>
			<input type="file" accept="audio/*" on:change={handleFileUpload} />
		</div>
	{/if}
	<button on:click={playTimeline} disabled={isPlaying}>Play</button>
	<button on:click={stopTimeline} disabled={!isPlaying}>Stop</button>
	<button on:click={saveTimeline}>Save Timeline</button>

	<div class="timeline">
		{#each tracks as track (track.id)}
			<div class="track">
				{#if track.isTextToSpeech}
					<TextToSpeechAudio
						voiceId="EXAVITQu4vr4xnSDxMaL"
						onAudioCreated={(audioBlob) => handleAudioCreated(track.id, audioBlob)}
						initialText={track.text}
					/>
				{:else}
					<span>{track.file}</span>
				{/if}
				<input
					type="number"
					min="0"
					step="0.1"
					bind:value={track.startTime}
					on:input={() => handleTrackStartTimeChange(track.id, track.startTime)}
				/>
				<div
					class="track-visual"
					style="left: {(track.startTime / duration) * 100}%; width: {(track.duration / duration) *
						100}%;"
				></div>
			</div>
		{/each}
	</div>

	<div class="playhead" style="left: {(currentTime / duration) * 100}%"></div>
</div>

<style>
	.audio-timeline-editor {
		width: 100%;
		max-width: 800px;
		margin: 0 auto;
		padding: 20px;
		position: relative;
	}

	.timeline {
		position: relative;
		height: 200px;
		border: 1px solid #ccc;
		margin-top: 20px;
	}

	.track {
		position: relative;
		height: 30px;
		margin-bottom: 10px;
	}

	.track-visual {
		position: absolute;
		height: 100%;
		background-color: #3498db;
		opacity: 0.7;
	}

	.playhead {
		position: absolute;
		top: 0;
		width: 2px;
		height: 100%;
		background-color: red;
		pointer-events: none;
	}

	.new-track-options {
		margin-top: 10px;
		display: flex;
		gap: 10px;
	}
</style>
