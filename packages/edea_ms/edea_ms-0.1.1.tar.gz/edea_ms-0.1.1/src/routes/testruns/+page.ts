import type { TestRun } from '$lib/models/models';
import type {PageLoad} from './$types';

export const load = (async ({fetch, params}) => {
    const resp = await fetch("/api/testruns");
    return {testruns: await (resp.json() as Promise<TestRun[]>)}
}) satisfies PageLoad;
