// Stable IDs make every projection idempotent and reconstructable.
CREATE CONSTRAINT graph_migration_key IF NOT EXISTS
FOR (node:GraphMigration) REQUIRE (node.schema_name, node.version) IS UNIQUE;
CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (node:User) REQUIRE node.id IS UNIQUE;
CREATE CONSTRAINT port_id_unique IF NOT EXISTS FOR (node:Port) REQUIRE node.id IS UNIQUE;
CREATE CONSTRAINT ship_id_unique IF NOT EXISTS FOR (node:Ship) REQUIRE node.id IS UNIQUE;
CREATE CONSTRAINT route_id_unique IF NOT EXISTS FOR (node:Route) REQUIRE node.id IS UNIQUE;
CREATE CONSTRAINT voyage_id_unique IF NOT EXISTS FOR (node:Voyage) REQUIRE node.id IS UNIQUE;
CREATE CONSTRAINT cargo_capacity_id_unique IF NOT EXISTS
FOR (node:CargoCapacity) REQUIRE node.id IS UNIQUE;
CREATE CONSTRAINT commodity_id_unique IF NOT EXISTS FOR (node:Commodity) REQUIRE node.id IS UNIQUE;
CREATE CONSTRAINT supplier_id_unique IF NOT EXISTS FOR (node:Supplier) REQUIRE node.id IS UNIQUE;
CREATE CONSTRAINT cargo_listing_id_unique IF NOT EXISTS
FOR (node:CargoListing) REQUIRE node.id IS UNIQUE;
CREATE CONSTRAINT recommendation_id_unique IF NOT EXISTS
FOR (node:Recommendation) REQUIRE node.id IS UNIQUE;
CREATE CONSTRAINT booking_id_unique IF NOT EXISTS FOR (node:Booking) REQUIRE node.id IS UNIQUE;
CREATE CONSTRAINT payment_id_unique IF NOT EXISTS FOR (node:Payment) REQUIRE node.id IS UNIQUE;
CREATE CONSTRAINT document_id_unique IF NOT EXISTS FOR (node:Document) REQUIRE node.id IS UNIQUE;
CREATE CONSTRAINT review_id_unique IF NOT EXISTS FOR (node:Review) REQUIRE node.id IS UNIQUE;
