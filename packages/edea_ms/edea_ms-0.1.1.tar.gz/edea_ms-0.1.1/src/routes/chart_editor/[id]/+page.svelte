<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { readable, writable } from 'svelte/store';
	import type { PageData } from './$types';

	import {
		getModeAutoPrefers,
		modeCurrent,
		type ToastSettings,
		getToastStore
	} from '@skeletonlabs/skeleton';

	import * as monaco from 'monaco-editor';
	import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker';
	import jsonWorker from 'monaco-editor/esm/vs/language/json/json.worker?worker';

	import { VegaLite } from 'svelte-vega';
	import type { EmbedOptions } from 'vega-embed';
	import type { VisualizationSpec } from 'svelte-vega';
	import SimpleTable from '$lib/tables/SimpleTable.svelte';

	const toastStore = getToastStore();

	let editorElement: HTMLDivElement;
	let editor: monaco.editor.IStandaloneCodeEditor;
	let model: monaco.editor.ITextModel;

	export let data: PageData;
	const vegaData = { measurements: data.measurements };

	let code = `{
  "data": {
    "name": "measurements"
  },
  "mark": "line",
  "encoding": {
    "x": {
      "field": "date",
      "type": "temporal"
    },
    "y": {
      "field": "price",
      "type": "quantitative"
    }
  }
}`;

	let vo: EmbedOptions = {
		theme: undefined,
		// only show actions which make sense. source and editor are available on the page
		actions: { export: true, source: false, compiled: true, editor: false }
	};
	let vizOtions = writable(vo);

	let documentValid = writable(false);
	let hasTemporary = writable(data.testrun.data?.vega_lite_temp ? true : false);
	let hasChanges = writable(false);

	let spec: VisualizationSpec;

	if (data.testrun.data?.vega_lite) {
		spec = data.testrun.data.vega_lite;
	} else {
		spec = JSON.parse(code);
	}

	let vizSpec = writable(spec);

	async function updateChart(body: string | null, temporary: boolean): Promise<number> {
		let url =
			'/api/testruns/' + data.testrun.id + '/field/' + (temporary ? 'vega_lite_temp' : 'vega_lite');
		let method = body ? 'PUT' : 'DELETE';
		const resp = await fetch(url, {
			headers: { 'Content-Type': 'application/json' },
			method: method,
			body: body
		});

		if (resp.status != 200) {
			console.log(resp);
			const t: ToastSettings = {
				message: 'Error saving the chart',
				background: 'variant-filled-error'
			};

			toastStore.trigger(t);
			return 1;
		}

		return 0;
	}

	onMount(async () => {
		self.MonacoEnvironment = {
			getWorker: function (_: any, label: string) {
				if (label === 'json') {
					return new jsonWorker();
				}
				return new editorWorker();
			}
		};

		monaco.languages.typescript.typescriptDefaults.setEagerModelSync(true);

		editor = monaco.editor.create(editorElement, {
			automaticLayout: true,
			theme: getModeAutoPrefers() ? 'vs' : 'vs-dark'
		});

		let modelUri = monaco.Uri.parse('https://vega.github.io/schema/vega-lite/v5.json');
		let modelContent: string | VisualizationSpec = code;
		if (data.testrun.data?.vega_lite_temp) {
			modelContent = data.testrun.data.vega_lite_temp;
		} else {
			modelContent = spec;
		}

		model = monaco.editor.createModel(JSON.stringify(modelContent, null, 4), 'json', modelUri);
		editor.setModel(model);

		monaco.languages.json.jsonDefaults.setDiagnosticsOptions({
			validate: true,
			enableSchemaRequest: true,
			schemas: [
				{
					uri: 'https://vega.github.io/schema/vega-lite/v5.json', // id of the first schema
					fileMatch: [modelUri.toString()]
				}
			]
		});

		// save the chart when hitting Ctrl+S
		editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, async () => {
			const rc = await updateChart(model.getValue(), !$documentValid);

			if (rc == 0) {
				if ($documentValid && $hasTemporary) {
					const rc = await updateChart(null, true);
					if (rc == 0) {
						$hasTemporary = false;
					}
				} else if (!$documentValid && !hasTemporary) {
					$hasTemporary = true;
				}

				$hasChanges = false;
			}
			if ($documentValid) {
				// if the vega spec is valid, update the real chart
				const r = await updateChart(model.getValue(), false);

				// remove the old, temporary chart spec
				if ($hasTemporary) {
					await updateChart(null, true);
					$hasTemporary = false;
				}
			} else {
				// otherwise save it as a temp chart
				const r = await updateChart(model.getValue(), true);
				if (!$hasTemporary) {
					$hasTemporary = true;
				}
			}
		});

		editor.onDidChangeModelDecorations(() => {
			const markers = monaco.editor.getModelMarkers({ owner: 'json' });
			if (markers.length == 0 && $documentValid == false) {
				documentValid.set(true);
				$vizSpec = JSON.parse(model.getValue());
			} else if (markers.length > 0 && $documentValid) {
				documentValid.set(false);
			}
		});

		editor.onDidChangeModelContent((e) => {
			if (!$hasChanges) {
				$hasChanges = true;
			}
		});

		vizOtions.update((o: EmbedOptions) => {
			o.theme = getModeAutoPrefers() ? undefined : 'dark';
			return o;
		});
	});

	onDestroy(() => {
		monaco?.editor.getModels().forEach((model) => model.dispose());
		editor?.dispose();
	});

	modeCurrent.subscribe((val) => {
		monaco.editor.setTheme(val ? 'vs' : 'vs-dark');
		vizOtions.update((o: EmbedOptions) => {
			o.theme = val ? undefined : 'dark';
			return o;
		});
	});
</script>

<div class="grid grid-cols-2 p-2 space-x-2 space-y-2">
	<div>
		<h3 class="h3">Specification</h3>
	</div>
	<div>
		<h3 class="h3">Preview</h3>
	</div>
	<div class="min-h-[38vh]">
		<div style="height: 100%;" bind:this={editorElement} />
	</div>
	<div class="">
		<VegaLite data={vegaData} spec={$vizSpec} options={$vizOtions} />
	</div>
	<div class="col-span-2">
		{#if $hasTemporary}<span class="chip variant-filled">Discard Temporary</span>{/if}
		{#if $hasChanges}
			<span class="chip variant-filled">Unsaved changes</span>
		{:else}
			<span class="chip variant-filled"
				>Saved {#if $hasTemporary}as temporary{/if}</span
			>
		{/if}
	</div>
	<div class="col-span-2">
		<SimpleTable data={readable(data.measurements)} rowsPerPage={10} />
	</div>
</div>
