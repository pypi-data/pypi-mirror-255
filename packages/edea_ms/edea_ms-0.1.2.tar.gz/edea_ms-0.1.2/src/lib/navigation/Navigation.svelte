<script lang="ts">
	import { getDrawerStore } from '@skeletonlabs/skeleton';
	const drawerStore = getDrawerStore();

	function drawerClose(): void {
		drawerStore.close();
	}
</script>

<nav class="list-nav p-4">
	<ul>
		<li><a href="/" on:click={drawerClose}>Overview</a></li>
		<li><a href="/projects" on:click={drawerClose}>Projects</a></li>
		<li><a href="/testruns" on:click={drawerClose}>Testruns</a></li>
	</ul>
</nav>
