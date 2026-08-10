"""Reconciliation CLI validates destructive flags and closes the driver."""

from contextlib import nullcontext
from types import SimpleNamespace

import pytest

from opticargo_knowledge_graph import reconcile


class Driver:
    def __init__(self) -> None:
        self.closed = False

    def session(self, *, database):
        return nullcontext(object())

    def close(self):
        self.closed = True


def test_reconcile_cli_composes_report_and_cleanup(monkeypatch, capsys) -> None:
    driver = Driver()
    report = SimpleNamespace(ok=True, to_dict=lambda: {"repair": True, "entities": []})
    service = SimpleNamespace(run=lambda **kwargs: report)
    monkeypatch.setattr(reconcile, "create_neo4j_driver", lambda settings: driver)
    monkeypatch.setattr(reconcile, "Reconciler", lambda session, source: service)

    assert reconcile.main(["--repair"]) == 0
    assert driver.closed
    assert '"repair": true' in capsys.readouterr().out


def test_cleanup_stale_requires_repair() -> None:
    with pytest.raises(SystemExit) as error:
        reconcile.main(["--cleanup-stale"])
    assert error.value.code == 2
