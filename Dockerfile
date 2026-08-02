FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/workspace/opticargo-shared/src:/workspace/opticargo-knowledge-graph/src

WORKDIR /workspace

COPY opticargo-shared ./opticargo-shared
COPY opticargo-knowledge-graph ./opticargo-knowledge-graph

RUN python -m pip install --upgrade pip \
    && python -m pip install ./opticargo-shared ./opticargo-knowledge-graph

CMD ["python", "-m", "opticargo_knowledge_graph.worker"]
