<script lang="ts" generics="T extends { name: string; id: string; }, X">
	import { onMount } from 'svelte';
	import {
		Table,
		TableBody,
		TableBodyCell,
		TableBodyRow,
		TableHead,
		TableHeadCell,
		TableSearch,
		Button,
		Dropdown,
		DropdownItem,
		Checkbox,
		ButtonGroup
	} from 'flowbite-svelte';
	import { createEventDispatcher } from 'svelte';

	import { Section } from 'flowbite-svelte-blocks';

	import {
		PlusOutline,
		ChevronDownOutline,
		FilterSolid,
		ChevronRightOutline,
		ChevronLeftOutline
	} from 'flowbite-svelte-icons';

	let divClass: string =
		'bg-white dark:bg-gray-800 relative shadow-md sm:rounded-lg overflow-hidden px-0';
	let innerDivClass: string =
		'flex flex-col md:flex-row items-center justify-between space-y-3 md:space-y-0 md:space-x-4 p-4';
	let searchClass: string = 'w-full md:w-1/2 relative';
	let svgDivClass: string = 'absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none';
	let classInput: string =
		'text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2  pl-10';

	export let data: T[] = [];
	export let onAdd: () => void;
	export let onMassEdit: () => void;
	export let onDeleteAll: () => void;
	export let onFilter: (searchTerm: string) => void; // Update to accept searchTerm
	export let displayKeys: (keyof T)[] = []; // New prop for keys to display

	const dispatch = createEventDispatcher<{ arrayItemClick: X }>();

	let currentPosition: number = 0;
	const itemsPerPage: number = 10;
	const showPage: number = 5;
	let totalPages: number = 0;
	let pagesToShow: number[] = [];
	let searchTerm: string = '';
	let totalItems: number = data.length;
	let startPage: number;
	let endPage: number;

	const updateDataAndPagination = (): void => {
		const currentPageItems = data.slice(currentPosition, currentPosition + itemsPerPage);
		renderPagination(currentPageItems.length);
	};

	const loadNextPage = (): void => {
		if (currentPosition + itemsPerPage < paginationData.length) {
			currentPosition += itemsPerPage;
			updateDataAndPagination();
		}
	};

	const loadPreviousPage = (): void => {
		if (currentPosition - itemsPerPage >= 0) {
			currentPosition -= itemsPerPage;
			updateDataAndPagination();
		}
	};

	const renderPagination = (totalItems: number): void => {
		totalPages = Math.ceil(paginationData.length / itemsPerPage);
		const currentPage: number = Math.ceil((currentPosition + 1) / itemsPerPage);

		startPage = currentPage - Math.floor(showPage / 2);
		startPage = Math.max(1, startPage);
		endPage = Math.min(startPage + showPage - 1, totalPages);

		pagesToShow = Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i);
	};

	const goToPage = (pageNumber: number): void => {
		currentPosition = (pageNumber - 1) * itemsPerPage;
		updateDataAndPagination();
	};

	$: startRange = currentPosition + 1;
	$: endRange = Math.min(currentPosition + itemsPerPage, totalItems);

	onMount((): void => {
		renderPagination(paginationData.length);
	});

	$: currentPageItems = data.slice(currentPosition, currentPosition + itemsPerPage);
	$: filteredItems = data.filter(
		(item: T) => item.name.toLowerCase().indexOf(searchTerm.toLowerCase()) !== -1
	);

	// Call onFilter when searchTerm changes
	$: onFilter(searchTerm);
</script>

<Section name="advancedTable" classSection="dark:bg-gray-900">
	<TableSearch
		placeholder="Search"
		hoverable={true}
		bind:inputValue={searchTerm}
		{divClass}
		{innerDivClass}
		{searchClass}
		{classInput}
	>
		<div
			slot="header"
			class="flex w-full flex-shrink-0 flex-col items-stretch justify-end space-y-2 md:w-auto md:flex-row md:items-center md:space-x-3 md:space-y-0"
		>
			<Button on:click={onAdd}>
				<PlusOutline class="mr-2 h-3.5 w-3.5" />Add
			</Button>
			<Button color="alternative">Actions<ChevronDownOutline class="ml-2 h-3 w-3 " /></Button>
			<Dropdown class="w-44 divide-y divide-gray-100">
				<DropdownItem on:click={onMassEdit}>Batch Edit</DropdownItem>
				<DropdownItem on:click={onDeleteAll}>Delete all</DropdownItem>
			</Dropdown>
			<Button color="alternative">Filter<FilterSolid class="ml-2 h-3 w-3 " /></Button>
			<Dropdown class="w-48 space-y-2 p-3 text-sm">
				<h6 class="mb-3 text-sm font-medium text-gray-900 dark:text-white">Choose brand</h6>
				<li>
					<Checkbox>Apple (56)</Checkbox>
				</li>
				<li>
					<Checkbox>Microsoft (16)</Checkbox>
				</li>
				<li>
					<Checkbox>Razor (49)</Checkbox>
				</li>
				<li>
					<Checkbox>Nikon (12)</Checkbox>
				</li>
				<li>
					<Checkbox>BenQ (74)</Checkbox>
				</li>
			</Dropdown>
		</div>
		<TableHead>
			{#each displayKeys as key}
				<TableHeadCell padding="px-4 py-3" scope="col">{key}</TableHeadCell>
			{/each}
		</TableHead>
		<TableBody tableBodyClass="divide-y">
			{#each filteredItems as item (item.id)}
				<TableBodyRow>
					{#each displayKeys as key}
						<TableBodyCell tdClass="px-4 py-3">{item[key]}</TableBodyCell>
					{/each}
				</TableBodyRow>
			{/each}
		</TableBody>
		<div
			slot="footer"
			class="flex flex-col items-start justify-between space-y-3 p-4 md:flex-row md:items-center md:space-y-0"
			aria-label="Table navigation"
		>
			<span class="text-sm font-normal text-gray-500 dark:text-gray-400">
				Showing
				<span class="font-semibold text-gray-900 dark:text-white">{startRange}-{endRange}</span>
				of
				<span class="font-semibold text-gray-900 dark:text-white">{totalItems}</span>
			</span>
			<ButtonGroup>
				<Button on:click={loadPreviousPage} disabled={currentPosition === 0}
					><ChevronLeftOutline size="xs" class="m-1.5" /></Button
				>
				{#each pagesToShow as pageNumber}
					<Button on:click={() => goToPage(pageNumber)}>{pageNumber}</Button>
				{/each}
				<Button on:click={loadNextPage} disabled={totalPages === endPage}
					><ChevronRightOutline size="xs" class="m-1.5" /></Button
				>
			</ButtonGroup>
		</div>
	</TableSearch>
</Section>
