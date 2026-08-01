# Projection Model

## Event-to-projection flow

1. Decode Redis fields.
2. Validasi event envelope/version melalui Shared.
3. Tentukan target entity dan change type menggunakan allowlist registry.
4. Untuk create/update/status event, baca row canonical PostgreSQL.
5. Builder menghasilkan immutable projection plan: label, stable ID, graph-safe properties, owned relationships, source hash.
6. Neo4j adapter menjalankan idempotent write transaction.
7. Worker mencatat terminal outcome, processed key, metric, dan ACK.

## Canonical lookup

Event payload tidak menjadi row final. Replay event lama harus membaca state PostgreSQL terbaru agar graph tidak kembali ke snapshot usang.

## Relationship replacement

Update entity menghapus relationship yang owner metadata-nya menunjuk entity tersebut, lalu membuat relationship plan baru dalam satu transaction. Incoming relationship yang dimiliki entity lain tidak boleh ikut dihapus.

## Placeholder target node

`MERGE` target stable ID dapat membuat node minimal ketika dependency belum diproyeksikan. Saat target entity diproyeksikan, property canonical melengkapi node tersebut. Placeholder semantics harus diuji agar label/property tidak mengaburkan missing canonical row.

## Delete

Delete event atau missing canonical row dengan delete semantics yang sah menghapus owned relationship dan node entity. Missing row pada update biasa tidak boleh otomatis dianggap delete tanpa contract.

## Hash

Hash dihitung dari normalized property dan relationship plan, bukan timestamp projection. Reconciliation menggunakan hash yang sama dengan worker. Perubahan algorithm membutuhkan schema/version decision agar mismatch massal dapat dijelaskan.
