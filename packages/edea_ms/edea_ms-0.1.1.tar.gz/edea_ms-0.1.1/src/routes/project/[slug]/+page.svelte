<script lang="ts">
	import { goto } from '$app/navigation';
	import SimpleTable from '$lib/tables/SimpleTable.svelte';
	import { columnDef, componentColumnDef, type Column } from '$lib/tables/types';
	import { getModalStore, type ModalSettings } from '@skeletonlabs/skeleton';
	import type { Row } from '@vincjo/datatables';
	import { readable } from 'svelte/store';
	import type { PageData } from './$types';
	import Actions from './actions.svelte';
	import DetailLink from './detail_link.svelte';
	import CheckBox from './select_box.svelte';
	import { selected_ids, specifications } from './store';

	export let data: PageData;
	const modalStore = getModalStore();

	specifications.set(data.specifications);
	let testruns = readable(data.testruns);

	const specColumns: Column[] = [
		columnDef('id', 'ID'),
		columnDef('project_id', 'Project ID'),
		columnDef('name', 'Name'),
		columnDef('minimum', 'Minimum'),
		columnDef('typical', 'Typical'),
		columnDef('maximum', 'Maximum'),
		columnDef('unit', 'Unit'),
		componentColumnDef('Actions', Actions)
	];

	const testrunColumns: Column[] = [
		componentColumnDef('Select', CheckBox),
		componentColumnDef('ID', DetailLink),
		columnDef('short_code', 'Short code'),
		columnDef('dut_id', 'DUT ID'),
		columnDef('machine_hostname', 'Machine Hostname'),
		columnDef('user_name', 'Username'),
		columnDef('test_name', 'Test Name')
	];

	const modalCreateSpec: ModalSettings = {
		type: 'component',
		title: 'New specification for ' + data.project.name,
		body: '',
		meta: { project_id: data.project.id },
		// Pass the component registry key as a string:
		component: 'modalSpecificationForm',
		response: async (r: any) => {
			if (r) {
				// append new specification to the table
				$specifications.push(r);
				specifications.set($specifications);
				modalStore.close();
			}
		}
	};

	function newSpec() {
		modalStore.trigger(modalCreateSpec);
	}

	function compareTestruns() {
		let values = Array.from($selected_ids.values());
		goto(`/project/compare?id=${data.project.id}&testruns=${values.join()}`);
	}

	function rowSelected(e: CustomEvent<Row>) {
		goto(`/testrun/${e.detail.id}`);
	}
</script>

<div class="container mx-auto p-8 space-y-8">
	<h1 class="h1">
		{data.project.name}{#if data.project.number}
			({data.project.number}){/if}
	</h1>

	<section class="space-y-2">
		<h2 class="h2">Testruns</h2>
		{#if $testruns.length > 0}
			<div>
				{#if $selected_ids.size > 1}
					<button class="btn variant-filled" on:click={compareTestruns}>Compare Selected</button>
				{:else}
					<button class="btn variant-filled" disabled>Compare Selected</button>
				{/if}
				<p>Only testruns with charts can be compared for now.</p>
			</div>
			<SimpleTable
				data={testruns}
				columns={testrunColumns}
				rowsPerPage={10}
				on:selected={rowSelected}
			/>
		{:else}
			<p>No testruns available.</p>
		{/if}
	</section>
	<hr />
	<section class="space-y-2">
		<div class="flex justify-between">
			<h2 class="h2">Specifications</h2>
			<button class="btn variant-filled" on:click={newSpec}>New</button>
		</div>
		{#if $specifications.length > 0}
			<SimpleTable data={specifications} columns={specColumns} rowsPerPage={10} />
		{:else}
			<p>No specification data available.</p>
		{/if}
	</section>
</div>
