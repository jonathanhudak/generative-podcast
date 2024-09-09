<script lang="ts">
	import Table from '$lib/components/Table.svelte';
	import type { Voice } from '$lib/types/Voices';
	export let voicesData: Voice[];
	let voices: Voice[] = voicesData;
	let displayKeys: (keyof Voice)[] = ['name', 'voice_id']; // Specify which keys to display
	type T = $$Generic<{ scripts: typeof voicesData }>;
	const handleAdd = () => {
		// Logic for adding a new voice
	};

	const handleMassEdit = () => {
		// Logic for mass editing voices
	};

	const handleDeleteAll = () => {
		// Logic for deleting all voices
	};

	const handleFilter = (searchTerm: string) => {
		// Logic for filtering voices based on searchTerm
		console.log('Filtering voices with term:', searchTerm);
	};
</script>

<Table
	data={voices.map((voice) => ({
		...voice,
		id: voice.voice_id
	}))}
	onAdd={handleAdd}
	onMassEdit={handleMassEdit}
	onDeleteAll={handleDeleteAll}
	onFilter={handleFilter}
	{displayKeys}
/>
