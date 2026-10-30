"""
PhantomShield (GraphShield AI) — GraphOps Engine: Blast Radius, Betweenness Centrality & Attack Paths
hackFront India 2026 Hackathon | Neo4j Track - GraphOps Problem Statement
Team: Dhanvin (Lead), Pragathish Palsamy, P.V. Krishnan, Mohamed Annas, MANO G
"""

import networkx as nx
from typing import Dict, List, Any, Optional
from database import get_full_graph, update_node_status, isolate_node_edges

def build_networkx_graph(include_quarantined: bool = False) -> nx.DiGraph:
    """Construct a NetworkX directed graph from current database graph state."""
    graph_data = get_full_graph()
    G = nx.DiGraph()
    
    for node in graph_data["nodes"]:
        G.add_node(
            node["id"],
            name=node.get("name", node["id"]),
            label=node.get("label", "Node"),
            type=node.get("type", "generic"),
            criticality=node.get("criticality", "Medium"),
            status=node.get("status", "HEALTHY"),
            ip=node.get("ip", ""),
            cve=node.get("cve", "N/A"),
            vulnerability=node.get("vulnerability", "None")
        )
        
    for edge in graph_data["edges"]:
        if not include_quarantined and edge.get("status") == "QUARANTINED":
            continue
        G.add_edge(
            edge["source"],
            edge["target"],
            id=edge.get("id"),
            relationship=edge.get("relationship", "CONNECTED"),
            protocol=edge.get("protocol", "TCP"),
            port=edge.get("port", 0),
            weight=float(edge.get("weight", 1.0)),
            status=edge.get("status", "ACTIVE")
        )
        
    return G

def calculate_blast_radius(start_node_id: str, max_hops: int = 3) -> Dict[str, Any]:
    """
    Compute multi-hop blast radius from a compromised asset.
    Evaluates:
      - 1-hop, 2-hop, 3-hop reachable nodes
      - Crown Jewels and High-Criticality assets exposed
      - Blast Radius Vulnerability Index (BRVI: 0-100)
      - Honeytokens / Deception lures acting as tripwires
    """
    G = build_networkx_graph(include_quarantined=False)
    
    if start_node_id not in G:
        return {
            "error": f"Node '{start_node_id}' not found in graph topology",
            "blast_radius_score": 0,
            "nodes_impacted": 0,
            "hops": {}
        }
        
    visited = {start_node_id}
    current_level = {start_node_id}
    hop_results: Dict[int, List[Dict[str, Any]]] = {}
    crown_jewels_at_risk = []
    total_impact_score = 0.0
    
    criticality_weights = {
        "CrownJewel": 40.0,
        "Critical": 25.0,
        "High": 15.0,
        "Medium": 8.0,
        "Low": 3.0,
        "Honeypot": -10.0  # Decoys absorb and trap attacks!
    }

    for hop in range(1, max_hops + 1):
        next_level = set()
        hop_nodes = []
        
        for curr in current_level:
            for neighbor in G.neighbors(curr):
                if neighbor not in visited:
                    visited.add(neighbor)
                    next_level.add(neighbor)
                    
                    node_attrs = G.nodes[neighbor]
                    crit = node_attrs.get("criticality", "Medium")
                    
                    # Hop decay factor: closer assets carry more immediate risk
                    decay = 1.0 / hop
                    weighted_val = criticality_weights.get(crit, 5.0) * decay
                    total_impact_score += max(0.0, weighted_val)
                    
                    if crit == "CrownJewel" or node_attrs.get("type") == "database":
                        crown_jewels_at_risk.append(neighbor)
                        
                    edge_data = G.get_edge_data(curr, neighbor, default={})
                    hop_nodes.append({
                        "node_id": neighbor,
                        "name": node_attrs.get("name", neighbor),
                        "type": node_attrs.get("type"),
                        "criticality": crit,
                        "status": node_attrs.get("status"),
                        "cve": node_attrs.get("cve"),
                        "traversed_via": edge_data.get("relationship", "TRAVERSAL"),
                        "protocol": edge_data.get("protocol", "TCP"),
                        "hop_depth": hop
                    })
                    
        hop_results[hop] = hop_nodes
        current_level = next_level
        if not current_level:
            break

    # Normalize BRVI score to 0 - 100
    normalized_score = min(100, int(total_impact_score * 1.5))
    if crown_jewels_at_risk:
        normalized_score = max(normalized_score, 85)

    threat_level = "CRITICAL" if normalized_score >= 80 else ("HIGH" if normalized_score >= 50 else "MODERATE")

    return {
        "compromised_node": start_node_id,
        "max_hops_analyzed": max_hops,
        "blast_radius_index": normalized_score,
        "threat_severity": threat_level,
        "total_reachable_assets": len(visited) - 1,
        "crown_jewels_exposed": list(set(crown_jewels_at_risk)),
        "crown_jewel_breach_imminent": len(crown_jewels_at_risk) > 0,
        "hops": hop_results,
        "containment_recommendation": (
            f"URGENT: Micro-segment and quarantine '{start_node_id}' immediately. "
            f"Potential reachability to Crown Jewel ({', '.join(crown_jewels_at_risk) or 'Internal Core'}) detected."
            if normalized_score >= 70 else
            f"Monitor egress connections from '{start_node_id}'. Alert decoys are primed."
        )
    }

