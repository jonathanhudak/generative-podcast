<script>
	import { Listgroup } from 'flowbite-svelte';

	let links = [
		{ name: 'Home', href: '/' },
		{ name: 'Podcasts', href: '/resource/podcasts' },
		{ name: 'Prompts', href: '/resource/prompts' },
		{ name: 'Scripts', href: '/resource/scripts' },
		{ name: 'Voices', href: '/resource/voices' }
	];

	import { page } from '$app/stores';
	import { Sidebar, SidebarGroup, SidebarItem, SidebarWrapper } from 'flowbite-svelte';
	$: activeUrl = $page.url.pathname;
</script>

<Sidebar {activeUrl}>
	<SidebarWrapper>
		<SidebarGroup>
			<SidebarItem label="Home" href="/"></SidebarItem>
			<SidebarItem label="Podcasts" href="/resource/podcasts"></SidebarItem>
			<SidebarItem label="Prompts" href="/resource/prompts"></SidebarItem>
			<SidebarItem label="Scripts" href="/resource/scripts"></SidebarItem>
			<SidebarItem label="Voices" href="/resource/voices"></SidebarItem>
			<SidebarItem label="Audio Timelines" href="/resource/audio-timeline"></SidebarItem>
		</SidebarGroup>
	</SidebarWrapper>
</Sidebar>
