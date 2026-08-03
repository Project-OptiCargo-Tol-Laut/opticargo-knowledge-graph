from opticargo_knowledge_graph.health import liveness_report


def main() -> int:
    print(liveness_report())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
