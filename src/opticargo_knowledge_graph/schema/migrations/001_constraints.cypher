// Remove legacy non-unique indexes created by the historical data seeder.
DROP INDEX port_id_idx IF EXISTS;
DROP INDEX supplier_id_idx IF EXISTS;
DROP INDEX commodity_id_idx IF EXISTS;
DROP INDEX voyage_id_idx IF EXISTS;
DROP INDEX ship_id_idx IF EXISTS;

CREATE CONSTRAINT opticargo_port_id IF NOT EXISTS
FOR (p:Port) REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT opticargo_supplier_id IF NOT EXISTS
FOR (s:Supplier) REQUIRE s.id IS UNIQUE;

CREATE CONSTRAINT opticargo_commodity_id IF NOT EXISTS
FOR (c:Commodity) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT opticargo_voyage_id IF NOT EXISTS
FOR (v:Voyage) REQUIRE v.id IS UNIQUE;

CREATE CONSTRAINT opticargo_ship_id IF NOT EXISTS
FOR (s:Ship) REQUIRE s.id IS UNIQUE;
