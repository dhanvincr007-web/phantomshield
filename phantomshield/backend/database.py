"""
PhantomShield (GraphShield AI) — Neo4j Database Connection & Cypher Seed Scripts
hackFront India 2026 Hackathon | Neo4j Track - GraphOps Problem Statement
Team: Dhanvin (Lead), Pragathish Palsamy, P.V. Krishnan, Mohamed Annas, MANO G
"""

import os
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("phantomshield.database")
logging.basicConfig(level=logging.INFO)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "phantomshield2026")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# In-memory mock store fallback when Neo4j is not reachable locally
IN_MEMORY_NODES: Dict[str, Dict[str, Any]] = {}
IN_MEMORY_EDGES: List[Dict[str, Any]] = []

INITIAL_TOPOLOGY_NODES = [
    {
        "id": "Internet-Gateway",
        "name": "Edge Border Gateway",
        "label": "Gateway",
        "type": "gateway",
        "ip": "198.51.100.1",
        "os": "VyOS Linux Edge",
        "criticality": "Medium",
        "status": "HEALTHY",
        "vulnerability": "None (Hardened)",
        "cve": "N/A",
        "description": "Perimeter ingress router handling corporate edge traffic"
    },
    {
        "id": "DMZ-Web-Prod",
        "name": "DMZ Public Web App",
        "label": "Server",
        "type": "server",
        "ip": "10.0.1.10",
        "os": "Ubuntu 22.04 LTS (NGINX)",
        "criticality": "High",
        "status": "COMPROMISED",
        "vulnerability": "Remote Code Execution",
        "cve": "CVE-2024-21413",
        "description": "Initial compromised ingress vector exploited via SSRF & deserialization"
    },
    {
        "id": "API-Gateway-01",
        "name": "Internal Microservices Gateway",
        "label": "Server",
        "type": "server",
        "ip": "10.0.1.20",
        "os": "Alpine Linux (Kong API)",
        "criticality": "High",
        "status": "HEALTHY",
        "vulnerability": "JWT Weak Secret",
        "cve": "CVE-2023-38035",
        "description": "Routes inbound customer and microservice REST payloads"
    },
    {
        "id": "Auth-Service-OAuth",
        "name": "Corporate SSO / Keycloak",
        "label": "AuthServer",
        "type": "server",
        "ip": "10.0.2.15",
        "os": "Debian 12 (Keycloak IAM)",
        "criticality": "Critical",
        "status": "HEALTHY",
        "vulnerability": "Privilege Escalation in OIDC Plugin",
        "cve": "CVE-2023-40028",
        "description": "Primary identity federation provider for internal microservices"
    },
    {
        "id": "Internal-Core-Switch",
        "name": "Core Layer-3 Switch (VLAN 10/20)",
        "label": "Switch",
        "type": "switch",
        "ip": "10.0.2.1",
        "os": "Cisco NX-OS",
        "criticality": "Critical",
        "status": "HEALTHY",
        "vulnerability": "CDP Stack Overflow",
        "cve": "CVE-2020-3118",
        "description": "Critical bridge choke point routing traffic between DMZ and LAN"
    },
    {
        "id": "DevOps-Workstation-04",
        "name": "Lead Architect Workstation",
        "label": "Workstation",
        "type": "workstation",
        "ip": "10.0.3.45",
        "os": "Windows 11 Enterprise",
        "criticality": "High",
        "status": "HEALTHY",
        "vulnerability": "Unquoted Service Path",
        "cve": "CVE-2023-36884",
        "description": "Contains cached AWS credentials and SSH jump keys"
    },
    {
        "id": "Production-K8s-Cluster",
        "name": "Prod Kubernetes Control Plane",
        "label": "Cluster",
        "type": "server",
        "ip": "10.0.4.10",
        "os": "Ubuntu 22.04 (k8s v1.28)",
        "criticality": "Critical",
        "status": "HEALTHY",
        "vulnerability": "API Ingress Path Traversal",
        "cve": "CVE-2023-5044",
        "description": "Hosts core revenue transaction processing pods"
    },
    {
        "id": "AD-Domain-Controller",
        "name": "AD Primary DC (CORP.LOCAL)",
        "label": "DomainController",
        "type": "domain_controller",
        "ip": "10.0.0.5",
        "os": "Windows Server 2022",
        "criticality": "Critical",
        "status": "HEALTHY",
        "vulnerability": "Zerologon RPC Relay",
        "cve": "CVE-2020-1472",
        "description": "Kerberos Key Distribution Center and Active Directory forest root"
    },
    {
        "id": "CrownJewel-Vault-DB",
        "name": "Crown Jewel: Secrets & PII Vault",
        "label": "CrownJewel",
        "type": "database",
        "ip": "10.0.0.50",
        "os": "RHEL 9 (HashiCorp Vault & PG-Crypto)",
        "criticality": "CrownJewel",
        "status": "HEALTHY",
        "vulnerability": "None (MFA Enforced)",
        "cve": "N/A",
        "description": "Ultimate target containing customer PII, encryption root keys, and financial ledger"
    },
    {
        "id": "Backup-DR-Storage",
        "name": "Immutable Cold Backup Array",
        "label": "Storage",
        "type": "storage",
        "ip": "10.0.5.100",
        "os": "TrueNAS Enterprise ZFS",
        "criticality": "High",
        "status": "HEALTHY",
        "vulnerability": "Outdated SSH Cipher Suite",
        "cve": "N/A",
        "description": "Air-gapped replica storage target"
    },
    # AI Deception Honey Traps
    {
        "id": "Honey-Bastion-SSH",
        "name": "Decoy Jumpbox (Honey-Bastion)",
        "label": "Honeypot",
        "type": "honeypot",
        "ip": "10.0.1.99",
        "os": "Alpine Linux (AI Emulated Shell)",
        "criticality": "Honeypot",
        "status": "DECOY",
        "vulnerability": "Default Root Credential Trap",
        "cve": "T1078.001",
        "description": "High-interaction deceptive SSH proxy equipped with AI prompt deception"
    },
    {
        "id": "HoneyToken-AdminKey",
        "name": "HoneyToken: AWS_ROOT_ACCESS_KEY",
        "label": "HoneyToken",
        "type": "honeytoken",
        "ip": "Virtual Decoy",
        "os": "Decoy Credential",
        "criticality": "Honeypot",
        "status": "DECOY",
        "vulnerability": "Simulated Leaked Cloud IAM Token",
        "cve": "T1552.001",
        "description": "Planted credential in /tmp and environment variables alerting when referenced"
    },
    {
        "id": "Honey-CRM-Database",
        "name": "Decoy CRM Database (Fake Leads)",
        "label": "Honeypot",
        "type": "honeypot",
        "ip": "10.0.2.99",
        "os": "MySQL 8.0 Decoy Container",
        "criticality": "Honeypot",
        "status": "DECOY",
        "vulnerability": "SQL Injection Trap",
        "cve": "T1190",
        "description": "Simulated synthetic database serving watermarked honeypot rows"
    },
    {
        "id": "Canary-File-Passwd",
        "name": "Canary: /var/backup/shadow.kdbx",
        "label": "Canary",
        "type": "canary",
        "ip": "File Artifact",
        "os": "Canary Breadcrumb",
        "criticality": "Honeypot",
        "status": "DECOY",
        "vulnerability": "Breadcrumb Trailing to Honey-CRM",
        "cve": "T1083",
        "description": "Planted KeePass database file alerting on read or file extraction attempts"
    }
]

