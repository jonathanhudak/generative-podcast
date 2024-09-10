<script lang="ts">
	import {
		Table,
		TableBody,
		TableBodyCell,
		TableBodyRow,
		TableHead,
		TableHeadCell
	} from 'flowbite-svelte';
	import type { PodcastItem } from '$lib/types/api';
	export let podcastsData: PodcastItem[];

	// Function to create a link for each podcast
	function createPodcastLink(podcast: PodcastItem) {
		return {
			...podcast,
			link: `/resource/podcast/${podcast.id}`
		};
	}

	const linkedPodcastsData = podcastsData.map(createPodcastLink);
</script>

<Table striped={true}>
	<TableHead>
		<TableHeadCell>Title</TableHeadCell>
		<TableHeadCell>ID</TableHeadCell>
		<TableHeadCell>Created At</TableHeadCell>
	</TableHead>
	<TableBody>
		{#each linkedPodcastsData as podcast}
			<TableBodyRow>
				<TableBodyCell>
					<a href={podcast.link} class="text-blue-600 hover:underline">{podcast.title}</a>
				</TableBodyCell>
				<TableBodyCell>{podcast.id}</TableBodyCell>
				<TableBodyCell>{new Date(podcast.created_at).toLocaleString()}</TableBodyCell>
			</TableBodyRow>
		{/each}
	</TableBody>
</Table>
