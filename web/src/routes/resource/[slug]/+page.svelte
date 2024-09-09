<script>
	export let data;
	import { page } from '$app/stores';
	import VoicesTable from '$lib/components/VoicesTable.svelte';
	import PromptsTable from '$lib/components/PromptsTable.svelte'; // New import
	import ScriptsTable from '$lib/components/ScriptsTable.svelte'; // New import
	import PodcastsTable from '$lib/components/PodcastsTable.svelte'; // New import
	import { Heading } from 'flowbite-svelte';
</script>

<div class="grid gap-4">
	<Heading tag="h1" class="px-4">{$page.params.slug}</Heading>

	{#if $page.params.slug === 'podcasts'}
		<PodcastsTable podcastsData={data.podcasts} />
	{:else if $page.params.slug === 'voices'}
		<VoicesTable voicesData={data.voices} />
	{:else if $page.params.slug === 'prompts'}
		<PromptsTable promptsData={data.prompts} />
	{:else if $page.params.slug === 'scripts'}
		<ScriptsTable scriptsData={data.scripts} />
	{:else}
		<p>This is a generic page</p>
	{/if}
</div>
