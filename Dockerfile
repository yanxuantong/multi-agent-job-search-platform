FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY jobagent ./jobagent
COPY mcp_server ./mcp_server
COPY samples ./samples

RUN python -m pip install --no-cache-dir -e .

CMD ["python", "-m", "jobagent.cli", "integrations"]
