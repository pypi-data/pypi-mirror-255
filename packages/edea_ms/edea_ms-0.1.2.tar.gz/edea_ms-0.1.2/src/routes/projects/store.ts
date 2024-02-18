import type { Project, User } from '$lib/models/models';
import { writable, type Writable } from 'svelte/store';

export const projects: Writable<Project[]> = writable([]);
export const user: Writable<User> = writable();