FROM python:3.9-slim-buster

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /APP

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-install-project

COPY . .
RUN uv sync --frozen

ENV PATH="/APP/.venv/bin:$PATH"

CMD ["flask", "run", "--host=0.0.0.0"]
EXPOSE 5000
