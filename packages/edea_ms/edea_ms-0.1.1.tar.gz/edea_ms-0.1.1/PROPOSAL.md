# EDeA MS Continuation

## Data Processors

Use processing pipelines compiled to WebAssembly to post-process data after taking measurements.
Can either output new measurement data or binary blobs (e.g. plot graphics) for generating reports.

## JupyterLite Integration

JupyterLite can be used to work with notebooks and EDeA MS data directly in the browser.
The edea-ms python package should detect and support when it's running in a browser and possibly pick up the cookies
if possible to automatically authenticate against the measurement server.

## Make an Investigation Check

Pick the probe point in the PCB/Schematic where you connect your probes.
