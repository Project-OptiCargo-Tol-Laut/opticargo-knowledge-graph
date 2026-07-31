// src/opticargo_knowledge_graph/schema/constraints.cypher
// Constraints untuk memastikan tidak ada duplikasi node berdasarkan ID

CREATE CONSTRAINT port_id_unique IF NOT EXISTS FOR (p:Port) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT ship_id_unique IF NOT EXISTS FOR (s:Ship) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT commodity_id_unique IF NOT EXISTS FOR (c:Commodity) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT supplier_id_unique IF NOT EXISTS FOR (s:Supplier) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT voyage_id_unique IF NOT EXISTS FOR (v:Voyage) REQUIRE v.id IS UNIQUE;
CREATE CONSTRAINT route_id_unique IF NOT EXISTS FOR (r:Route) REQUIRE r.id IS UNIQUE;
