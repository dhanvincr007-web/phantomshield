"""
PhantomShield Test Suite
Validates Neo4j/In-Memory Graph Topology, Blast Radius, Centrality, and AI Deception Shell
"""

from database import seed_database, get_full_graph
from graph_ops import calculate_blast_radius, compute_centrality_and_choke_points, find_attack_paths, execute_autonomous_containment
from llm_sandbox import handle_deception_command

def run_tests():
    print("==================================================")
    print("PhantomShield (GraphShield AI) — GraphOps Engine Tests")
    print("==================================================")

    seed_res = seed_database()
    print(f"[+] Graph Seeding: {seed_res['status']} ({seed_res['nodes_seeded']} nodes, {seed_res['edges_seeded']} edges)")
    
    graph = get_full_graph()
    assert len(graph["nodes"]) >= 14, "Missing nodes in graph topology!"
    assert len(graph["edges"]) >= 15, "Missing relationships in graph topology!"
    print(f"[+] Topology Check Passed. Engine: {graph['engine']}")

    blast = calculate_blast_radius("DMZ-Web-Prod", max_hops=3)
    print(f"[+] Blast Radius (DMZ-Web-Prod, 3 hops): Score = {blast['blast_radius_index']}, Severity = {blast['threat_severity']}")
    assert blast['blast_radius_index'] >= 80, "Expected high blast radius for compromised DMZ node!"
    assert "CrownJewel-Vault-DB" in blast['crown_jewels_exposed'], "Crown jewel should be in blast radius!"

    centrality = compute_centrality_and_choke_points()
    top_node = centrality['highest_centrality_node']
    print(f"[+] Centrality Analysis: Top Choke Point = {top_node['name']} ({top_node['node_id']}) with score {top_node['betweenness_score']}")

    paths = find_attack_paths("DMZ-Web-Prod", "CrownJewel-Vault-DB")
    print(f"[+] Viable Attack Paths to Crown Jewel: {paths['total_viable_paths']} path(s) discovered")
    assert paths['total_viable_paths'] > 0, "Expected viable path to Crown Jewel!"

    shell_res = handle_deception_command("cat /var/backup/shadow.kdbx")
    print(f"[+] Deception Shell: Command '{shell_res['command']}' -> MITRE {shell_res['mitre_technique']['technique_id']}")
    assert shell_res['alert_triggered'], "Canary file access should trigger deception alert!"

    contain_res = execute_autonomous_containment("DMZ-Web-Prod")
    print(f"[+] Micro-Segmentation: Pre-Risk = {contain_res['pre_containment_risk_score']} -> Post-Risk = {contain_res['post_containment_risk_score']}")
    print("ALL GRAPHOPS & DECEPTION ENGINE TESTS PASSED!")

if __name__ == "__main__":
    run_tests()

