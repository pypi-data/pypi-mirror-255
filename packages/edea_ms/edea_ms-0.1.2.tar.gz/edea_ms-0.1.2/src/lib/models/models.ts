import type { VisualizationSpec } from "svelte-vega";

export enum TestRunState {
    NEW = 1,
    SETUP_COMPLETE = 2,
    RUNNING = 3,
    INTERRUPTED = 4,
    COMPLETE = 5,
    FAILED = 6,

}

export type TestRunData = {
    vega_lite?: VisualizationSpec
    vega_lite_temp?: string
    quality?: string
}

export type TestRun = {
    id: number;
    project_id: number;
    short_code: string;
    dut_id: string;
    machine_hostname: string;
    user_name: string;
    test_name: string;
    created_at: string;
    started_at: string;
    completed_at: string;
    state: TestRunState;
    data?: TestRunData;
}

export type Specification = {
    id?: number;
    project_id: number;
    name: string;
    unit: string;
    minimum?: number;
    typical?: number;
    maximum?: number;
}

export type Project = {
    id: number;
    short_code: string;
    name: string;
    groups: string[];
}

export type User = {
    id: number;
    subject: string;
    displayname: string;
    groups: string[];
    roles: string[];
    disabled?: boolean;
}
