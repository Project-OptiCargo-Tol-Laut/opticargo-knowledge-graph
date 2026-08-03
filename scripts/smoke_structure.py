from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    required = ["src/opticargo_knowledge_graph/worker.py", "compose.graph.yml", "src/opticargo_knowledge_graph/schema"]
    missing = [item for item in required if not (root / item).exists()]
    if missing:
        print({"missing": missing})
        return 1
    print({"status": "ok", "repo": "opticargo-knowledge-graph"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
