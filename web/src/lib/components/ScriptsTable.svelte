<script lang="ts">
	import {
		Table,
		TableBody,
		TableBodyCell,
		TableBodyRow,
		TableHead,
		TableHeadCell
	} from 'flowbite-svelte';
	import type { ScriptItem } from '$lib/types/api';
	export let scriptsData: ScriptItem[];

	// Function to create a link for each prompt
	function createScriptLink(prompt: ScriptItem) {
		return {
			...prompt,
			link: `/resource/script/${prompt.id}`
		};
	}

	const linkedScriptsData = scriptsData.map(createScriptLink);
</script>

<Table striped={true}>
	<TableHead>
		<TableHeadCell>Name</TableHeadCell>
		<TableHeadCell>ID</TableHeadCell>
		<TableHeadCell>Created At</TableHeadCell>
	</TableHead>
	<TableBody>
		{#each linkedScriptsData as script}
			<TableBodyRow>
				<TableBodyCell>
					<a href={script.link} class="text-blue-600 hover:underline">{script.name}</a>
				</TableBodyCell>
				<TableBodyCell>{script.id}</TableBodyCell>
				<!-- <TableBodyCell>{new Date(prompt.created_at).toLocaleString()}</TableBodyCell> -->
			</TableBodyRow>
		{/each}
	</TableBody>
</Table>
