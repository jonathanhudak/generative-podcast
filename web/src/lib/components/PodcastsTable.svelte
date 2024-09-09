<script lang="ts">
	import Table from '$lib/components/Table.svelte'; // Import the Table component
	import type { PodcastItem } from '$lib/types/api';
	export let podcastsData: PodcastItem[];
</script>

<Table
	data={podcastsData.map((podcast) => ({ name: podcast.name, id: podcast.id }))}
	displayKeys={['name', 'id']}
	onAdd={() => {
		/* handle add action */
	}}
	onMassEdit={() => {
		/* handle mass edit action */
	}}
	onDeleteAll={() => {
		/* handle delete all action */
	}}
	onFilter={(searchTerm) => {
		/* handle filter action */
	}}
/>
