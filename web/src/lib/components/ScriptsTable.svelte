<script lang="ts">
	import Table from '$lib/components/Table.svelte'; // Import the Table component
	import type { ScriptItem } from '$lib/types/api';

	export let scriptsData: ScriptItem[];

	let displayKeys: (keyof ScriptItem)[] = ['name', 'id']; // Specify which keys to display

	type T = $$Generic<{ scripts: Script[] }>;
</script>

<Table
	data={scriptsData.map((script) => ({ name: script.name, id: script.id }))}
	{displayKeys}
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
