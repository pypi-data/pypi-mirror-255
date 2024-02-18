import { error } from '@sveltejs/kit';
import type { TestRun } from '$lib/models/models';
import type { Row } from '@vincjo/datatables';
import type { AnyZodObject } from 'zod';
import type { SuperValidated } from 'sveltekit-superforms';
import { setError } from 'sveltekit-superforms/client';

export async function getTestRunData(fetch: (input: RequestInfo | URL, init?: RequestInit | undefined) => Promise<Response>, id: string) {
    const run = await fetch("/api/testruns/" + id)
        .then(response => {
            if (!response.ok) {
                error(response.status, response.statusText);
            }
            return response.json() as Promise<TestRun>;
        });

    const measurements = await fetch("/api/testruns/measurements/" + run.id)
        .then(response => {
            if (!response.ok) {
                error(response.status, response.statusText);
            }
            return response.json() as Promise<Array<Row>>;
        });
    return { run, measurements };
}

export async function submitForm(
    endpoint: string,
    form: SuperValidated<AnyZodObject>,
    request_body?: Object
): Promise<any> {
    let method = 'POST';
    if (form.data.id) {
        endpoint += '/' + form.data.id;
        method = 'PUT';
    }

    return await submitFormObject(method, endpoint, form, request_body);
}

export async function submitFormObject(
    method: string,
    endpoint: string,
    form: SuperValidated<AnyZodObject>,
    request_body?: any
): Promise<any> {
    let url = '/api/' + endpoint;
    const resp = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        method: method,
        body: JSON.stringify(request_body || form.data)
    });

    const d = await resp.json();

    console.log(resp);

    // handle custom errors and set the form validation error field for it
    // for now this is only for unique constraints
    if (!resp.ok) {
        // an integrity error or the schema changed
        if (resp.status == 422) {
            if ('error' in d && 'type' in d['error']) {
                if (d.error.type == 'unique_violation') {
                    setError(form, d.error.field, 'An entry with this value already exists');
                } else {
                    console.log('TODO: implement this error type');
                }
            }
        } else {
            throw new Error("TODO");
        }
    }

    return d;
}