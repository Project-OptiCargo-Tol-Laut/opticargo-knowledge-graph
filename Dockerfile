# syntax=docker/dockerfile:1.7
FROM python:3.11-slim-bookworm AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build
COPY vendor/opticargo_shared-1.0.0-py3-none-any.whl /wheels/opticargo_shared-1.0.0-py3-none-any.whl
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN python -m pip install --upgrade pip setuptools wheel build && \
    python -m build --wheel --outdir /wheels

FROM python:3.11-slim-bookworm AS runtime

ARG OPTICARGO_RELEASE=dev
ARG OPTICARGO_GIT_SHA=local
ARG OPTICARGO_BUILD_TIME=unknown

LABEL org.opencontainers.image.title="opticargo-knowledge-graph" \
      org.opencontainers.image.description="OptiCargo Neo4j projection, synchronization, and reconciliation worker" \
      org.opencontainers.image.version="$OPTICARGO_RELEASE" \
      org.opencontainers.image.revision="$OPTICARGO_GIT_SHA" \
      org.opencontainers.image.created="$OPTICARGO_BUILD_TIME"

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/home/opticargo \
    TZ=UTC \
    WORKER_HEALTH_FILE=/tmp/opticargo-graph-worker-health.json

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 opticargo \
    && useradd --uid 10001 --gid 10001 --create-home --shell /usr/sbin/nologin opticargo

COPY --from=builder /wheels /wheels
RUN python -m pip install \
      /wheels/opticargo_shared-1.0.0-py3-none-any.whl \
      /wheels/opticargo_knowledge_graph-1.0.0-py3-none-any.whl \
    && rm -rf /wheels

WORKDIR /app
RUN mkdir -p /tmp/opticargo /app \
    && chown -R 10001:10001 /home/opticargo /tmp/opticargo /app

USER 10001:10001
EXPOSE 9100

HEALTHCHECK --interval=20s --timeout=5s --start-period=30s --retries=4 \
  CMD ["python", "-m", "opticargo_knowledge_graph.healthcheck"]

CMD ["python", "-m", "opticargo_knowledge_graph.worker"]
