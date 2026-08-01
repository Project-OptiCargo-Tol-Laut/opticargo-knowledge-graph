# Security and Data Boundary

## Source access

PostgreSQL credential untuk graph runtime bersifat read-only. Migration Neo4j credential dapat dipisahkan dari query consumer credential.

## Projection allowlist

Setiap entity builder menyebut property yang diizinkan. Generic row-to-property copy dilarang.

## Data yang dilarang

Password/token/secret, raw payment provider payload/card data, document content/object credential, AuditLog detail, Notification payload, unnecessary email/phone/address/PII.

## Query safety

Value diparameterkan. Dynamic identifier hanya dari registry allowlist dan divalidasi sebagai identifier. Natural-language input tidak menjadi Cypher.

## DLQ/log/metric

Gunakan sanitized error class dan reference. Jangan menyimpan full event/canonical row bila mengandung data sensitif.

## Network

Worker/job/package internal-only; Neo4j Bolt tidak diberi public ingress. Frontend/browser tidak mengakses Neo4j.
