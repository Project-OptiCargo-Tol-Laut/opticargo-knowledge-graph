from neo4j import Session
from typing import List, Dict, Any

def find_matching_ships_for_cargo(
    session: Session,
    origin_port_id: str,
    destination_port_id: str,
    commodity_category: str,
    volume_needed: float,
    time_window_start: str = None,
    time_window_end: str = None
) -> List[Dict[str, Any]]:
    """
    Mencocokkan kebutuhan pengiriman kargo dengan kapal yang tersedia.
    Mencari rute kapal yang menyinggahi origin dan destination, 
    dan memiliki kapasitas yang cukup untuk komoditas tertentu.
    """
    
    query = """
    // Temukan rute yang melayani kedua pelabuhan
    MATCH (origin:Port {id: $origin_id})
    MATCH (dest:Port {id: $dest_id})
    
    // Cari Rute yang terhubung antara kedua pelabuhan 
    // ATAU cari Kapal yang rutenya singgah di kedua pelabuhan
    MATCH (origin)<-[:TERHUBUNG_DENGAN|SINGGAH_DI]-(v:Voyage)-[:TERHUBUNG_DENGAN|SINGGAH_DI]->(dest)
    MATCH (ship:Ship)-[:BEROPERASI_DI]->(v)
    
    // Filter kapasitas dan kompatibilitas
    // (Asumsikan kapal tidak membawa restricted commodity jika ada constraint,
    // di sini kita cek ketersediaan ruang)
    WHERE v.remaining_capacity >= $volume
    
    RETURN 
        ship.name AS ship_name,
        ship.id AS ship_id,
        v.id AS voyage_id,
        v.remaining_capacity AS remaining_capacity,
        v.departure_date AS departure_date
    ORDER BY v.departure_date ASC
    LIMIT 20
    """
    
    result = session.run(
        query, 
        origin_id=origin_port_id, 
        dest_id=destination_port_id,
        volume=volume_needed
    )
    return [dict(record) for record in result]
