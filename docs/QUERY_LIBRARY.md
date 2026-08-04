# Typed read-only query library

Public API package `opticargo_knowledge_graph.queries`:

- `find_backhaul_graph_context`: shared `GraphContext` untuk Agents/RAG;
- `candidate_suppliers`: supplier/commodity/port discovery;
- `voyage_cargo_matches`: matching di destination voyage dengan capacity cap;
- `route_paths` dan `direct_routes`: path 1-6 hop;
- `ports_by_name` dan `nearby_ports`: lookup nama/geospatial;
- `port_supplier_counts`: supplier, commodity, voyage, dan capacity analytics.

Hasil memakai `QueryResult[T]` dan typed row seperti `SupplierMatch`,
`RouteResult`, `PortResult`, dan `PortSupplierMetric`. Seluruh query memiliki:

- value parameter binding;
- limit/hop yang di-clamp;
- timeout maksimal 30 detik;
- deterministic ordering dengan stable ID tie-breaker;
- mutation/procedure guard;
- `QueryError` typed untuk dependency failure.

Raw Cypher tidak menjadi public consumer API. Dynamic label/property/sort key
dari input pengguna dilarang.
