# Reconciliation

## Tujuan

Membuktikan Neo4j dapat direkonstruksi dari PostgreSQL dan memperbaiki event loss/drift tanpa duplicate.

## Mode

- **Check-only:** menghitung missing, mismatched, dan stale tanpa mutation.
- **Repair:** upsert missing/mismatched; optional stale cleanup sesuai policy.
- **Full rebuild:** pada graph disposable/cutover terkontrol, terapkan schema dan project seluruh canonical row.

## Lock

Redis distributed lock memakai unique token, TTL, refresh, dan owner-safe release. Job kedua gagal cepat atau menunggu sesuai policy; tidak boleh overlap diam-diam.

## Dependency order

```text
User → Port → Ship → Route → Voyage → CargoCapacity → Commodity → Supplier
→ CargoListing → Recommendation → Booking → Payment → Document → Review
```

Urutan final harus berasal dari projection registry dan digunakan test/docs, bukan disalin terpisah tanpa verification.

## Comparison

Gunakan stable projection hash dan entity ID set. Report per entity family memuat scanned, missing, mismatch, stale, repaired, deleted, failed, duration.

## Stale cleanup

- Default dan production policy harus eksplisit.
- Check report disimpan sebelum cleanup destructive.
- Cleanup tidak boleh menghapus node label di luar namespace/schema yang dimiliki repository.
- Backup/snapshot/rebuild evidence tersedia sebelum release gate.
