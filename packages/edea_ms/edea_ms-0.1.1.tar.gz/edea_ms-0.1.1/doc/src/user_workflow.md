# User Workflow

Or how a user goes about their day while using EDeA-MS.

NOTE: this is from the early stages and will be reworked.

## Projects

At the beginning is always a new project.

### New Project

1. Create new project in UI. There will also be specific API support in the future to have a role which is allowed to create new projects to integrate with internal tooling.
2. Get the Project ID to input it into the new script.

### Existing project

Search for existing project based on name or id. Not sure how many projects the average user will have, or how/if we should support the usecase of thousands of projects per instance.

    ->  That's more for read-only projects in EDeA portal.

User takes selected project id or project name and inserts that into the script.

## Test runs

A test run will be generated each time the test-run script is executed.
In the future we may support resuming from the last known good state, but that needs instrument config capture and replay possibly.
Another possibility would be to support checkpoints, defined transition states from when on a testrun may be resumed and where previous data will be discarded then.

### Test run progress

Currently no progress reporting is planned. May be implemented later once the forcing condition generator is built.

### Test run results

Results should be searchable/viewable/sortable via datatables. For now only simply viewing the
data should be supported, for more complex analytics a data export will be provided so that the engineer can load the data into a jupyter notebook and explore it there.
