<script lang="ts">
	import {
		Table,
		TableBody,
		TableBodyCell,
		TableBodyRow,
		TableHead,
		TableHeadCell
	} from 'flowbite-svelte';
	import type { PromptItem } from '$lib/types/api';
	export let promptsData: PromptItem[];

	// Function to create a link for each prompt
	function createPromptLink(prompt: PromptItem) {
		return {
			...prompt,
			link: `/resource/prompt/${prompt.id}`
		};
	}

	const linkedPromptsData = promptsData.map(createPromptLink);
</script>

<Table striped={true}>
	<TableHead>
		<TableHeadCell>Name</TableHeadCell>
		<TableHeadCell>ID</TableHeadCell>
		<TableHeadCell>Created At</TableHeadCell>
	</TableHead>
	<TableBody>
		{#each linkedPromptsData as prompt}
			<TableBodyRow>
				<TableBodyCell>
					<a href={prompt.link} class="text-blue-600 hover:underline">{prompt.name}</a>
				</TableBodyCell>
				<TableBodyCell>{prompt.id}</TableBodyCell>
				<!-- <TableBodyCell>{new Date(prompt.created_at).toLocaleString()}</TableBodyCell> -->
			</TableBodyRow>
		{/each}
	</TableBody>
</Table>
