<script lang="ts">
	import { superForm, superValidateSync } from 'sveltekit-superforms/client';
	import { ProjectSchema } from '$lib/schemas';
	import { submitForm } from "$lib/helpers";

	// Props
	/** Exposes parent props to this component. */
	export let parent: any;
	// Stores
	import { getModalStore } from '@skeletonlabs/skeleton';

	const modalStore = getModalStore();

	// Modal metadata, default to create modal but should also work as update form
	const form_id = $modalStore[0].meta?.form_id || 'create-project-form';
	let project_id = $modalStore[0].meta?.project_id || undefined;
	const groups = $modalStore[0].meta?.groups || [];
	const row = $modalStore[0].meta?.row || undefined;
	if (project_id == undefined && row) {
		project_id = row.id;
	}

	// Base Classes
	const cBase = 'card p-4 w-modal shadow-xl space-y-4';
	const cHeader = 'text-2xl font-bold';
	const cForm = 'border border-surface-500 p-4 space-y-4 rounded-container-token';

	const { form, errors, enhance, constraints } = superForm(superValidateSync(row, ProjectSchema), {
		SPA: true,
		validators: ProjectSchema,
		async onUpdate({ form }) {
			if (form.valid) {
				const request_body = {
					id: form.data.id,
					short_code: form.data.short_code,
					name: form.data.name,
					groups: form.data.group == 'none' ? [] : [form.data.group]
				};

				const d = await submitForm('projects', form, request_body);

				if ($modalStore[0]?.response) {
					$modalStore[0].response(d);
				}
				modalStore.close();
			}
		},
		id: form_id,
		applyAction: false // if set to true, this triggers onUpdated immediately after opening the modal again
	});

	$form.id = project_id || null;

	function formClose() {
		modalStore.close();
	}
</script>

<!-- @component Form for creating new specifications. -->

<div class={cBase}>
	<header class={cHeader}>{$modalStore[0]?.title ?? '(title missing)'}</header>
	<article>{$modalStore[0]?.body ?? '(body missing)'}</article>
	<form id={form_id} class="modal-form {cForm}" method="POST" use:enhance>
		{#if row}
			<input type="hidden" name="id" bind:value={$form.id} />
		{/if}
		<label class="label">
			<span>Short Code</span>
			<input
				name="short_code"
				class="input"
				type="text"
				aria-invalid={$errors.short_code ? true : undefined}
				bind:value={$form.short_code}
				{...$constraints.short_code}
				placeholder="Enter internal project designator..."
			/>
			{#if $errors.short_code}<span class="invalid">{$errors.short_code}</span>{/if}
		</label>
		<label class="label">
			<span>Name</span>
			<input
				name="name"
				class="input"
				type="text"
				aria-invalid={$errors.name ? true : undefined}
				bind:value={$form.name}
				{...$constraints.name}
				placeholder="Enter name..."
			/>
			{#if $errors.name}<span class="invalid">{$errors.name}</span>{/if}
		</label>
		<label class="label">
			<span>Group</span>
			<select
				class="select"
				name="group"
				aria-invalid={$errors.group ? true : undefined}
				bind:value={$form.group}
				{...$constraints.group}
			>
				<option value="none">None</option>
				{#each groups as group}
					{#if row && row.groups.length > 0 && row.groups[0] == group}
						<option value={group} selected>{group}</option>
					{:else}
						<option value={group}>{group}</option>
					{/if}
				{/each}
			</select>
		</label>
		<footer class="modal-footer {parent.regionFooter}">
			<button class="btn {parent.buttonPositive}">Submit</button>
			<button class="btn {parent.buttonNeutral}" type="button" on:click={formClose}
				>{parent.buttonTextCancel}</button
			>
		</footer>
	</form>
</div>
