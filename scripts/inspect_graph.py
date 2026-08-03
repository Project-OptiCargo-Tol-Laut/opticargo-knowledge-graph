from opticargo_knowledge_graph.health import readiness_report


def main() -> int:
    print(readiness_report().to_dict())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
