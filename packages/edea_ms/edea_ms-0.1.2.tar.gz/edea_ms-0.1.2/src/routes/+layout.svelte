<script lang="ts">
	import '../app.postcss';

	import ProjectForm from '$lib/modals/ProjectForm.svelte';
	import SpecificationForm from '$lib/modals/SpecificationForm.svelte';
	import DataQualityForm from '$lib/modals/DataQualityForm.svelte';
	import Navigation from '$lib/navigation/Navigation.svelte';
	import {
		AppBar,
		AppShell,
		Drawer,
		LightSwitch,
		Modal,
		Toast,
		getDrawerStore,
		initializeStores,
		type ModalComponent,
		autoModeWatcher
	} from '@skeletonlabs/skeleton';
	import { setContext } from 'svelte';
	import { writable } from 'svelte/store';
	import type { LayoutData } from './$types';

	export let data: LayoutData;

	initializeStores();

	function drawerOpen() {
		let drawerStore = getDrawerStore();
		drawerStore.open({});
	}

	const modalComponentRegistry: Record<string, ModalComponent> = {
		modalSpecificationForm: {
			ref: SpecificationForm
		},
		modalProjectForm: {
			ref: ProjectForm
		},
		modalChangeDataQuality: {
			ref: DataQualityForm
		}
	};

	// store user information in a context
	setContext('user', writable(data.user));
</script>

<svelte:head>{@html `<script>${autoModeWatcher.toString()} autoModeWatcher();</script>`}</svelte:head>

<Drawer>
	<Navigation />
</Drawer>

<Modal components={modalComponentRegistry} />

<AppShell slotSidebarLeft="bg-surface-500/5 w-0 lg:w-64">
	<svelte:fragment slot="header">
		<!-- App Bar -->
		<AppBar shadow="shadow-2xl">
			<svelte:fragment slot="lead">
				<div class="flex items-center">
					<button class="lg:hidden btn btn-sm mr-4" on:click={drawerOpen}>
						<span>
							<svg viewBox="0 0 100 80" class="fill-token w-4 h-4">
								<rect width="100" height="20" />
								<rect y="30" width="100" height="20" />
								<rect y="60" width="100" height="20" />
							</svg>
						</span>
					</button>
					<a class="lg:!ml-0 w-[48px] lg:w-auto overflow-hidden" href="/">
						<img src="/icon.svg" alt="EDeA logo" class="w-12 pl-2 pr-2" />
					</a>
				</div>
			</svelte:fragment>
			<svelte:fragment slot="trail">
				<a class="btn btn-sm variant-filled" href="https://blog.edea.dev" target="_blank"> Blog </a>
				<a
					class="btn btn-sm variant-filled"
					href="https://edea-dev.gitlab.io/edea-ms/"
					target="_blank"
				>
					Docs
				</a>
				<a class="btn btn-sm variant-filled" href="https://tmc.edea.dev" target="_blank">
					TMC Docs
				</a>
				<a
					class="btn btn-sm variant-filled"
					href="https://gitlab.com/edea-dev/edea-ms"
					target="_blank"
				>
					GitLab
				</a>
				{#if data.user == undefined}
					<a class="btn btn-sm variant-filled" href="/api/login/dex">Login</a>
				{:else if data.user.subject != "single_user"}
					<a class="btn btn-sm variant-filled" href="/api/logout">Logout</a>
				{/if}
				<LightSwitch />
			</svelte:fragment>
		</AppBar>
	</svelte:fragment>
	<svelte:fragment slot="sidebarLeft">
		<Navigation />
	</svelte:fragment>
	<Toast />
	<!-- Page Route Content -->
	<slot />
</AppShell>
