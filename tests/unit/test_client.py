from opticargo_knowledge_graph.client import KnowledgeGraphClient, get_session


def test_get_session_export_exists() -> None:
    assert get_session


def test_knowledge_graph_client_uses_driver_session() -> None:
    calls: list[str] = []
    databases: list[str] = []

    class Result:
        def single(self):
            return None

        def __iter__(self):
            return iter(())

    class Session:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

        def run(self, *args, **kwargs):
            calls.append("run")
            return Result()

    class Driver:
        def session(self, *, database):
            databases.append(database)
            return Session()

    context = KnowledgeGraphClient(Driver()).graph_context(origin_port="Ambon")

    assert calls
    assert databases == ["neo4j"]
    assert context.candidates == []
