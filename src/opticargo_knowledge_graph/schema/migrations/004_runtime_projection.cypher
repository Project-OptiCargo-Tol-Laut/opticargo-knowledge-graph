CREATE CONSTRAINT opticargo_projection_event_id IF NOT EXISTS
FOR (e:_ProjectionEvent) REQUIRE e.event_id IS UNIQUE;

CREATE INDEX opticargo_voyage_status IF NOT EXISTS
FOR (v:Voyage) ON (v.status);

CREATE INDEX opticargo_supplier_verified IF NOT EXISTS
FOR (s:Supplier) ON (s.verified);

CREATE INDEX opticargo_route_relationship_id IF NOT EXISTS
FOR ()-[r:TERHUBUNG_DENGAN]-() ON (r.id);
