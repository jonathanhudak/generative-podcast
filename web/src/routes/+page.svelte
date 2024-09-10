<script lang="ts">
	import CreatePrompt from '$lib/components/CreatePrompt.svelte';
	import { Alert } from 'flowbite-svelte';
	import SvelteMarkdown from 'svelte-markdown';
</script>

<main>
	<h1>Generate Podcast Prompt</h1>
	<SvelteMarkdown
		source={`
  # Podcast Generator

Have an idea for a short podcast you would like to hear? Type your idea to generate a podcast script and produce your own audio podcast. Choose from a variety of quality voices.
`}
	/>
	<CreatePrompt />
</main>
