"""
PhantomShield Test Suite
Validates Neo4j/In-Memory Graph Topology, Blast Radius, Centrality, AI Deception Shell, and Judge Simulation
"""

import sys
from database import seed_database, get_full_graph, check_connection
from graph_ops import (
    calculate_blast_radius, 
    compute_centrality_and_choke_points, 
    find_attack_paths, 
    execute_autonomous_containment,
    get_blast_radius,
    get_choke_points,
    contain_threat
)
from llm_sandbox import handle_deception_command

def run_tests():
    print("==================================================")
    print("PhantomShield (GraphShield AI) — GraphOps Engine Tests")
    print("==================================================")

    # 1. Test Seed & Graph Integrity
    seed_res = seed_database()
    print(f"[+] Graph Seeding: {seed_res['status']} ({seed_res['nodes_seeded']} nodes, {seed_res['edges_seeded']} edges)")
    
    graph = get_full_graph()
    assert len(graph["nodes"]) >= 14, "Missing nodes in graph topology!"
    assert len(graph["edges"]) >= 15, "Missing relationships in graph topology!"
    print(f"[+] Topology Check Passed. Engine: {graph['engine']}")

    # 2. Test Blast Radius Calculation & Judge Scenario Node
    blast = calculate_blast_radius("DMZ-Web-Prod", max_hops=3)
    print(f"[+] Blast Radius (DMZ-Web-Prod, 3 hops): Score = {blast['blast_radius_index']}, Severity = {blast['threat_severity']}")
    assert blast['blast_radius_index'] >= 80, "Expected high blast radius for compromised DMZ node!"
    assert "CrownJewel-Vault-DB" in blast['crown_jewels_exposed'], "Crown jewel should be in blast radius!"

    # Test Judge Scenario Decoy Node Blast Radius
    decoy_blast = get_blast_radius("decoy-ssh-01", max_hops=3)
    print(f"[+] Blast Radius (decoy-ssh-01, 3 hops): Score = {decoy_blast['blast_radius_index']}, Severity = {decoy_blast['threat_severity']}")
    assert decoy_blast['blast_radius_index'] == 92, "Expected 92% BRVI for decoy-ssh-01!"
    assert "CrownJewel-Vault-DB" in decoy_blast['crown_jewels_exposed'], "Crown jewel should be reachable from decoy pivot!"

    # 3. Test Betweenness Centrality & Choke Points
    centrality = get_choke_points()
    top_node = centrality['highest_centrality_node']
    print(f"[+] Centrality Analysis: Top Choke Point = {top_node['name']} ({top_node['node_id']}) with score {top_node['betweenness_score']}")
    choke_node_ids = [c['node_id'] for c in centrality['strategic_choke_points'] if c['is_choke_point']]
    print(f"    Identified Choke Points: {choke_node_ids}")
    assert "Internal-Core-Switch" in choke_node_ids, "Internal-Core-Switch must be recognized as choke point!"

    # 4. Test Attack Path Finding
    paths = find_attack_paths("DMZ-Web-Prod", "CrownJewel-Vault-DB")
    print(f"[+] Viable Attack Paths to Crown Jewel: {paths['total_viable_paths']} path(s) discovered")
    assert paths['total_viable_paths'] > 0, "Expected viable path to Crown Jewel!"

    # 5. Test AI Deception Shell & MITRE Tagging (Canary Dump)
    shell_res = handle_deception_command("cat /var/backup/shadow.kdbx")
    print(f"[+] Deception Shell: Command '{shell_res['command']}' -> MITRE {shell_res['mitre_technique']['technique_id']} ({shell_res['mitre_technique']['technique_name']})")
    assert shell_res['alert_triggered'], "Canary file access should trigger deception alert!"
    assert "AKIA_CANARY_PHANTOM_99" in shell_res['output'], "Canary key must appear in output!"

    # 6. Test Autonomous Micro-Segmentation
    contain_res = contain_threat("decoy-ssh-01")
    print(f"[+] Autonomous Micro-Segmentation: {contain_res['action_taken']}")
    print(f"    Pre-Risk: {contain_res['pre_containment_risk_score']} -> Post-Risk: {contain_res['post_containment_risk_score']} (Reduced by {contain_res['blast_radius_reduction_pct']})")
    assert contain_res['post_containment_risk_score'] == 0, "Risk score should collapse to 0 after containment!"

    print("==================================================")
    print("ALL 6 GRAPHOPS & JUDGE SCENARIO TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
