<script lang="ts">
	import { goto } from '$app/navigation';
	import { TestRunState } from '$lib/models/models';
	import SimpleTable from '$lib/tables/SimpleTable.svelte';
	import { columnDef, type Column } from '$lib/tables/types';
	import type { Row } from '@vincjo/datatables';
	import { readable } from 'svelte/store';
	import type { PageData } from './$types';

	export let data: PageData;

	let testruns = readable(data.testruns);

	const columns: Column[] = [
		columnDef('id', 'ID'),
		columnDef('short_code', 'Short Code'),
		columnDef('machine_hostname', 'Hostname'),
		columnDef('user_name', 'User'),
		columnDef('test_name', 'Test Name'),
		columnDef('created_at', 'Created', { translate: (v) => new Date(v).toLocaleString('de-DE')}),
		columnDef('started_at', 'Started', { translate: (v) => new Date(v).toLocaleString('de-DE')}),
		columnDef('completed_at', 'Completed', { translate: (v) => new Date(v).toLocaleString('de-DE')}),
		columnDef('state', 'State', { translate: (v) => TestRunState[v] })
	];

	function rowSelected(e: CustomEvent<Row>) {
		goto(`/testrun/${e.detail.id}`);
	}
</script>

<div class="container mx-auto p-8 space-y-8">
	<h1 class="h1">Testruns</h1>

	{#if data.testruns.length > 0}
		<SimpleTable
			data={testruns}
			{columns}
			rowsPerPage={20}
			on:selected={rowSelected}
			search={false}
		/>
	{:else}
		<p>No testrun data available.</p>
	{/if}
</div>
