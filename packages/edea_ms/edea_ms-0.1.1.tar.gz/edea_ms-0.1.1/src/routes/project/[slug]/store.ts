import type { Specification } from '$lib/models/models';
import { writable, type Writable } from 'svelte/store';

export const specifications: Writable<Specification[]> = writable([]);
export const selected_ids: Writable<Set<Number>> = writable(new Set<Number>());
