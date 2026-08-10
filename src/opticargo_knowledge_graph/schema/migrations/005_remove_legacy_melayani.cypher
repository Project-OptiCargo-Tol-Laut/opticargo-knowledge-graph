// Canonical model is Ship -> Voyage -> Port. MELAYANI duplicated this path.
MATCH ()-[legacy:MELAYANI]->()
DELETE legacy;
