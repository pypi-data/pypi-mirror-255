import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';
import type { TestRun } from '$lib/models/models';

export const load = (async ({ fetch, params }) => {
    return {
        testruns: fetch("/api/testruns/overview")
            .then(response => {
                if (response.status == 401) {
                    return Promise.resolve<TestRun[]>([]);
                } else if (!response.ok) {
                    error(response.status, response.statusText);
                } else {
                    return response.json() as Promise<TestRun[]>
                }
            })
    }
}) satisfies PageLoad;
