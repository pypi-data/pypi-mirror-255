<script lang="ts">
	import { writable } from 'svelte/store';
	import type { PageData } from './$types';
	import { getModeAutoPrefers, modeCurrent } from '@skeletonlabs/skeleton';

	import { VegaLite } from 'svelte-vega';
	import type { EmbedOptions } from 'vega-embed';
	import { onMount } from 'svelte';

	export let data: PageData;

	let vo: EmbedOptions = {
		theme: undefined,
		// only show actions which make sense. source and editor are available on the page
		actions: { export: true, source: false, compiled: true, editor: false }
	};
	let vizOtions = writable(vo);

	onMount(async () => {
		vizOtions.update((o: EmbedOptions) => {
			o.theme = getModeAutoPrefers() ? undefined : 'dark';
			return o;
		});
	});

	modeCurrent.subscribe((val) => {
		vizOtions.update((o: EmbedOptions) => {
			o.theme = val ? undefined : 'dark';
			return o;
		});
	});
</script>

<div class="container mx-auto p-8 space-y-8">
	<h2 class="h2">Compare testruns</h2>
	<table class="table table-hover">
		<thead>
			{#each data.runs as v}
				<th>ID: {v.run.id}, SC: {v.run.short_code}</th>
			{/each}
		</thead>
		<tbody>
			<tr>
				{#each data.runs as v}
					{#if v.run.data?.vega_lite}
						<td>
							<p><a href="/testruns/{v.run.id}">Run {v.run.id}</a></p>
							<p>Started at {v.run.started_at}, completed at {v.run.completed_at}</p>
							<VegaLite
								data={{ measurements: v.measurements }}
								spec={v.run.data?.vega_lite}
								options={$vizOtions}
							/>
						</td>
					{:else}
						<p>no viz for {v.run.id}</p>
					{/if}
				{/each}
			</tr>
		</tbody>
	</table>
</div>
