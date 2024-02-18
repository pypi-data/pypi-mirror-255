<script lang="ts">
	import SimpleTable from '$lib/tables/SimpleTable.svelte';
	import { readable } from 'svelte/store';
	import type { PageData } from './$types';

	import { VegaLite } from 'svelte-vega';
	import type { EmbedOptions } from 'vega-embed';
	import { Icon, Pencil } from 'svelte-hero-icons';

	export let data: PageData;

	const vegaData = { measurements: data.measurements };
	const hasVegaViz = data.testrun.data?.vega_lite ? true : false;

	import type { ModalSettings } from '@skeletonlabs/skeleton';
	import { getModalStore } from '@skeletonlabs/skeleton';

	const modalStore = getModalStore();

	function exportTestrunData(e: Event) {
		// TODO
	}

	let vo: EmbedOptions = {
		theme: undefined,
		actions: { export: true, source: false, compiled: true, editor: false }
	};

	async function changeDataQuality(e: Event) {
		const modalChangeDataQuality: ModalSettings = {
			type: 'component',
			title: 'Update Quality',
			body: '',
			meta: { testrun: data.testrun, method: 'PUT' },
			// Pass the component registry key as a string:
			component: 'modalChangeDataQuality',
			response: async (r: any) => {
				if (r) {
					// TODO
					modalStore.close();
				}
			}
		};

		modalStore.trigger(modalChangeDataQuality);
	}
</script>

<div class="table-container mx-auto p-8 space-y-8">
	<section class="space-y-2">
		<div class="flex justify-between">
			<h1 class="h1">Testrun {data.name}</h1>
			<button class="btn variant-filled" on:click={exportTestrunData}>Export</button>
		</div>
	</section>

	<section class="space-y-2">
		<div class="flex space-x-2">
			<p>Result data quality: {data.testrun.data?.quality}</p>
			<button
				class="chip variant-soft hover:variant-filled"
				on:click={changeDataQuality}
				on:keypress={changeDataQuality}
			>
				<span><Icon size="12" src={Pencil} /></span>
				<span>Edit</span>
			</button>
		</div>
	</section>

	<section class="space-y-2">
		{#if data.measurements.length > 0}
			<SimpleTable data={readable(data.measurements)} />
		{:else}
			<p>No Testrun data available.</p>
		{/if}
	</section>

	<section class="space-y-2">
		<h2 class="h2">Visualizations</h2>
		<div>
			<a class="chip variant-soft hover:variant-filled" href="/chart_editor/{data.testrun.id}">
				<span><Icon size="12" src={Pencil} /></span>
				<span>Edit</span>
			</a>
		</div>
		{#if data.measurements.length > 0 && hasVegaViz && data.testrun.data?.vega_lite}
			<VegaLite data={vegaData} spec={data.testrun.data.vega_lite} options={vo} />
		{/if}
	</section>
</div>
