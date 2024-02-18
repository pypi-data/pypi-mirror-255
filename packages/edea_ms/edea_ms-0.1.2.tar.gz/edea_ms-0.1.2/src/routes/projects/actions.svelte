<script lang="ts">
	// define all the props that get passed to a cell component
	export let row: any;

	import { Icon, Pencil, Trash } from 'svelte-hero-icons';

	import type { ModalSettings, ToastSettings } from '@skeletonlabs/skeleton';
	import { getModalStore, getToastStore } from '@skeletonlabs/skeleton';
	import { projects, user } from './store';

	const modalStore = getModalStore();
	const toastStore = getToastStore();

	async function deleteSpecification(id: number) {
		try {
			const response = await fetch('/api/projects/' + id, {
				method: 'DELETE'
			});

			if (response.ok) {
				const t: ToastSettings = {
					message: 'Project deleted',
					background: 'variant-filled-success'
				};
				toastStore.trigger(t);
				let index = $projects.findIndex((x) => x.id == id);
				$projects.splice(index, 1);

				// need to manually trigger the update because it's a reference
				projects.set($projects);
			} else {
				const t: ToastSettings = {
					message: 'An error occured: ' + response.statusText,
					background: 'variant-filled-error',
					timeout: 5000
				};
				toastStore.trigger(t);
			}
		} catch (error) {
			const t: ToastSettings = {
				message: 'An error occured while sending the request to the server: ' + error,
				background: 'variant-filled-error',
				autohide: false
			};
			toastStore.trigger(t);
		}
	}

	async function confirmDelete(e: Event) {
		let spec_name = row['name'];
		const confirm: ModalSettings = {
			type: 'confirm',
			title: 'Please Confirm',
			body: 'Are you sure you want to delete "' + spec_name + '"',
			response: async (r: boolean) => {
				if (!r) return;
				await deleteSpecification(row['id']);
			}
		};
		modalStore.trigger(confirm);
	}

	async function editRow(e: Event) {
		const modalEditProject: ModalSettings = {
			type: 'component',
			title: 'Updating ' + row.name,
			body: '',
			meta: { row: row, method: 'PUT', groups: $user.groups },
			// Pass the component registry key as a string:
			component: 'modalProjectForm',
			response: async (r: any) => {
				if (r) {
					// change the modified specification
					let index = $projects.findIndex((x) => x.id == r.message.id);
					$projects[index] = r.message;
					projects.set($projects);
					modalStore.close();
				}
			}
		};

		modalStore.trigger(modalEditProject);
	}
</script>

<button class="chip variant-soft hover:variant-filled" on:click={editRow} on:keypress={editRow}>
	<span><Icon size="12" src={Pencil} /></span>
	<span>Edit</span>
</button>
<button
	class="chip variant-soft hover:variant-filled"
	on:click={confirmDelete}
	on:keypress={confirmDelete}
>
	<span><Icon size="12" src={Trash} /></span>
	<span>Delete</span>
</button>
