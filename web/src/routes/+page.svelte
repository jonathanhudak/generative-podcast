<script lang="ts">
	import CreatePodcastWizard from '$lib/components/CreatePodcastWizard.svelte';
	import { Heading, P, Button } from 'flowbite-svelte';
</script>

<main>
	<Heading tag="h1" class="mb-4" customSize="text-4xl font-extrabold  md:text-5xl lg:text-6xl"
		>Generate a podcast</Heading
	>

	<CreatePodcastWizard />
</main>
