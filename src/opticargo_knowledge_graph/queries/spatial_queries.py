from neo4j import Session
from typing import List, Dict, Any

def find_suppliers_in_radius(
    session: Session,
    port_id: str,
    radius_km: float = 50.0
) -> List[Dict[str, Any]]:
    """
    Mencari supplier yang berada dalam radius tertentu dari sebuah pelabuhan.
    Menggunakan fitur Point() dan distance() Neo4j.
    """
    
    query = """
    MATCH (p:Port {id: $port_id})
    MATCH (s:Supplier)
    
    // Pastikan keduanya memiliki properti point location
    WHERE p.location IS NOT NULL AND s.location IS NOT NULL
    
    // Hitung jarak (dalam meter, jadi dikali 1000)
    WITH p, s, distance(p.location, s.location) AS dist
    WHERE dist <= ($radius_km * 1000)
    
    RETURN 
        s.id AS supplier_id,
        s.name AS supplier_name,
        s.region AS supplier_region,
        dist / 1000 AS distance_km
    ORDER BY dist ASC
    """
    
    result = session.run(query, port_id=port_id, radius_km=radius_km)
    return [dict(record) for record in result]