INITIAL_TOPOLOGY_EDGES = [
    {"id": "e1", "source": "Internet-Gateway", "target": "DMZ-Web-Prod", "relationship": "ROUTES_TRAFFIC_TO", "protocol": "HTTPS", "port": 443, "weight": 1.0, "status": "ACTIVE"},
    {"id": "e2", "source": "Internet-Gateway", "target": "Honey-Bastion-SSH", "relationship": "ROUTES_TRAFFIC_TO", "protocol": "SSH", "port": 2222, "weight": 0.5, "status": "DECEPTIVE"},
    {"id": "e3", "source": "DMZ-Web-Prod", "target": "API-Gateway-01", "relationship": "CONNECTS_TO", "protocol": "mTLS", "port": 8443, "weight": 1.5, "status": "ACTIVE"},
    {"id": "e4", "source": "API-Gateway-01", "target": "Auth-Service-OAuth", "relationship": "AUTHENTICATES_VIA", "protocol": "OIDC", "port": 8080, "weight": 2.0, "status": "ACTIVE"},
    {"id": "e5", "source": "DMZ-Web-Prod", "target": "Internal-Core-Switch", "relationship": "CROSSES_SUBNET", "protocol": "TCP", "port": 0, "weight": 3.0, "status": "ACTIVE"},
    {"id": "e6", "source": "Internal-Core-Switch", "target": "DevOps-Workstation-04", "relationship": "CONNECTS_TO", "protocol": "RDP", "port": 3389, "weight": 2.5, "status": "ACTIVE"},
    {"id": "e7", "source": "DevOps-Workstation-04", "target": "Production-K8s-Cluster", "relationship": "ADMIN_ACCESS", "protocol": "KUBECTL", "port": 6443, "weight": 3.5, "status": "ACTIVE"},
    {"id": "e8", "source": "DMZ-Web-Prod", "target": "Canary-File-Passwd", "relationship": "CONTAINS_CANARY", "protocol": "LOCAL_FS", "port": 0, "weight": 0.2, "status": "DECEPTIVE"},
    {"id": "e9", "source": "Honey-Bastion-SSH", "target": "HoneyToken-AdminKey", "relationship": "LEADS_TO_TRAP", "protocol": "TOKEN_READ", "port": 0, "weight": 0.1, "status": "DECEPTIVE"},
    {"id": "e10", "source": "Canary-File-Passwd", "target": "Honey-CRM-Database", "relationship": "REFERENCES_DECOY", "protocol": "DB_CONN", "port": 3306, "weight": 0.4, "status": "DECEPTIVE"},
    {"id": "e11", "source": "Internal-Core-Switch", "target": "AD-Domain-Controller", "relationship": "LATERAL_MOVEMENT_PATH", "protocol": "SMB/RPC", "port": 445, "weight": 4.0, "status": "ACTIVE"},
    {"id": "e12", "source": "DevOps-Workstation-04", "target": "AD-Domain-Controller", "relationship": "PIVOT_EXPLOIT", "protocol": "WINRM", "port": 5985, "weight": 3.8, "status": "ACTIVE"},
    {"id": "e13", "source": "AD-Domain-Controller", "target": "CrownJewel-Vault-DB", "relationship": "CONTROLS_DATA", "protocol": "LDAP_SYNC", "port": 636, "weight": 5.0, "status": "ACTIVE"},
    {"id": "e14", "source": "Production-K8s-Cluster", "target": "CrownJewel-Vault-DB", "relationship": "QUERIES_SECRETS", "protocol": "VAULT_REST", "port": 8200, "weight": 4.5, "status": "ACTIVE"},
    {"id": "e15", "source": "CrownJewel-Vault-DB", "target": "Backup-DR-Storage", "relationship": "REPLICATES_TO", "protocol": "ZFS_SEND", "port": 9000, "weight": 1.2, "status": "ACTIVE"}
]

