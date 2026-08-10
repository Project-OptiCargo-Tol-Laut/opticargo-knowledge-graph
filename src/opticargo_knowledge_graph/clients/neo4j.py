from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from ..projections.models import ProjectionPlan

_IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


def _identifier(value: str) -> str:
    if not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"unsafe Cypher identifier: {value!r}")
    return value


class Neo4jClient:
    """Projection-oriented Neo4j adapter with lazy driver creation."""

    def __init__(
        self,
        uri: str,
        user: str,
        password: str,
        *,
        database: str = "neo4j",
        query_timeout_seconds: float = 10,
        driver: Any | None = None,
    ) -> None:
        self._uri = uri
        self._user = user
        self._password = password
        self._database = database
        self._query_timeout_seconds = query_timeout_seconds
        self._driver = driver

    @property
    def driver(self) -> Any:
        if self._driver is None:
            from neo4j import GraphDatabase

            self._driver = GraphDatabase.driver(
                self._uri,
                auth=(self._user, self._password),
                connection_timeout=self._query_timeout_seconds,
            )
        return self._driver

    def ping(self) -> bool:
        with self.driver.session(database=self._database) as session:
            result = session.run("RETURN 1 AS ok")
            return int(result.single()["ok"]) == 1

    def run(
        self,
        query: str,
        parameters: Mapping[str, Any] | None = None,
        *,
        readonly: bool = True,
    ) -> list[dict[str, Any]]:
        params = dict(parameters or {})
        with self.driver.session(database=self._database) as session:
            execute = session.execute_read if readonly else session.execute_write

            def work(transaction: Any) -> list[dict[str, Any]]:
                # ManagedTransaction.run() accepts Cypher text, not neo4j.Query.
                # Query(timeout=...) is only valid for Session.run()/Driver.execute_query().
                result = transaction.run(query, params)
                return [dict(record) for record in result]

            # Preserve the per-transaction timeout while using managed transactions.
            # Neo4j exposes unit_of_work() specifically for execute_read/execute_write
            # transaction functions. Lightweight test environments may omit the driver.
            try:
                from neo4j import unit_of_work
            except ImportError:  # pragma: no cover - only lightweight unit-test envs
                configured_work = work
            else:
                configured_work = unit_of_work(timeout=self._query_timeout_seconds)(work)

            return list(execute(configured_work))

    def execute_statements(self, statements: Sequence[str]) -> None:
        filtered = [statement.strip() for statement in statements if statement.strip()]
        for statement in filtered:
            with self.driver.session(database=self._database) as session:
                session.run(statement).consume()

    def apply_projection(self, plan: ProjectionPlan) -> None:
        label = _identifier(plan.label)
        owner_type = plan.entity_type
        owner_id = plan.entity_id
        node_query = (
            f"MERGE (node:{label} {{id: $entity_id}}) "
            "SET node = $properties, "
            "node._projection_entity_type = $owner_type, "
            "node._source_hash = $source_hash, "
            "node._projected_at = datetime()"
        )
        clear_query = (
            "MATCH ()-[rel]->() "
            "WHERE rel._owner_entity_type = $owner_type "
            "AND rel._owner_entity_id = $owner_id DELETE rel"
        )
        with self.driver.session(database=self._database) as session:

            def work(transaction: Any) -> None:
                transaction.run(clear_query, owner_type=owner_type, owner_id=owner_id).consume()
                transaction.run(
                    node_query,
                    entity_id=owner_id,
                    properties=plan.properties,
                    owner_type=owner_type,
                    source_hash=plan.source_hash,
                ).consume()
                for relationship in plan.relationships:
                    source_label = _identifier(relationship.source.label)
                    target_label = _identifier(relationship.target.label)
                    relationship_type = _identifier(relationship.relationship_type)
                    query = (
                        f"MERGE (source:{source_label} {{id: $source_id}}) "
                        f"MERGE (target:{target_label} {{id: $target_id}}) "
                        f"MERGE (source)-[rel:{relationship_type} "
                        "{_owner_entity_type: $owner_type, _owner_entity_id: $owner_id}]->(target) "
                        "SET rel += $properties, rel._projected_at = datetime()"
                    )
                    transaction.run(
                        query,
                        source_id=relationship.source.entity_id,
                        target_id=relationship.target.entity_id,
                        owner_type=owner_type,
                        owner_id=owner_id,
                        properties=relationship.properties,
                    ).consume()

            session.execute_write(work)

    def delete_projection(self, entity_type: str, entity_id: str, label: str) -> None:
        safe_label = _identifier(label)
        clear_relationships = (
            "MATCH ()-[rel]->() WHERE rel._owner_entity_type = $entity_type "
            "AND rel._owner_entity_id = $entity_id DELETE rel"
        )
        delete_node = f"MATCH (node:{safe_label} {{id: $entity_id}}) DETACH DELETE node"
        with self.driver.session(database=self._database) as session:

            def work(transaction: Any) -> None:
                transaction.run(
                    clear_relationships,
                    entity_type=entity_type,
                    entity_id=entity_id,
                ).consume()
                transaction.run(delete_node, entity_id=entity_id).consume()

            session.execute_write(work)

    def projection_state(self, entity_type: str, label: str) -> dict[str, str]:
        safe_label = _identifier(label)
        query = (
            f"MATCH (node:{safe_label}) "
            "WHERE node._projection_entity_type = $entity_type "
            "RETURN node.id AS id, node._source_hash AS source_hash"
        )
        rows = self.run(query, {"entity_type": entity_type})
        return {str(row["id"]): str(row.get("source_hash") or "") for row in rows}

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()


def create_neo4j_driver(settings=None):
    from neo4j import GraphDatabase
    from opticargo_knowledge_graph.config import GraphSettings
    active = settings or GraphSettings.from_environment()
    return GraphDatabase.driver(active.neo4j_uri, auth=(active.neo4j_user, active.neo4j_password))
