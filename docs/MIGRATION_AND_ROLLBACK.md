# Migration and rollback

Migration berada di `src/opticargo_knowledge_graph/schema/migrations` dengan
nama `NNN_name.cypher`. Nomor wajib berurutan mulai 001 dan isi migration yang
sudah diterapkan tidak boleh diubah.

`SchemaMigrator` menyediakan:

- checksum SHA-256 per file;
- ledger `_OptiCargoSchemaMigration` berisi version, status, checksum, dan waktu;
- lock `_OptiCargoSchemaLock` dengan owner dan expiry;
- status `applying`, `applied`, atau `failed`;
- retry aman untuk statement idempotent `IF NOT EXISTS`;
- penolakan checksum drift.

Command:

```text
python -m opticargo_knowledge_graph.cli.migrate
```

Down migration destructive tidak dijalankan otomatis. Neo4j merupakan derived
store; rollback dilakukan dengan image compatible sebelumnya atau rebuild dari
PostgreSQL setelah snapshot/report disimpan. Migration 005 menyelaraskan model
relationship dengan menghapus relasi legacy `MELAYANI`.
