"""Migration CLI selects the configured database and always closes the driver."""

from contextlib import nullcontext

from opticargo_knowledge_graph.cli import migrate
from opticargo_knowledge_graph.config import GraphSettings


class Driver:
    def __init__(self) -> None:
        self.database = None
        self.closed = False
        self.session_value = object()

    def session(self, *, database):
        self.database = database
        return nullcontext(self.session_value)

    def close(self):
        self.closed = True


def test_migrate_cli_applies_and_closes(monkeypatch, capsys) -> None:
    driver = Driver()
    monkeypatch.setattr(migrate, "build_driver_from_env", lambda: driver)
    monkeypatch.setattr(
        GraphSettings,
        "from_environment",
        classmethod(lambda cls: GraphSettings(neo4j_database="tenant")),
    )
    monkeypatch.setattr(migrate, "apply_migrations", lambda session: 3)

    assert migrate.main() == 0
    assert driver.database == "tenant"
    assert driver.closed
    assert "Applied 3" in capsys.readouterr().out
