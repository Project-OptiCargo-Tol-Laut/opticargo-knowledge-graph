.PHONY: test smoke run

test:
	python -m pytest tests/contract/test_rag_graph_context_contract.py tests/unit/queries

smoke:
	python scripts/smoke_structure.py
	python scripts/smoke_shared.py

run:
	python -m opticargo_knowledge_graph.worker