driver = None

def get_neo4j_driver():
    """Lazily initialize and return the Neo4j driver, or None if unavailable."""
    global driver
    if driver is not None:
        return driver
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD),
            max_connection_lifetime=30 * 60,
            max_connection_pool_size=50,
            connection_acquisition_timeout=2.0
        )
        with driver.session(database=NEO4J_DATABASE) as session:
            session.run("RETURN 1 AS test")
        logger.info(f"Connected successfully to Neo4j instance at {NEO4J_URI}")
        return driver
    except Exception as e:
        logger.warning(f"Neo4j instance offline or unreachable ({e}). Using high-fidelity In-Memory Graph Engine.")
        driver = None
        return None

def check_connection() -> Dict[str, Any]:
    """Check connectivity to Neo4j database."""
    drv = get_neo4j_driver()
    if drv is not None:
        try:
            with drv.session(database=NEO4J_DATABASE) as session:
                res = session.run("RETURN 1 AS connected").single()
                if res and res["connected"] == 1:
                    return {"status": "connected", "mode": "neo4j_native", "uri": NEO4J_URI}
        except Exception as e:
            return {"status": "degraded", "mode": "in_memory_simulation", "error": str(e)}
    return {"status": "active_in_memory", "mode": "in_memory_simulation", "nodes_count": len(IN_MEMORY_NODES)}

