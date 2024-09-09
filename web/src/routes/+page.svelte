<script>
	import { Alert } from 'flowbite-svelte';
	import SvelteMarkdown from 'svelte-markdown';
</script>

<main>
	<SvelteMarkdown
		source={`
  # A Podcast Generator

Have an idea for a short podcast you would like to hear? Type your idea to generate a podcast script and produce your own audio podcast. Choose from a variety of quality voices.
`}
	/>
	<Alert color="blue">
		<span class="font-medium">Work in progress!</span>
	</Alert>
</main>
