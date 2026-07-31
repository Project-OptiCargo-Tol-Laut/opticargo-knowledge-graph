from neo4j import Session
from typing import List, Dict, Any

def find_shortest_transit_path(
    session: Session,
    start_port_id: str,
    end_port_id: str,
    max_hops: int = 3
) -> List[Dict[str, Any]]:
    """
    Mencari rute transit (multi-hop) terpendek antara dua pelabuhan
    jika tidak ada kapal yang berlayar langsung.
    Menggunakan graph traversal hingga max_hops kedalaman.
    """
    
    # Pathfinding dasar di Neo4j menggunakan shortestPath()
    # Ini mensyaratkan adanya relasi yang menggambarkan rute kapal
    # Asumsikan Voyage menghubungkan port ke port (Port)-[:TERHUBUNG_DENGAN]->(Port)
    
    query = f"""
    MATCH (start:Port {{id: $start_id}}), (end:Port {{id: $end_id}})
    
    // Cari path terpendek menggunakan relasi TERHUBUNG_DENGAN dengan batas kedalaman
    MATCH p = shortestPath((start)-[:TERHUBUNG_DENGAN*1..{max_hops}]->(end))
    
    RETURN 
        [node in nodes(p) | node.name] AS port_names,
        length(p) AS total_hops
    """
    
    result = session.run(
        query, 
        start_id=start_port_id, 
        end_id=end_port_id
    )
    return [dict(record) for record in result]
