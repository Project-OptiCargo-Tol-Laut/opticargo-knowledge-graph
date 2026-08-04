from opticargo_knowledge_graph.reconciliation import Reconciler


class Result:
    def __init__(self, rows=(), single=None):
        self.rows = list(rows)
        self.single_value = single

    def __iter__(self):
        return iter(self.rows)

    def single(self):
        return self.single_value

    def consume(self):
        return None


class Session:
    def run(self, query, **parameters):
        if "ReconciliationLock" in query and "RETURN lock.owner" in query:
            return Result(single={"owner": parameters["owner"]})
        return Result()


class Source:
    def fetch_all(self, entity_type):
        if entity_type == "port":
            return [
                {
                    "id": "port-1",
                    "name": "Ambon",
                    "city": "Ambon",
                    "province": "Maluku",
                    "latitude": -3.7,
                    "longitude": 128.1,
                    "max_vessel_tonnage": 1000,
                }
            ]
        return []


def test_reconciliation_detects_missing_source_projection() -> None:
    report = Reconciler(Session(), Source(), owner="test").run(repair=False)

    assert report.scanned == 1
    assert report.drift == 1
    port_report = next(item for item in report.entities if item.entity_type == "port")
    assert port_report.missing == 1
    assert report.ok is False


def test_reconciliation_repairs_missing_projection() -> None:
    reconciler = Reconciler(Session(), Source(), owner="test")

    class Service:
        def project_record(self, *args, **kwargs):
            return type("Projection", (), {"status": "projected"})()

    reconciler._service = Service()
    report = reconciler.run(repair=True)

    assert report.projected == 1
    assert report.failed == 0
    assert report.ok is True
