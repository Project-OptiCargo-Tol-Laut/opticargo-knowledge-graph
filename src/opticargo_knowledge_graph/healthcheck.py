"""CLI healthcheck entrypoint."""

from opticargo_knowledge_graph.health import readiness_report


def main() -> None:
    if readiness_report().status != "ready":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
