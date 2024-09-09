<script lang="ts">
	import Table from '$lib/components/Table.svelte'; // Import the Table component
	import type { PromptItem } from '$lib/types/api';
	export let promptsData: PromptItem[];
	type T = $$Generic<PromptItem[]>;
</script>

<Table
	data={promptsData.map((prompt) => ({ name: prompt.name, id: prompt.id }))}
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
