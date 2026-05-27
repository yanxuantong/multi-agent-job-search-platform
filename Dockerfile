FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY jobagent ./jobagent
COPY mcp_server ./mcp_server
COPY samples ./samples
COPY tests ./tests

RUN python -m pip install --no-cache-dir -e .

CMD ["sh", "-c", "uvicorn jobagent.web.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
