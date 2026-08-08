# Reconciliation PostgreSQL-Neo4j

Reconciliation membandingkan ID dan `_source_checksum` untuk Port, Ship,
Commodity, Route, Supplier, dan active Voyage. Urutan dependency merupakan
`port -> ship -> commodity -> route -> supplier -> voyage`.

Mode:

- default: check-only, tidak memutasi graph;
- `--repair`: upsert missing/mismatched;
- `--repair --cleanup-stale`: juga menghapus projection yang tidak lagi ada di
  PostgreSQL.

Job menggunakan `_OptiCargoReconciliationLock` di Neo4j sehingga dua job tidak
berjalan bersamaan. Report JSON memuat source/graph count, missing, mismatched,
stale, projected, deleted, failed, dan durasi.

```text
python -m opticargo_knowledge_graph.reconcile
python -m opticargo_knowledge_graph.reconcile --repair
python -m opticargo_knowledge_graph.reconcile --repair --cleanup-stale
```

Exit code 0 berarti tidak ada kegagalan dan, untuk check-only, tidak ada drift.
Exit code 2 berarti drift ditemukan atau repair gagal. Cleanup harus dijalankan
setelah report check-only ditinjau dan backup/rebuild source tersedia.
