// src/opticargo_knowledge_graph/schema/indexes.cypher
// Index untuk mempercepat pencarian (B-Tree dan Spatial Point Index)

// Pencarian berdasarkan nama entitas
CREATE INDEX port_name_idx IF NOT EXISTS FOR (p:Port) ON (p.name);
CREATE INDEX ship_name_idx IF NOT EXISTS FOR (s:Ship) ON (s.name);
CREATE INDEX commodity_name_idx IF NOT EXISTS FOR (c:Commodity) ON (c.name);

// Filter berdasarkan kategori
CREATE INDEX commodity_category_idx IF NOT EXISTS FOR (c:Commodity) ON (c.category);
CREATE INDEX ship_type_idx IF NOT EXISTS FOR (s:Ship) ON (s.ship_type);

// Pencarian berdasarkan wilayah
CREATE INDEX port_region_idx IF NOT EXISTS FOR (p:Port) ON (p.region);
CREATE INDEX supplier_region_idx IF NOT EXISTS FOR (s:Supplier) ON (s.region);

// SPATIAL INDEX: Untuk koordinat latitude dan longitude
// Anggap port memiliki properti location berupa tipe Point Neo4j.
// Di seed script, properti ini biasanya digenerate, tapi kita buat index-nya di sini.
CREATE POINT INDEX port_location_idx IF NOT EXISTS FOR (p:Port) ON (p.location);
CREATE POINT INDEX supplier_location_idx IF NOT EXISTS FOR (s:Supplier) ON (s.location);
