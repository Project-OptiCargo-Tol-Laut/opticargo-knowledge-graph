"""Document supersession is queryable without object key or raw content."""

import os
from uuid import uuid4

import pytest

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.projections import ProjectionService, default_projection_registry
from tests.e2e.helpers import DictSource, cleanup_entities, project

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_E2E") != "1",
    reason="requires explicit disposable Neo4j E2E runtime",
)


def test_document_supersession_relationship_and_sensitive_exclusion() -> None:
    uploader, old_document, new_document = (str(uuid4()) for _ in range(3))
    source = DictSource()
    source.put(
        "user",
        {
            "id": uploader,
            "role": "operator",
            "is_active": True,
            "created_at": "2026-01-01T00:00:00+00:00",
        },
    )
    common = {
        "booking_id": None,
        "uploaded_by": uploader,
        "doc_type": "regulation",
        "issuer": "Synthetic Authority",
        "effective_date": "2026-01-01",
        "source_reference": "SYNTHETIC",
        "is_superseded": False,
        "ingestion_status": "indexed",
    }
    source.put(
        "document",
        {
            **common,
            "id": old_document,
            "title": "Policy v1",
            "document_version": "1",
            "supersedes_document_id": None,
        },
    )
    source.put(
        "document",
        {
            **common,
            "id": new_document,
            "title": "Policy v2",
            "document_version": "2",
            "supersedes_document_id": old_document,
        },
    )
    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    service = ProjectionService(default_projection_registry(), source)
    try:
        with driver.session(database=settings.neo4j_database) as session:
            project(session, service, "user", uploader)
            project(session, service, "document", old_document)
            project(session, service, "document", new_document)
            result = session.run(
                """
                MATCH (new:Document {id: $new})-[:SUPERSEDES]->
                      (old:Document {id: $old})
                RETURN properties(new) AS properties
                """,
                new=new_document,
                old=old_document,
            ).single(strict=True)
            assert result is not None
            assert "object_key" not in result["properties"]
            assert "content" not in result["properties"]
            cleanup_entities(session, [uploader, old_document, new_document])
    finally:
        driver.close()
