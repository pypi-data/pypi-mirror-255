import { getTestRunData } from '$lib/helpers';
import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';
import type { Project, TestRun } from '$lib/models/models';
import type { Row } from '@vincjo/datatables';

type TRDTuple = {
    run: TestRun,
    measurements: Row[],
};

export const load = (async ({ fetch, url }) => {
    let project_id = url.searchParams.get("id");
    let run_ids = url.searchParams.get("testruns")?.split(",").sort();

    const project = await fetch("/api/projects/" + project_id)
        .then(response => {
            if (!response.ok) {
                error(response.status, response.statusText);
            }
            return response.json() as Promise<Project>
        });

    let runs: Array<TRDTuple> = [];

    if (run_ids) {
        for (var id of run_ids) {
            const { run, measurements } = await getTestRunData(fetch, id);
            runs.push({ run, measurements });
        }
    }

    return {
        project: project,
        runs: runs,
    };
}) satisfies PageLoad;
