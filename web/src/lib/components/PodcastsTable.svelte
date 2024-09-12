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
		<TableHeadCell>ID</TableHeadCell>
		<!-- <TableHeadCell>Created At</TableHeadCell> -->
		<TableHeadCell>Audio</TableHeadCell>
		<!-- New column for audio -->
	</TableHead>
	<TableBody>
		{#each linkedPodcastsData as podcast}
			<TableBodyRow>
				<TableBodyCell>{podcast.id}</TableBodyCell>
				<!-- <TableBodyCell>{new Date(podcast.created_at).toLocaleString()}</TableBodyCell> -->
				<TableBodyCell>
					<audio controls>
						<source src={`http://127.0.0.1:5432/audio/${podcast.id}`} type="audio/mpeg" />
						Your browser does not support the audio element.
					</audio>
				</TableBodyCell>
				<!-- New audio element -->
			</TableBodyRow>
		{/each}
	</TableBody>
</Table>