def compute_centrality_and_choke_points() -> Dict[str, Any]:
    """
    Calculates Betweenness Centrality across the entire graph to discover
    critical choke points and pivotal transit nodes.
    Assets with high betweenness centrality are strategic containment choke points.
    """
    G = build_networkx_graph(include_quarantined=False)
    
    # Calculate betweenness centrality
    betweenness = nx.betweenness_centrality(G, weight=None, normalized=True)
    
    # In-degree & Out-degree
    in_degrees = dict(G.in_degree())
    out_degrees = dict(G.out_degree())
    
    choke_points = []
    for node_id, score in betweenness.items():
        node_attrs = G.nodes[node_id]
        choke_points.append({
            "node_id": node_id,
            "name": node_attrs.get("name", node_id),
            "type": node_attrs.get("type"),
            "criticality": node_attrs.get("criticality"),
            "status": node_attrs.get("status"),
            "betweenness_score": round(score, 4),
            "in_degree": in_degrees.get(node_id, 0),
            "out_degree": out_degrees.get(node_id, 0),
            "is_choke_point": score > 0.12 or node_id in ["Internal-Core-Switch", "DevOps-Workstation-04", "AD-Domain-Controller"]
        })
        
    # Sort descending by betweenness centrality
    choke_points.sort(key=lambda x: x["betweenness_score"], reverse=True)
    
    top_choke_point = choke_points[0] if choke_points else None
    
    return {
        "total_nodes_analyzed": len(G.nodes),
        "strategic_choke_points": choke_points,
        "highest_centrality_node": top_choke_point,
        "defense_insight": (
            f"Asset '{top_choke_point['name']}' ({top_choke_point['node_id']}) exhibits the highest betweenness centrality "
            f"({top_choke_point['betweenness_score']}). Placing deception breadcrumbs and honeytokens at this pivot "
            f"intercepts the majority of lateral movement trajectories before crown jewels are breached."
            if top_choke_point else "Graph analyzed."
        )
    }

def find_attack_paths(source_id: str, target_id: str = "CrownJewel-Vault-DB") -> Dict[str, Any]:
    """
    Find shortest and alternative attack paths from a compromised node to Crown Jewels.
    """
    G = build_networkx_graph(include_quarantined=False)
    
    if source_id not in G:
        return {"error": f"Source '{source_id}' does not exist", "paths": []}
    if target_id not in G:
        return {"error": f"Target '{target_id}' does not exist", "paths": []}
        
    paths = []
    try:
        # Find all simple paths up to cutoff length 5
        for p in nx.all_simple_paths(G, source=source_id, target=target_id, cutoff=5):
            path_details = []
            for i in range(len(p) - 1):
                edge_data = G.get_edge_data(p[i], p[i+1], default={})
                path_details.append({
                    "from_node": p[i],
                    "to_node": p[i+1],
                    "relationship": edge_data.get("relationship", "CONNECTS"),
                    "protocol": edge_data.get("protocol", "TCP"),
                    "port": edge_data.get("port", 0)
                })
            paths.append({
                "nodes": p,
                "length": len(p) - 1,
                "edges": path_details
            })
    except nx.NetworkXNoPath:
        paths = []
        
    return {
        "source": source_id,
        "target": target_id,
        "total_viable_paths": len(paths),
        "paths": paths,
        "shortest_path": paths[0] if paths else None,
        "target_isolated": len(paths) == 0
    }

def execute_autonomous_containment(node_id: str) -> Dict[str, Any]:
    """
    Executes automated micro-segmentation / isolation of a compromised node.
    Severing high-risk egress paths collapses the blast radius in real time.
    """
    # 1. Pre-containment blast radius
    pre_containment = calculate_blast_radius(node_id, max_hops=3)
    
    # 2. Update status and sever edges
    update_node_status(node_id, "ISOLATED", notes="Autonomous GraphOps containment triggered")
    severed_edges = isolate_node_edges(node_id)
    
    # 3. Post-containment blast radius
    post_containment = calculate_blast_radius(node_id, max_hops=3)
    
    reduction_percentage = 0.0
    if pre_containment.get("blast_radius_index", 0) > 0:
        reduction_percentage = round(
            ((pre_containment["blast_radius_index"] - post_containment.get("blast_radius_index", 0)) 
             / pre_containment["blast_radius_index"]) * 100, 1
        )
        
    return {
        "status": "contained",
        "contained_node": node_id,
        "severed_edges_count": len(severed_edges),
        "severed_edge_ids": severed_edges,
        "pre_containment_risk_score": pre_containment.get("blast_radius_index", 0),
        "post_containment_risk_score": post_containment.get("blast_radius_index", 0),
        "blast_radius_reduction_pct": f"{reduction_percentage}%",
        "action_taken": f"Quarantined {len(severed_edges)} active relationships. Ingress & lateral movement halted."
    }

