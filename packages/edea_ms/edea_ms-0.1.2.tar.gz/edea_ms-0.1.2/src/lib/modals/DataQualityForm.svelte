<script lang="ts">
	import { superForm, superValidateSync } from 'sveltekit-superforms/client';
	import { DataQualitySchema } from '$lib/schemas';
	import { submitFormObject } from '$lib/helpers';

	// Props
	/** Exposes parent props to this component. */
	export let parent: any;
	// Stores
	import { getModalStore } from '@skeletonlabs/skeleton';

	const modalStore = getModalStore();

	// Modal metadata, default to create modal but should also work as update form
	const form_id = $modalStore[0].meta?.form_id || 'data-quality-form';
	let testrun_id = $modalStore[0].meta?.testrun_id || undefined;
	const testrun = $modalStore[0].meta?.testrun || undefined;
	if (testrun_id == undefined && testrun) {
		testrun_id = testrun.id;
	}

	let row = {
		testrun_id: testrun.id,
		quality: testrun.data?.quality
	};

	// Base Classes
	const cBase = 'card p-4 w-modal shadow-xl space-y-4';
	const cHeader = 'text-2xl font-bold';
	const cForm = 'border border-surface-500 p-4 space-y-4 rounded-container-token';

	const { form, errors, enhance, constraints } = superForm(
		superValidateSync(row, DataQualitySchema),
		{
			SPA: true,
			validators: DataQualitySchema,
			async onUpdate({ form }) {
				if (form.valid) {
					const d = await submitFormObject(
						'PUT',
						'testruns/' + testrun_id + '/field/quality',
						form,
						form.data.quality
					);

					if ($modalStore[0]?.response) {
						$modalStore[0].response(d);
					}
					modalStore.close();
				}
			},
			id: form_id,
			applyAction: false // if set to true, this triggers onUpdated immediately after opening the modal again
		}
	);

	$form.testrun_id = testrun_id || null;

	function formClose() {
		modalStore.close();
	}
</script>

<!-- @component Form for setting the data quality of a testrun -->

<div class={cBase}>
	<header class={cHeader}>{$modalStore[0]?.title ?? '(title missing)'}</header>
	<article>{$modalStore[0]?.body ?? '(body missing)'}</article>
	<p>
		The data quality should refer to the confidence as to how representative the results are for the
		tests.
	</p>
	<dl class="list-dl">
		<div>
			<span class="badge bg-primary-500">💀</span>
			<span class="flex-auto">
				<dt class="font-bold">Not-representative</dt>
				<dd>Test was interrupted or mistakes in the configuration or methodology were found.</dd>
			</span>
		</div>
		<div>
			<span class="badge bg-primary-500">🥉</span>
			<span class="flex-auto">
				<dt class="font-bold">Bronze</dt>
				<dd>Test setup or code still in progress but results are already worth looking at.</dd>
			</span>
		</div>
		<div>
			<span class="badge bg-primary-500">🥈</span>
			<span class="flex-auto">
				<dt class="font-bold">Silver</dt>
				<dd>
					Test setup and code are in a state where results should be representative but more changes
					may be necessary.
				</dd>
			</span>
		</div>
		<div>
			<span class="badge bg-primary-500">🥇</span>
			<span class="flex-auto">
				<dt class="font-bold">Gold</dt>
				<dd>
					Test setup and code are in a state where results can be considered representative. Results
					are ready to be used in reports and graphs.
				</dd>
			</span>
		</div>
	</dl>
	<form id={form_id} class="modal-form {cForm}" method="POST" use:enhance>
		{#if row}
			<input type="hidden" name="id" bind:value={$form.testrun_id} />
		{/if}
		<label class="label">
			<span>Quality</span>
			<select
				name="quality"
				class="select"
				aria-invalid={$errors.quality ? true : undefined}
				bind:value={$form.quality}
				{...$constraints.quality}
			>
				<option value="undefined">Not-representative</option>
				<option value="bronze">Bronze</option>
				<option value="silver">Silver</option>
				<option value="gold">Gold</option>
			</select>
			{#if $errors.quality}<span class="invalid">{$errors.quality}</span>{/if}
		</label>
		<footer class="modal-footer {parent.regionFooter}">
			<button class="btn {parent.buttonPositive}">Submit</button>
			<button class="btn {parent.buttonNeutral}" type="button" on:click={formClose}
				>{parent.buttonTextCancel}</button
			>
		</footer>
	</form>
</div>
