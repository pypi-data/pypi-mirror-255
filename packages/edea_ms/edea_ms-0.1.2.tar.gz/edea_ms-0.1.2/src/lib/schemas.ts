import { z } from 'zod';

export const ProjectSchema = z.object({
    id: z.number().nullable(),
    short_code: z.string().nullable(),
    name: z.string(),
    group: z.string(),
});

export const SpecificationSchema = z.object({
    id: z.number().nullable(),
    project_id: z.number(),
    name: z.string(),
    unit: z.string().default(""),
    minimum: z.number(),
    typical: z.number(),
    maximum: z.number()
});

export const DataQualitySchema = z.object({
    testrun_id: z.number(),
    quality: z.string().nullable(),
})