def seed_database():
    """Seed the graph database with full cyber topology and AI deception nodes."""
    global IN_MEMORY_NODES, IN_MEMORY_EDGES
    
    IN_MEMORY_NODES = {node["id"]: dict(node) for node in INITIAL_TOPOLOGY_NODES}
    IN_MEMORY_EDGES = [dict(edge) for edge in INITIAL_TOPOLOGY_EDGES]
    
    drv = get_neo4j_driver()
    if drv is not None:
        try:
            with drv.session(database=NEO4J_DATABASE) as session:
                session.run("MATCH (n) DETACH DELETE n")
                for node in INITIAL_TOPOLOGY_NODES:
                    cypher_node = f"""
                    CREATE (n:{node['label']} {{
                        id: $id,
                        name: $name,
                        label: $label,
                        type: $type,
                        ip: $ip,
                        os: $os,
                        criticality: $criticality,
                        status: $status,
                        vulnerability: $vulnerability,
                        cve: $cve,
                        description: $description
                    }})
                    """
                    session.run(cypher_node, **node)
                
                for edge in INITIAL_TOPOLOGY_EDGES:
                    cypher_edge = f"""
                    MATCH (source {{id: $source_id}}), (target {{id: $target_id}})
                    CREATE (source)-[r:{edge['relationship']} {{
                        id: $edge_id,
                        protocol: $protocol,
                        port: $port,
                        weight: $weight,
                        status: $status
                    }}]->(target)
                    """
                    session.run(
                        cypher_edge,
                        source_id=edge["source"],
                        target_id=edge["target"],
                        edge_id=edge["id"],
                        protocol=edge["protocol"],
                        port=edge["port"],
                        weight=edge["weight"],
                        status=edge["status"]
                    )
                logger.info(f"Neo4j seeded successfully with {len(INITIAL_TOPOLOGY_NODES)} nodes and {len(INITIAL_TOPOLOGY_EDGES)} edges.")
        except Exception as e:
            logger.error(f"Failed to seed Neo4j: {e}. In-memory graph ready.")
    else:
        logger.info(f"In-memory graph seeded with {len(IN_MEMORY_NODES)} nodes and {len(IN_MEMORY_EDGES)} edges.")

    return {
        "status": "success",
        "nodes_seeded": len(IN_MEMORY_NODES),
        "edges_seeded": len(IN_MEMORY_EDGES),
        "target_crown_jewel": "CrownJewel-Vault-DB"
    }

def get_full_graph() -> Dict[str, Any]:
    """Retrieve all nodes and edges for the graph visualizer."""
    drv = get_neo4j_driver()
    if drv is not None:
        try:
            with drv.session(database=NEO4J_DATABASE) as session:
                result = session.run("""
                MATCH (n)
                OPTIONAL MATCH (n)-[r]->(m)
                RETURN n, r, m
                """)
                nodes_dict = {}
                edges_list = []
                for record in result:
                    n = record["n"]
                    if n and n.get("id"):
                        nodes_dict[n["id"]] = dict(n)
                    r = record["r"]
                    m = record["m"]
                    if r and m and m.get("id"):
                        edges_list.append({
                            "id": r.get("id", f"{n['id']}->{m['id']}"),
                            "source": n["id"],
                            "target": m["id"],
                            "relationship": type(r).__name__ if not hasattr(r, "type") else r.type,
                            "protocol": r.get("protocol", "TCP"),
                            "port": r.get("port", 0),
                            "weight": r.get("weight", 1.0),
                            "status": r.get("status", "ACTIVE")
                        })
                return {
                    "nodes": list(nodes_dict.values()),
                    "edges": edges_list,
                    "engine": "Neo4j Cypher Native"
                }
        except Exception as e:
            logger.warning(f"Error querying Neo4j graph: {e}. Fallback to in-memory store.")
    
    return {
        "nodes": list(IN_MEMORY_NODES.values()),
        "edges": list(IN_MEMORY_EDGES),
        "engine": "In-Memory Graph Engine"
    }

def update_node_status(node_id: str, new_status: str, notes: Optional[str] = None) -> bool:
    """Update status of a node (e.g. COMPROMISED, ISOLATED, PROBED)."""
    global IN_MEMORY_NODES
    if node_id in IN_MEMORY_NODES:
        IN_MEMORY_NODES[node_id]["status"] = new_status
        if notes:
            IN_MEMORY_NODES[node_id]["last_alert"] = notes

    drv = get_neo4j_driver()
    if drv is not None:
        try:
            with drv.session(database=NEO4J_DATABASE) as session:
                session.run("""
                MATCH (n {id: $node_id})
                SET n.status = $status
                """, node_id=node_id, status=new_status)
        except Exception as e:
            logger.warning(f"Failed to update Neo4j node {node_id}: {e}")

    return True

def isolate_node_edges(node_id: str) -> List[str]:
    """Quarantine node by severing/marking all incident edges as QUARANTINED."""
    global IN_MEMORY_EDGES
    severed_edge_ids = []
    for edge in IN_MEMORY_EDGES:
        if edge["source"] == node_id or edge["target"] == node_id:
            edge["status"] = "QUARANTINED"
            severed_edge_ids.append(edge["id"])
            
    drv = get_neo4j_driver()
    if drv is not None:
        try:
            with drv.session(database=NEO4J_DATABASE) as session:
                session.run("""
                MATCH (n {id: $node_id})-[r]-(m)
                SET r.status = 'QUARANTINED'
                """, node_id=node_id)
        except Exception as e:
            logger.warning(f"Failed to isolate edges in Neo4j for {node_id}: {e}")

    return severed_edge_ids

if not IN_MEMORY_NODES:
    seed_database()

