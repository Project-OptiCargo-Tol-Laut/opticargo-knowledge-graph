# Typed Query Library

## Public capabilities

### Backhaul discovery

Input voyage atau origin port, radius, schedule tolerance, dan limit. Hasil hanya memuat listing aktif dalam lokasi/waktu yang valid serta capacity fit yang dapat dibuktikan.

### Cargo matching

Input origin, destination, commodity/category, volume/weight, time window, compatibility/certification, dan limit. Hard constraint harus berada dalam query atau filter deterministik yang diuji.

### Pathfinding

Input start/end port dan bounded max hops. Gunakan canonical `ROUTE_TO`; tidak ada traversal tak terbatas atau dynamic Cypher dari user text.

### Spatial

Input port/radius/limit. Coordinate missing/invalid menghasilkan typed behavior. Unit jarak eksplisit.

### Analytics

Graph overview, corridor load, transaction lifecycle, dan underserved supplier. Formula network analytics dan underserved perlu keputusan product/data sebelum implementasi final.

## Contract result

- Typed model dan versioned field.
- Stable entity IDs.
- Unit eksplisit.
- Deterministic order/tie-breaker.
- Empty result berbeda dari dependency failure.
- Query timeout dan validation error memiliki typed error.
- Consumer test terhadap Agents/RAG.

## Safety

Value menggunakan parameter. Label, relationship, property, index, sort key, dan hop bound berasal dari allowlist, bukan string arbitrary.
