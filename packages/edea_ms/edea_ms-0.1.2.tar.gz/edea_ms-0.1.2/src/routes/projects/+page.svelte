<script lang="ts">
	import { goto } from '$app/navigation';
	import type { User } from '$lib/models/models';
	import SimpleTable from '$lib/tables/SimpleTable.svelte';
	import { columnDef, componentColumnDef, type Column } from '$lib/tables/types';
	import { getModalStore, type ModalSettings } from '@skeletonlabs/skeleton';
	import type { Row } from '@vincjo/datatables';
	import { getContext } from 'svelte';
	import type { Writable } from 'svelte/store';
	import type { PageData } from './$types';
	import Actions from './actions.svelte';
	import { projects } from './store';

	export let data: PageData;
	const modalStore = getModalStore();

	projects.set(data.projects);

	const user = getContext<Writable<User | undefined>>('user');

	const columns: Column[] = [
		columnDef('id', 'ID'),
		columnDef('short_code', 'Short Code'),
		columnDef('name', 'Name'),
		columnDef('groups', 'Groups'),
		componentColumnDef('Actions', Actions)
	];

	const modalCreateProject: ModalSettings = {
		type: 'component',
		title: 'New Project',
		body: '',
		meta: { groups: $user?.groups },
		// Pass the component registry key as a string:
		component: 'modalProjectForm',
		response: async (r: any) => {
			if (r) {
				// append new specification to the table
				$projects.push(r);
				projects.set($projects);
				modalStore.close();
			}
		}
	};

	function newProject() {
		modalStore.trigger(modalCreateProject);
	}

	function rowSelected(e: CustomEvent<Row>) {
		goto(`/project/${e.detail.id}`);
	}
</script>

<div class="container mx-auto p-8 space-y-8">
	<section class="flex justify-between">
		<h1 class="h1">Projects</h1>
		{#if $user !== undefined}
			<button class="btn bg-gradient-to-br variant-filled" on:click={newProject}>New</button>
		{/if}
	</section>

	{#if $projects.length > 0}
		<SimpleTable data={projects} {columns} rowsPerPage={10} on:selected={rowSelected} />
	{:else}
		<p>No project data available.</p>
	{/if}
</div>
