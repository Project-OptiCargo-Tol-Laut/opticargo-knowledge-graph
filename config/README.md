# Configuration

## File

| File | Fungsi |
|---|---|
| `infra.example.env` | Salinan acuan environment dan port dari repository Infra yang diberikan. Nilai di dalamnya tidak otomatis menjadi secret atau konfigurasi produksi. |
| `knowledge-graph.env.example` | Daftar variable yang diperlukan runtime Knowledge Graph. Nilai sengaja kosong agar keputusan tidak ditebak. |

## Aturan endpoint

- Koneksi antar-container menggunakan service name dan internal port: PostgreSQL `5432`, Redis `6379`, Neo4j Bolt `7687`.
- Host port hanya digunakan oleh tooling/operator dari host. Acuan yang diberikan memetakan PostgreSQL ke `5433` dan Neo4j HTTP ke `7474`.
- Tidak ada public ingress untuk graph worker atau reconciliation job.
- Port metrics graph worker harus dialokasikan pada Infra sebelum digunakan; implementasi referensi memakai default internal `9100`, tetapi acuan Infra tidak menetapkan host mapping khusus untuk port tersebut.

## Secret

Example value tidak boleh dipakai di production. Password, token, dan URI berisi credential harus berasal dari secret manager atau mekanisme Infra yang disepakati.
