<script lang="ts">
	import { Paginator, type SvelteEvent } from '@skeletonlabs/skeleton';
	import { DataHandler, Th, ThFilter, type Row } from '@vincjo/datatables';
	import { createEventDispatcher } from 'svelte';
	import type { Readable } from 'svelte/store';
	import { columnDef, type Column } from './types';

	// Event Dispatcher
	type TableEvent = {
		selected: Row;
	};
	const dispatch = createEventDispatcher<TableEvent>();

	let tableElement: HTMLElement | undefined;

	export let data: Readable<Array<Row>>;
	export let columns: Array<Column> | undefined = undefined;
	export let filterable: boolean = false;
	export let rowsPerPage: number = 20;

	export let search = true;
	export let pagination = true;

	let searchValue = '';

	if (columns == undefined) {
		columns = Object.keys($data[0]).map((key) => columnDef(key, key));
	}

	let page = {
		page: 0,
		limit: rowsPerPage,
		size: $data.length,
		amounts: [5, 10, 20, 50, 100]
	};

	const handler = new DataHandler($data, { rowsPerPage: rowsPerPage });

	handler.on('change', () => {
		if (tableElement) tableElement.scrollTop = 0;
	});

	handler.on('clearSearch', () => (searchValue = ''));

	$: $data, update();
	let rows = handler.getRows();
	let rpp = handler.getRowsPerPage();

	const update = () => {
		if (tableElement && tableElement.parentElement) {
			const scrollTop = tableElement.parentElement.scrollTop;
			handler.setRows($data);
			setTimeout(() => {
				if (tableElement?.parentElement) {
					tableElement.parentElement.scrollTop = scrollTop;
				}
			}, 2);
		}
	};

	function onRowClick(
		event: SvelteEvent<MouseEvent | KeyboardEvent, HTMLTableRowElement>,
		rowIndex: number
	): void {
		// ignore events not hitting a td, buttons etc. should handle their own events
		if (event.target instanceof Element && event.target.tagName != 'TD') {
			return;
		}
		event.preventDefault();
		event.stopPropagation();
		const rowMetaData = $data[rowIndex];
		/** @event {rowMetaData} selected - Fires when a table row is clicked. */
		dispatch('selected', rowMetaData);
	}

	// Row Keydown Handler
	function onRowKeydown(
		event: SvelteEvent<KeyboardEvent, HTMLTableRowElement>,
		rowIndex: number
	): void {
		if (['Enter', 'Space'].includes(event.code)) onRowClick(event, rowIndex);
	}

	function pageChange(e: CustomEvent<Number>) {
		// skeleton paginator starts at 0, datatables at 1 so we have to add 1
		// on every page change to get the correct one.
		handler.setPage(e.detail.valueOf() + 1);
	}

	function rowsPerPageChange(e: CustomEvent<Number>) {
		rpp.set(e.detail.valueOf());
	}
</script>

<section class="space-y-2">
	<header>
		{#if search}
			<input
				class="input"
				style="max-width: 30ch"
				bind:value={searchValue}
				placeholder={handler.i18n.search}
				spellcheck="false"
				on:input={() => handler.search(searchValue)}
			/>
		{/if}
	</header>

	<div class="overflow-x-scroll">
		<table class="table table-compact table-hover" bind:this={tableElement}>
			<thead>
				{#if columns}
					<tr>
						{#each columns as column}
							{#if column.sortable}
								<Th {handler} orderBy={column.key}>{column.header}</Th>
							{:else}
								<th>{column.header}</th>
							{/if}
						{/each}
					</tr>
					{#if filterable}
						<tr>
							{#each columns as column}
								{#if column.filterable}
									<ThFilter {handler} filterBy={column.key} />
								{:else}
									<th />
								{/if}
							{/each}
						</tr>
					{/if}
				{/if}
			</thead>
			<tbody>
				{#if columns}
					{#each $rows as row, rowIndex}
						<tr
							on:click={(e) => {
								onRowClick(e, rowIndex);
							}}
							on:keydown={(e) => {
								onRowKeydown(e, rowIndex);
							}}
							aria-rowindex={rowIndex + 1}
						>
							{#each columns as column, colIndex}
								<td
									class="!align-middle"
									role="gridcell"
									aria-colindex={colIndex + 1}
									tabindex={colIndex === 0 ? 0 : -1}
								>
									{#if column.component}
										<svelte:component this={column.component} {row} />
									{:else if column.translate}
										{column.translate(row[column.key])}
									{:else}
										{row[column.key]}
									{/if}
								</td>
							{/each}
						</tr>
					{/each}
				{/if}
			</tbody>
		</table>
	</div>

	{#if pagination}
		<footer>
			<Paginator
				bind:settings={page}
				showFirstLastButtons={false}
				showPreviousNextButtons={true}
				on:page={pageChange}
				on:amount={rowsPerPageChange}
			/>
		</footer>
	{/if}
</section>
