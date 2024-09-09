<script>
	import { Listgroup } from 'flowbite-svelte';
	let links = [
		{ name: 'Podcasts', href: '/resource/podcasts', current: true },
		{ name: 'Prompts', href: '/resource/prompts' },
		{ name: 'Scripts', href: '/resource/scripts' },
		{ name: 'Voices', href: '/resource/voices' }
	];
</script>

<Listgroup active items={links} let:index class="w-48">
	{links[index].name}
</Listgroup>
