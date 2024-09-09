<script>
	import '../app.css';
	import ResourceMenu from '$lib/components/ResourceMenu.svelte';
</script>

<div class="gap-4 p-4 md:flex">
	<div>
		<ResourceMenu />
	</div>
	<div class="p-4">
		<slot></slot>
	</div>
</div>
