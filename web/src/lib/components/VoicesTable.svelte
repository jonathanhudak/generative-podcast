<script lang="ts">
	import Table from '$lib/components/Table.svelte';
	export let voicesData;

	type Voice = {
		voice_id: string;
		name: string;
		id: string;
		// Add other properties as needed
	};

	let voices: Voice[] = voicesData; // Extract voices array from JSON
	let displayKeys: (keyof Voice)[] = ['name', 'voice_id']; // Specify which keys to display

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
