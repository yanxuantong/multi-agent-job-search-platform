# Langfuse Deployment Note

Langfuse is part of the original Project 1 stack for traces, token usage, latency, cost, prompt versions, datasets, and eval dashboards.

This repo keeps Langfuse optional because the default learning workflow should run without accounts, API keys, or hosted services. Use the local JSONL trace first, then export to Langfuse with `jobagent.observability.langfuse_exporter.LangfuseTraceExporter`.

Recommended learning sequence:

1. Run the default trace locally:

   ```bash
   python3 -m jobagent.cli demo --auto-approve
   ```

2. Inspect `.jobagent/runs/<run_id>/trace.jsonl`.

3. Install the optional SDK:

   ```bash
   python3 -m pip install -e '.[observability]'
   ```

4. Configure Langfuse credentials using the current Langfuse documentation.

5. Export a trace through `LangfuseTraceExporter`.

For self-hosting, prefer Langfuse's official deployment guide because its backing services and compose templates can change over time. The important project lesson is the instrumentation boundary: every agent node should emit run id, node name, prompt version, model, tokens, latency, cost, and error metadata.
