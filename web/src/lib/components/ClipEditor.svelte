<script lang="ts">
	import Clip from './Clip.svelte';
	import ContextMenu from './ContextMenu.svelte';
	import { createEventDispatcher, onMount } from 'svelte';
	import { ButtonGroup, Button } from 'flowbite-svelte';
	import { twMerge } from 'tailwind-merge';
	import type { HTMLInputAttributes } from 'svelte/elements';

	interface ClipData {
		id: number;
		start: number;
		end: number;
	}

	interface Track {
		id: number;
		type: 'audio' | 'midi';
		clips: ClipData[];
	}

	let tracks: Track[] = [];
	let nextTrackId = 1;
	let nextClipId = 1;

	const trackWidth = 1200;
	const duration = 60;

	let contextMenu: {
		show: boolean;
		x: number;
		y: number;
		type: 'editor' | 'track' | 'clip';
		trackId?: number;
		clipId?: number;
	} = { show: false, x: 0, y: 0, type: 'editor' };

	const dispatch = createEventDispatcher();

	let copiedClip: ClipData | null = null;

	let isPlaying = false;
	let currentTime = 0;
	let timelineInterval: number;

	let lastSpacebarPress = 0;
	const doubleTapThreshold = 300; // milliseconds

	onMount(() => {
		const animate = () => {
			if (isPlaying) {
				currentTime = (currentTime + 0.016) % duration; // 60 FPS
			}
			requestAnimationFrame(animate);
		};
		requestAnimationFrame(animate);

		window.addEventListener('keydown', handleKeydown);

		return () => {
			if (timelineInterval) clearInterval(timelineInterval);
			window.removeEventListener('keydown', handleKeydown);
		};
	});

	function togglePlayPause() {
		isPlaying = !isPlaying;
	}

	function stop() {
		isPlaying = false;
		clearInterval(timelineInterval);
	}

	function rewind() {
		currentTime = 0;
		if (isPlaying) {
			clearInterval(timelineInterval);
			timelineInterval = setInterval(() => {
				currentTime = (currentTime + 0.1) % duration;
			}, 100);
		}
	}

	interface RangeSliderProps extends Omit<HTMLInputAttributes, 'size'> {
		value?: number;
		size?: 'sm' | 'md' | 'lg';
	}

	let rangeSliderValue = currentTime;
	let rangeSliderSize: NonNullable<RangeSliderProps['size']> = 'md';

	const sizes = {
		sm: 'h-1 range-sm',
		md: 'h-2',
		lg: 'h-3 range-lg'
	};

	$: rangeSliderClass = twMerge(
		'w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700',
		sizes[rangeSliderSize] ?? sizes.md,
		'range-slider'
	);

	function updatePlayhead(event: Event) {
		currentTime = rangeSliderValue;
	}

	const addTrack = (type: 'audio' | 'midi') => {
		tracks = [...tracks, { id: nextTrackId++, type, clips: [] }];
		hideContextMenu();
	};

	const addClip = (trackId: number) => {
		const trackIndex = tracks.findIndex((track) => track.id === trackId);
		if (trackIndex !== -1) {
			const newClip: ClipData = {
				id: nextClipId++,
				start: 0,
				end: 10
			};
			tracks[trackIndex].clips = [...tracks[trackIndex].clips, newClip];
			tracks = [...tracks];
		}
		hideContextMenu();
	};

	const deleteClip = (trackId: number, clipId: number) => {
		const trackIndex = tracks.findIndex((track) => track.id === trackId);
		if (trackIndex !== -1) {
			tracks[trackIndex].clips = tracks[trackIndex].clips.filter((clip) => clip.id !== clipId);
			tracks = [...tracks];
		}
	};

	const updateClip = (trackId: number, event: CustomEvent<ClipData>) => {
		const trackIndex = tracks.findIndex((track) => track.id === trackId);
		if (trackIndex !== -1) {
			const updatedClip = event.detail;
			tracks[trackIndex].clips = tracks[trackIndex].clips.map((clip) =>
				clip.id === updatedClip.id ? updatedClip : clip
			);
			tracks = [...tracks];
		}
	};

	const duplicateClip = (trackId: number, clipId: number) => {
		const trackIndex = tracks.findIndex((track) => track.id === trackId);
		if (trackIndex !== -1) {
			const originalClip = tracks[trackIndex].clips.find((clip) => clip.id === clipId);
			if (originalClip) {
				const newClip: ClipData = {
					id: nextClipId++,
					start: originalClip.start,
					end: originalClip.end
				};
				tracks[trackIndex].clips = [...tracks[trackIndex].clips, newClip];
				tracks = [...tracks];
			}
		}
	};

	const copyClip = (trackId: number, clipId: number) => {
		const trackIndex = tracks.findIndex((track) => track.id === trackId);
		if (trackIndex !== -1) {
			const clipToCopy = tracks[trackIndex].clips.find((clip) => clip.id === clipId);
			if (clipToCopy) {
				copiedClip = { ...clipToCopy };
			}
		}
	};

	const pasteClip = (trackId: number) => {
		if (copiedClip) {
			const trackIndex = tracks.findIndex((track) => track.id === trackId);
			if (trackIndex !== -1) {
				const newClip: ClipData = {
					id: nextClipId++,
					start: copiedClip.start,
					end: copiedClip.end
				};
				tracks[trackIndex].clips = [...tracks[trackIndex].clips, newClip];
				tracks = [...tracks];
			}
		}
	};

	const showContextMenu = (
		event: MouseEvent,
		type: 'editor' | 'track' | 'clip',
		trackId?: number,
		clipId?: number
	) => {
		console.log('showContextMenu', type);
		event.preventDefault();
		event.stopPropagation();
		contextMenu = {
			show: true,
			x: event.clientX,
			y: event.clientY,
			type,
			trackId,
			clipId
		};
	};

	const hideContextMenu = () => {
		contextMenu = { show: false, x: 0, y: 0, type: 'editor' };
	};

	const handleContextMenuAction = (event: CustomEvent<string>) => {
		const action = event.detail;
		switch (action) {
			case 'addAudioTrack':
				addTrack('audio');
				break;
			case 'addMidiTrack':
				addTrack('midi');
				break;
			case 'addClip':
				if (contextMenu.trackId !== undefined) addClip(contextMenu.trackId);
				break;
			case 'duplicateClip':
				if (contextMenu.trackId !== undefined && contextMenu.clipId !== undefined) {
					duplicateClip(contextMenu.trackId, contextMenu.clipId);
				}
				break;
			case 'copyClip':
				if (contextMenu.trackId !== undefined && contextMenu.clipId !== undefined) {
					copyClip(contextMenu.trackId, contextMenu.clipId);
				}
				break;
			case 'pasteClip':
				if (contextMenu.trackId !== undefined) {
					pasteClip(contextMenu.trackId);
				}
				break;
			case 'deleteClip':
				if (contextMenu.trackId !== undefined && contextMenu.clipId !== undefined) {
					deleteClip(contextMenu.trackId, contextMenu.clipId);
				}
				break;
		}
		hideContextMenu();
	};

	const handleClickOutside = (event: MouseEvent) => {
		if (contextMenu.show && !(event.target as Element).closest('.context-menu')) {
			hideContextMenu();
		}
	};

	function getContextMenuItems() {
		switch (contextMenu.type) {
			case 'editor':
				return [
					{ label: 'Add Audio Track', action: 'addAudioTrack' },
					{ label: 'Add MIDI Track', action: 'addMidiTrack' }
				];
			case 'track':
				return [{ label: 'Add Clip', action: 'addClip' }];
			case 'clip':
				return [
					{ label: 'Duplicate Clip', action: 'duplicateClip' },
					{ label: 'Copy Clip', action: 'copyClip' },
					{ label: 'Paste Clip', action: 'pasteClip' },
					{ label: 'Delete Clip', action: 'deleteClip' }
				];
			default:
				return [];
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.code === 'Space' && !event.repeat) {
			event.preventDefault();
			const now = Date.now();
			if (now - lastSpacebarPress < doubleTapThreshold) {
				// Double tap detected
				currentTime = 0;
				if (!isPlaying) {
					togglePlayPause();
				}
			} else {
				togglePlayPause();
			}
			lastSpacebarPress = now;
		}
	}
