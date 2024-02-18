<script lang="ts">
	import { selected_ids } from './store';

	export let row: any;
	let has_viz = row.data?.vega_lite ? true : false;
	let is_checked = false;
    
    // add or remove the id on selection change
	function update_checklist() {
		if (is_checked) {
			selected_ids.update((s) => s.add(row.id));
		} else {
			selected_ids.update((s) => {
				s.delete(row.id);
				return s;
			});
		}
	}
</script>

{#if has_viz}
	<input class="checkbox" type="checkbox" bind:checked={is_checked} on:change={update_checklist} />
{:else}
	<input class="checkbox" type="checkbox" disabled />
{/if}
