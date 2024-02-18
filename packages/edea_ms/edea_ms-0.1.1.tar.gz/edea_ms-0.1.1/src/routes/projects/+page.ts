import type { Project } from '$lib/models/models';
import type { PageLoad } from './$types';

export const load = (async ({ fetch, params }) => {
    const projects = await fetch("/api/projects");
    return {
        projects: await (projects.json() as Promise<Project[]>)
    }
}) satisfies PageLoad;
