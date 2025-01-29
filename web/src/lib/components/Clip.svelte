<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';

	export let id: number;
	export let start = 0;
	export let end = 10;
	export let trackWidth = 600;
	export let duration = 60;
	export let onContextMenu: (event: MouseEvent) => void;

	let clipWidth: number;
	let clipElement: HTMLDivElement;
	let isDragging = false;
	1;
	let isResizing = false;
	let initialX: number;
	let startX: number;
	let endX: number;
	let resizeDirection: 'left' | 'right' | null = null;

	const dispatch = createEventDispatcher<{
		update: { id: number; start: number; end: number };
		delete: { id: number };
	}>();

	const updateClipWidth = () => {
		clipWidth = ((end - start) / duration) * trackWidth;
	};

	onMount(updateClipWidth);

	const handleDragStart = (event: MouseEvent) => {
		isDragging = true;
		initialX = event.clientX;
		startX = start;
		endX = end;
	};

	const handleResizeStart = (event: MouseEvent, direction: 'left' | 'right') => {
		isResizing = true;
		initialX = event.clientX;
		resizeDirection = direction;
		startX = start;
		endX = end;
	};

	const handleMouseMove = (event: MouseEvent) => {
		if (isDragging) {
			const delta = (event.clientX - initialX) * (duration / trackWidth);
			start = Math.max(0, Math.min(duration - (end - start), startX + delta));
			end = start + (endX - startX);
		} else if (isResizing) {
			const delta = (event.clientX - initialX) * (duration / trackWidth);
			if (resizeDirection === 'left') {
				start = Math.max(0, Math.min(end - 1, startX + delta));
			} else {
				end = Math.max(start + 1, Math.min(duration, endX + delta));
			}
		}
		updateClipWidth();
	};

	const handleMouseUp = () => {
		if (isDragging || isResizing) {
			dispatch('update', { id, start, end });
		}
		isDragging = false;
		isResizing = false;
		resizeDirection = null;
	};

	const handleDelete = () => {
		dispatch('delete', { id });
	};
</script>

<div
	class="clip"
	bind:this={clipElement}
	role="button"
	tabindex="0"
	style="width: {clipWidth}px; left: {(start / duration) * trackWidth}px"
	on:mousedown={handleDragStart}
>
	<div
		class="resize-handle left"
		role="button"
		tabindex="0"
		on:mousedown|stopPropagation={(e) => handleResizeStart(e, 'left')}
	></div>
	<div class="clip-content" on:contextmenu={onContextMenu} role="menu" tabindex="0">
		<button class="delete-button" on:click|stopPropagation={handleDelete}>×</button>
	</div>
	<div
		class="resize-handle right"
		role="button"
		tabindex="0"
		on:mousedown|stopPropagation={(e) => handleResizeStart(e, 'right')}
	></div>
</div>

<svelte:window on:mousemove={handleMouseMove} on:mouseup={handleMouseUp} />

<style>
	.clip {
		position: absolute;
		height: 100%;
		background-color: #4caf50;
		cursor: grab;
		display: flex;
		align-items: stretch;
		justify-content: space-between;
	}

	.resize-handle {
		width: 5px;
		cursor: ew-resize;
		background-color: #333;
	}
</style>
