"""
PhantomShield (GraphShield AI) — Submission Verification Script
hackFront India 2026 Hackathon | Neo4j Track - GraphOps Problem Statement
Team: Dhanvin (Lead), Pragathish Palsamy, P.V. Krishnan, Mohamed Annas, MANO G
"""

import os
import sys
import zipfile
import asyncio
from pathlib import Path

# Configure utf-8 stdout for Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from database import seed_database, get_full_graph, check_connection
from graph_ops import (
    get_blast_radius,
    get_choke_points,
    contain_threat,
    calculate_blast_radius,
    compute_centrality_and_choke_points
)
from llm_sandbox import handle_deception_command

def run_verification():
    print("=" * 72)
    print(" [PHANTOMSHIELD AI] - SUBMISSION VERIFICATION SUITE")
    print(" hackFront India 2026 (Edition 01) | Track: Cybersecurity -> Neo4j Track")
    print("=" * 72)

    results = []

    # 1. Test Graph Seeding & Topology
    try:
        seed_res = seed_database()
        graph = get_full_graph()
        nodes_count = len(graph["nodes"])
        edges_count = len(graph["edges"])
        assert nodes_count >= 14, f"Insufficient nodes: {nodes_count}"
        assert edges_count >= 15, f"Insufficient edges: {edges_count}"
        results.append(("Graph Topology Seeding", "PASS", f"{nodes_count} nodes, {edges_count} edges ({graph['engine']})"))
    except Exception as e:
        results.append(("Graph Topology Seeding", "FAIL", str(e)))

    # 2. Test Blast Radius & Vulnerability Index
    try:
        blast = get_blast_radius("decoy-ssh-01", max_hops=3)
        brvi = blast["blast_radius_index"]
        severity = blast["threat_severity"]
        crown_jewels = blast.get("crown_jewels_exposed", [])
        assert brvi == 92, f"Expected BRVI 92%, got {brvi}%"
        assert "CrownJewel-Vault-DB" in crown_jewels, "CrownJewel-Vault-DB not exposed"
        results.append(("Blast Radius (decoy-ssh-01)", "PASS", f"BRVI {brvi}% ({severity}), Exposed: {len(crown_jewels)} jewels"))
    except Exception as e:
        results.append(("Blast Radius (decoy-ssh-01)", "FAIL", str(e)))

    # 3. Test Choke Points & Centrality
    try:
        choke = get_choke_points()
        top_node = choke["highest_centrality_node"]
        choke_points = [cp["node_id"] for cp in choke["strategic_choke_points"] if cp["is_choke_point"]]
        assert "Internal-Core-Switch" in choke_points, "Internal-Core-Switch not identified as choke point"
        results.append(("Centrality & Choke Points", "PASS", f"Top: {top_node['name']} (CB: {top_node['betweenness_score']})"))
    except Exception as e:
        results.append(("Centrality & Choke Points", "FAIL", str(e)))

    # 4. Test AI Deception & Canary Trigger
    try:
        shell_res = handle_deception_command("cat /var/backup/shadow.kdbx")
        canary_found = "AKIA_CANARY_PHANTOM_99" in shell_res["output"]
        mitre_tech = shell_res["mitre_technique"]["technique_id"]
        assert shell_res["alert_triggered"], "Canary alert not triggered"
        assert canary_found, "Canary key AKIA_CANARY_PHANTOM_99 not returned"
        results.append(("AI Deception & Canary Trap", "PASS", f"Canary AKIA_CANARY_PHANTOM_99 tripped (MITRE {mitre_tech})"))
    except Exception as e:
        results.append(("AI Deception & Canary Trap", "FAIL", str(e)))

    # 5. Test Autonomous Micro-Segmentation
    try:
        contain_res = contain_threat("decoy-ssh-01")
        pre_risk = contain_res["pre_containment_risk_score"]
        post_risk = contain_res["post_containment_risk_score"]
        assert post_risk == 0, f"Expected post-containment risk 0%, got {post_risk}%"
        results.append(("Autonomous Containment", "PASS", f"Risk collapsed: {pre_risk}% -> {post_risk}% (SECURE)"))
    except Exception as e:
        results.append(("Autonomous Containment", "FAIL", str(e)))

    # 6. Check Pitch Deck Artifact
    deck_path = backend_dir.parent / "phantomshield_pitch_deck.md"
    try:
        assert deck_path.exists(), f"Missing pitch deck at {deck_path}"
        deck_text = deck_path.read_text(encoding="utf-8")
        slide_count = deck_text.count("## 📑 Slide ")
        assert slide_count >= 10, f"Expected 10 slides, found {slide_count}"
        results.append(("Pitch Deck (10 Slides)", "PASS", f"Found {slide_count} slides at {deck_path.name}"))
    except Exception as e:
        results.append(("Pitch Deck (10 Slides)", "FAIL", str(e)))

    # 7. Check Submission Zip Archive
    zip_path = backend_dir.parent / "phantomshield_source_code.zip"
    try:
        assert zip_path.exists(), f"Missing submission archive at {zip_path}"
        file_size_kb = round(zip_path.stat().st_size / 1024, 1)
        with zipfile.ZipFile(zip_path, 'r') as z:
            namelist = z.namelist()
            # Assert no node_modules or .venv
            forbidden = [name for name in namelist if "node_modules" in name or ".venv" in name or "__pycache__" in name]
            assert len(forbidden) == 0, f"Forbidden artifacts found in zip: {forbidden[:3]}"
            # Assert critical files are present
            assert any("main.py" in n for n in namelist), "backend/main.py missing in zip"
            assert any("page.tsx" in n for n in namelist), "frontend/page.tsx missing in zip"
            assert any("README.md" in n for n in namelist), "README.md missing in zip"
        results.append(("Submission ZIP Archive", "PASS", f"{file_size_kb} KB, {len(namelist)} files (No node_modules/.venv)"))
    except Exception as e:
        results.append(("Submission ZIP Archive", "FAIL", str(e)))

    # 8. Test J.A.R.V.I.S. Autonomous AI Sentinel
    try:
        from ai_sentinel import JarvisSentinel
        test_sentinel = JarvisSentinel(auto_threshold=85.0)
        assert test_sentinel.agent_name == "J.A.R.V.I.S."
        assert test_sentinel.mode == "AUTONOMOUS_PROTECTION"
        
        # Test evaluation with high blast radius (92.0%)
        triggered, payload = test_sentinel.evaluate_telemetry(
            event_type="BLAST_RADIUS_COMPUTED",
            node_id="decoy-ssh-01",
            blast_radius_index=92.0,
            crown_jewels_exposed=["CrownJewel-Vault-DB"]
        )
        assert triggered is True, "J.A.R.V.I.S. failed to trigger safeguard on critical BRVI (92%)"
        assert payload["event_type"] == "SENTINEL_SAFEGUARD_TRIGGERED"
        assert payload["action_enforced"] == "AUTONOMOUS_MICRO_SEGMENTATION"
        
        # Test manual override mode
        test_sentinel.set_mode("MANUAL_OVERRIDE")
        triggered_override, _ = test_sentinel.evaluate_telemetry(
            event_type="BLAST_RADIUS_COMPUTED",
            node_id="decoy-ssh-01",
            blast_radius_index=95.0
        )
        assert triggered_override is False, "J.A.R.V.I.S. triggered safeguard while in MANUAL_OVERRIDE"
        
        results.append(("J.A.R.V.I.S. AI Sentinel", "PASS", "Autonomous Guard (85% BRVI threshold) & Manual Override verified"))
    except Exception as e:
        results.append(("J.A.R.V.I.S. AI Sentinel", "FAIL", str(e)))

    # Print Summary Table
    print("\n" + "-" * 72)
    print(f"{'TEST / DELIVERABLE':<32} | {'STATUS':<8} | {'DETAILS'}")
    print("-" * 72)
    all_passed = True
    for test_name, status, details in results:
        status_display = "[PASS]" if status == "PASS" else "[FAIL]"
        if status != "PASS":
            all_passed = False
        print(f"{test_name:<32} | {status_display:<8} | {details}")
    print("-" * 72)

    if all_passed:
        print("\n>>> SUBMISSION PACKAGE VERIFIED & READY FOR HACKFRONT INDIA 2026! <<<")
        print("    All 8 core deliverables, J.A.R.V.I.S. Safeguards, and GraphOps algorithms validated.\n")
        return 0
    else:
        print("\n[!] VERIFICATION COMPLETED WITH FAILURES. Review details above.\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_verification())

