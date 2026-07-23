# opticargo-knowledge-graph

Definisi skema, query Cypher, dan script pembangunan/sinkronisasi Knowledge
Graph OptiCargo AI di Neo4j.

## Node & Relationship
Node: Ship, Port, Commodity, Distributor, Aggregator, Route, Supplier, Voyage.
Relationship kunci: `BEROPERASI_DI`, `SINGGAH_DI`, `MENYUPLAI`, `BERLOKASI_DI`,
`BERMINAT_PADA`, `TERHUBUNG_DENGAN`, `MEMBUTUHKAN`.

## Fungsi
- Skema graph (constraint, index) sebagai kode (versioned migration).
- Cypher query library untuk backhaul discovery, cargo matching, pathfinding.
- Script sinkronisasi dari data transaksional (PostgreSQL) ke Neo4j.

## Tech Stack
- Neo4j (Community Edition untuk MVP)
- Python (neo4j-driver) untuk migration & sync script

## Struktur Direktori
    /schema         → constraint & index definitions
    /migrations      → versioned graph migrations
    /queries         → Cypher query library (dipakai Graph Analysis Agent)
    /sync            → job sinkronisasi dari Postgres ke Neo4j

## Dependensi Repo Lain
- `opticargo-shared` — definisi node/edge selaras dengan tipe di service lain.
- Dipakai oleh `opticargo-agents` (Graph Analysis, Retrieval Agent) dan `opticargo-rag-pipeline`.
- Data awal dari `opticargo-data`.

## Menjalankan Lokal
    docker compose -f ../opticargo-infra/neo4j.yml up -d
    python -m sync.seed_graph