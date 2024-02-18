import type { PageLoad } from './$types';
import { getTestRunData } from "$lib/helpers";


export const load = (async ({ fetch, params }) => {
    const { run, measurements } = await getTestRunData(fetch, params.id);

    return {
        testrun: run,
        measurements: measurements,
        name: params.id
    }
}) satisfies PageLoad;
