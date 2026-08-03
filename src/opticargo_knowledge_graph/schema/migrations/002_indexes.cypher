CREATE INDEX opticargo_port_name IF NOT EXISTS
FOR (p:Port) ON (p.name);

CREATE INDEX opticargo_supplier_business_name IF NOT EXISTS
FOR (s:Supplier) ON (s.business_name);

CREATE INDEX opticargo_commodity_name IF NOT EXISTS
FOR (c:Commodity) ON (c.name);

CREATE INDEX opticargo_voyage_route_id IF NOT EXISTS
FOR (v:Voyage) ON (v.route_id);
