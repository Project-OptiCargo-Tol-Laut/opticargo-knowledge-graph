from neo4j import Session
from typing import List, Dict, Any

def find_backhaul_candidates(
    session: Session,
    voyage_id: str = None,
    origin_port: str = None,
    search_radius_km: float = 100.0,
    tolerance_days: int = 5
) -> List[Dict[str, Any]]:
    """
    Mencari peluang kargo (komoditas) untuk mengisi muatan balik kapal.
    Jika origin_port diberikan, akan mencari supplier di pelabuhan tersebut.
    """
    
    if origin_port:
        query = """
        MATCH (p:Port)
        WHERE toLower(p.name) CONTAINS toLower($origin_port)
        MATCH (s:Supplier)-[:BERLOKASI_DI]->(p)
        MATCH (s)-[:MENYUPLAI]->(c:Commodity)
        RETURN 
            s.id AS supplier_id,
            s.business_name AS supplier_name,
            c.name AS commodity_name,
            c.category AS commodity_category,
            s.avg_monthly_volume_ton AS volume,
            p.name AS port_name
        ORDER BY s.avg_monthly_volume_ton DESC
        LIMIT 50
        """
        result = session.run(query, origin_port=origin_port)
    else:
        query = """
        MATCH (v:Voyage {id: $voyage_id})
        MATCH (v)-[:SINGGAH_DI]->(p:Port) 
        MATCH (s:Supplier)-[:BERLOKASI_DI]->(p)
        MATCH (s)-[:MENYUPLAI]->(c:Commodity)
        WHERE s.avg_monthly_volume_ton <= v.remaining_capacity
        RETURN 
            s.id AS supplier_id,
            s.business_name AS supplier_name,
            c.name AS commodity_name,
            c.category AS commodity_category,
            s.avg_monthly_volume_ton AS volume,
            p.name AS port_name
        ORDER BY s.avg_monthly_volume_ton DESC
        LIMIT 50
        """
        result = session.run(query, voyage_id=voyage_id)
        
    return [dict(record) for record in result]
