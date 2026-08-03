from opticargo_knowledge_graph.reconciliation import reconcile_once


def main() -> int:
    print(reconcile_once())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
