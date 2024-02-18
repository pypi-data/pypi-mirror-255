import type { ComponentType } from "svelte";

export type Column = {
    key: string;
    header: string;
    sortable: boolean;
    filterable: boolean;
    component?: ComponentType;
    translate?: ((v: any) => string);
};

export interface IColumnOptions {
    sortable?: boolean;
    filterable?: boolean;
    translate?: ((v: any) => string);
}

export function columnDef(key: string, header: string, options?: IColumnOptions): Column {
    return {
        key: key,
        header: header,
        sortable: options?.sortable || false,
        filterable: options?.filterable || false,
        translate: options?.translate || undefined
    }
}

export function componentColumnDef(header: string, component: ComponentType): Column {
    return {
        key: '',
        header: header,
        sortable: false,
        filterable: false,
        component: component,
        translate: undefined
    }
}