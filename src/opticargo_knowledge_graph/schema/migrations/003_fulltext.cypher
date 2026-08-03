CREATE FULLTEXT INDEX opticargo_document_lookup IF NOT EXISTS
FOR (d:Document) ON EACH [d.title, d.issuer, d.source_reference];

CREATE FULLTEXT INDEX opticargo_port_supplier_lookup IF NOT EXISTS
FOR (n:Port|Supplier|Commodity) ON EACH [n.name, n.business_name];
