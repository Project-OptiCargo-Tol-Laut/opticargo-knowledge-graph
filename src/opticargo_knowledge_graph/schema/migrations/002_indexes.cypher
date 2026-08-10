CREATE INDEX port_city IF NOT EXISTS FOR (node:Port) ON (node.city);
CREATE INDEX port_coordinates IF NOT EXISTS FOR (node:Port) ON (node.latitude, node.longitude);
CREATE INDEX ship_status IF NOT EXISTS FOR (node:Ship) ON (node.status);
CREATE INDEX route_active IF NOT EXISTS FOR (node:Route) ON (node.is_active);
CREATE INDEX voyage_status IF NOT EXISTS FOR (node:Voyage) ON (node.status);
CREATE INDEX voyage_departure IF NOT EXISTS FOR (node:Voyage) ON (node.departure_date);
CREATE INDEX commodity_category IF NOT EXISTS FOR (node:Commodity) ON (node.category);
CREATE INDEX supplier_verified IF NOT EXISTS FOR (node:Supplier) ON (node.verified);
CREATE INDEX cargo_listing_status IF NOT EXISTS FOR (node:CargoListing) ON (node.status);
CREATE INDEX cargo_listing_available_from IF NOT EXISTS
FOR (node:CargoListing) ON (node.available_from);
CREATE INDEX cargo_listing_available_until IF NOT EXISTS
FOR (node:CargoListing) ON (node.available_until);
CREATE INDEX booking_status IF NOT EXISTS FOR (node:Booking) ON (node.status);
CREATE INDEX payment_status IF NOT EXISTS FOR (node:Payment) ON (node.status);
CREATE INDEX document_type IF NOT EXISTS FOR (node:Document) ON (node.doc_type);
CREATE INDEX document_effective_date IF NOT EXISTS FOR (node:Document) ON (node.effective_date);
