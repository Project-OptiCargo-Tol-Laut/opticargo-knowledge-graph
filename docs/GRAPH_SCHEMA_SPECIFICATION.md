# Graph Schema Specification

## Canonical labels

```text
User, Port, Ship, Route, Voyage, CargoCapacity, Commodity, Supplier,
CargoListing, Recommendation, Booking, Payment, Document, Review
```

## Canonical relationships

```text
Ship            -[:OPERATED_BY]-> User
Route           -[:ORIGIN_PORT]-> Port
Route           -[:DESTINATION_PORT]-> Port
Port            -[:ROUTE_TO]-> Port
Voyage          -[:USES_SHIP]-> Ship
Voyage          -[:FOLLOWS_ROUTE]-> Route
Voyage          -[:DEPARTS_FROM]-> Port
Voyage          -[:ARRIVES_AT]-> Port
Voyage          -[:HAS_CAPACITY]-> CargoCapacity
CargoCapacity   -[:FOR_VOYAGE]-> Voyage
Supplier        -[:OWNED_BY]-> User
Supplier        -[:LOCATED_AT]-> Port
Supplier        -[:SUPPLIES]-> Commodity
CargoListing    -[:LISTED_BY]-> Supplier
CargoListing    -[:OF_COMMODITY]-> Commodity
CargoListing    -[:ORIGINATES_AT]-> Port
CargoListing    -[:DESTINED_FOR]-> Port
Recommendation  -[:FOR_VOYAGE]-> Voyage
Recommendation  -[:REQUESTED_BY]-> User
Booking         -[:RESERVES_VOYAGE]-> Voyage
Booking         -[:BOOKS_LISTING]-> CargoListing
Booking         -[:CREATED_BY]-> User
Booking         -[:BASED_ON_RECOMMENDATION]-> Recommendation
Payment         -[:PAYS_FOR]-> Booking
Document        -[:UPLOADED_BY]-> User
Document        -[:ATTACHED_TO_BOOKING]-> Booking
Document        -[:SUPERSEDES]-> Document
Review          -[:FOR_BOOKING]-> Booking
Review          -[:WRITTEN_BY]-> User
Review          -[:REVIEWS_USER]-> User
```

## Projection metadata

Setiap canonical node minimal membutuhkan stable `id`, entity/schema metadata, source hash, dan projected timestamp. Nama property final harus ditetapkan pada schema contract dan diuji backward compatibility.

Setiap owned relationship membutuhkan owner entity type/ID agar update satu entity dapat menghapus relationship lama dan membuat ulang relationship canonical tanpa meninggalkan edge stale.

## Excluded data

- `RagChunk`, embedding, dan raw document content.
- Notification payload dan AuditLog detail.
- Password hash, refresh token, provider secret/token.
- Raw card/payment provider payload atau reference yang tidak dibutuhkan analytics.
- Document object key/storage credential.
- PII yang tidak diperlukan untuk discovery/analytics.

## Constraint/index

Unique stable ID constraint harus tersedia untuk canonical label. Index hanya dibuat bila digunakan projection/query dan dibuktikan melalui query plan/performance test. Full-text index memerlukan ADR terpisah mengenai field, analyzer, locale, dan rebuild.
