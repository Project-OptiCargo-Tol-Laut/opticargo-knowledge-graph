import os
from neo4j import GraphDatabase, Driver
from typing import Optional

class Neo4jClient:
    _instance: Optional['Neo4jClient'] = None

    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "opticargo123")
        
        self.driver: Driver = GraphDatabase.driver(uri, auth=(user, password))

    @classmethod
    def get_instance(cls) -> 'Neo4jClient':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def close(self):
        if self.driver:
            self.driver.close()

def get_session():
    """Returns a Neo4j session from the singleton driver."""
    client = Neo4jClient.get_instance()
    return client.driver.session()
