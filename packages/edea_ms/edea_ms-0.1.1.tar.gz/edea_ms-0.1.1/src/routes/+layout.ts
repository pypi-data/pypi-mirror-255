import type { User } from '$lib/models/models.js';

export const ssr = false;
// export const prerender = true;

export async function load({ fetch }) {
    const response = await fetch('/api/users/self');

	return {
		user: response.status == 200 ? await response.json() as Promise<User> : undefined
	};
}
