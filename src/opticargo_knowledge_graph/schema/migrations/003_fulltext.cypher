CREATE FULLTEXT INDEX opticargo_entity_search IF NOT EXISTS
FOR (node:Port|Ship|Commodity|Supplier|Document)
ON EACH [node.name, node.business_name, node.title, node.city, node.province, node.issuer];