</script>

<svelte:window on:click={handleClickOutside} />

<div class="relative">
	<ButtonGroup class="*:!ring-primary-700">
		<Button on:click={rewind}>&#171;</Button>
		<Button on:click={togglePlayPause}>{isPlaying ? 'Pause' : 'Play'}</Button>
		<Button on:click={stop}>Stop</Button>
	</ButtonGroup>
	<div class="timeline">
		<div class="playhead" style="left: {(currentTime / duration) * 100}%"></div>
		<input
			type="range"
			bind:value={rangeSliderValue}
			min="0"
			max={duration}
			step="0.1"
			class={rangeSliderClass}
			on:input={updatePlayhead}
			on:change={updatePlayhead}
		/>
	</div>
</div>

<div class="clip-editor" role="application" on:contextmenu={(e) => showContextMenu(e, 'editor')}>
	{#each tracks as track (track.id)}
		<div
			class="track"
			style="width: {trackWidth}px;"
			role="menu"
			on:contextmenu={(e) => showContextMenu(e, 'track', track.id)}
		>
			<span class="track-label">{track.type.toUpperCase()}</span>
			{#each track.clips as clip (clip.id)}
				<Clip
					id={clip.id}
					start={clip.start}
					end={clip.end}
					{trackWidth}
					{duration}
					onContextMenu={(e) => showContextMenu(e, 'clip', track.id, clip.id)}
					on:delete={() => deleteClip(track.id, clip.id)}
					on:update={(e) => updateClip(track.id, e)}
				/>
			{/each}
		</div>
	{/each}
	{#if contextMenu.show}
		<ContextMenu
			x={contextMenu.x}
			y={contextMenu.y}
			items={getContextMenuItems()}
			on:action={handleContextMenuAction}
		/>
	{/if}
</div>

<style>
	.clip-editor {
		position: relative;
		width: 100%;
		overflow-x: scroll;
		background-color: #ddd;
		padding: 20px;
		border: 1px solid #aaa;
	}

	.track {
		position: relative;
		height: 50px;
		background-color: aqua;
		margin-bottom: 5px;
	}

	.track-label {
		position: absolute;
		left: 5px;
		top: 5px;
		font-size: 12px;
		color: #666;
	}

	.context-menu {
		position: fixed;
		background-color: white;
		border: 1px solid #ccc;
		box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
		z-index: 1000;
	}

	.timeline {
		position: relative;
		width: 100%;
		padding: 10px 0;
	}

	.playhead {
		position: fixed;
		top: 0;
		bottom: 0;
		left: 0;
		width: 2px;
		background-color: rgba(255, 0, 0, 0.5);
		z-index: 1000;
		pointer-events: none;
		transition: left 0.016s linear;
	}

	.range-slider {
		position: absolute;
		width: 100%;
		top: 50%;
		transform: translateY(-50%);
		z-index: 1;
	}

	.controls button {
		margin-right: 5px;
	}

	.relative {
		position: relative;
	}
</style>
