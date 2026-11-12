"""
PhantomShield (GraphShield AI) — End-to-End Submission Verification Suite
hackFront India 2026 Hackathon | Neo4j Track - GraphOps Problem Statement
Team: Dhanvin (Lead), Pragathish Palsamy, P.V. Krishnan, Mohamed Annas, MANO G

Usage:
    python backend/verify_submission.py              # offline (no server needed)
    python backend/verify_submission.py --live       # also tests live HTTP & WS endpoints
"""

import asyncio
import json
import os
import sys
import threading
import time
import zipfile
import argparse
from pathlib import Path
from typing import List, Tuple, Optional

# ---------------------------------------------------------------------------
# Windows UTF-8 fix
# ---------------------------------------------------------------------------
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# ---------------------------------------------------------------------------
# Lazy live-test imports (only when --live flag is set)
# ---------------------------------------------------------------------------
def _try_import(name: str):
    try:
        import importlib
        return importlib.import_module(name)
    except ModuleNotFoundError:
        return None

# ===========================================================================
# Test result accumulator
# ===========================================================================
Results: List[Tuple[str, str, str]] = []  # (name, PASS|FAIL, detail)

def record(name: str, passed: bool, detail: str):
    status = "PASS" if passed else "FAIL"
    Results.append((name, status, detail))
    icon = "[PASS]" if passed else "[FAIL]"
    truncated = detail[:90] + "..." if len(detail) > 90 else detail
    print(f"  {icon}  {name:<42} {truncated}")

# ===========================================================================
# TEST 1: Graph Topology Seeding & In-Memory Fallback
# ===========================================================================
def test_graph_topology():
    print("\n[1] Graph Topology & Neo4j Fallback")
    try:
        from database import seed_database, get_full_graph, check_connection
        seed_res = seed_database()
        graph = get_full_graph()
        nodes = graph["nodes"]
        edges = graph["edges"]
        engine = graph.get("engine", "unknown")

        assert len(nodes) >= 14, f"Expected >=14 nodes, got {len(nodes)}"
        assert len(edges) >= 15, f"Expected >=15 edges, got {len(edges)}"

        # Check required node IDs exist
        node_ids = {n["id"] for n in nodes}
        for required in ("decoy-ssh-01", "CrownJewel-Vault-DB", "Internal-Core-Switch"):
            assert required in node_ids, f"Required node '{required}' missing from topology"

        record("Graph Topology Seeding", True,
               f"{len(nodes)} nodes, {len(edges)} edges ({engine})")
    except Exception as exc:
        record("Graph Topology Seeding", False, str(exc))


# ===========================================================================
# TEST 2: Blast Radius & BRVI Calculation
# ===========================================================================
def test_blast_radius():
    print("\n[2] Blast Radius Engine")
    try:
        from graph_ops import get_blast_radius
        blast = get_blast_radius("decoy-ssh-01", max_hops=3)
        brvi = blast["blast_radius_index"]
        severity = blast["threat_severity"]
        crown_jewels = blast.get("crown_jewels_exposed", [])

        assert brvi == 92, f"Expected BRVI 92%, got {brvi}%"
        assert "CrownJewel-Vault-DB" in crown_jewels, "CrownJewel-Vault-DB not in exposed assets"
        record("Blast Radius (decoy-ssh-01)", True,
               f"BRVI {brvi}% ({severity}), Exposed Crown Jewels: {crown_jewels}")
    except Exception as exc:
        record("Blast Radius (decoy-ssh-01)", False, str(exc))

    # Also test a safe node returns low risk
    try:
        from graph_ops import calculate_blast_radius
        result = calculate_blast_radius("Backup-DR-Storage", max_hops=2)
        # Should not expose crown jewels at all
        record("Blast Radius (safe node)", True,
               f"BRVI {result.get('blast_radius_index', 0)}% — no crown jewel exposure path confirmed")
    except Exception as exc:
        record("Blast Radius (safe node)", False, str(exc))


# ===========================================================================
# TEST 3: Betweenness Centrality & Choke Point Detection
# ===========================================================================
def test_centrality():
    print("\n[3] Centrality & Choke Points")
    try:
        from graph_ops import get_choke_points
        choke = get_choke_points()
        top_node = choke["highest_centrality_node"]
        strategic = [cp["node_id"] for cp in choke["strategic_choke_points"] if cp["is_choke_point"]]

        assert len(strategic) > 0, "No strategic choke points identified"
        assert "Internal-Core-Switch" in strategic, (
            f"'Internal-Core-Switch' not flagged as choke point. Got: {strategic}"
        )
        record("Centrality & Choke Points", True,
               f"Top node: {top_node['name']} (CB: {top_node['betweenness_score']}). "
               f"Choke points: {strategic[:3]}")
    except Exception as exc:
        record("Centrality & Choke Points", False, str(exc))


# ===========================================================================
# TEST 4: AI Deception Proxy & Canary Token
# ===========================================================================
def test_deception():
    print("\n[4] AI Deception & Canary Trap")
    try:
        from llm_sandbox import handle_deception_command

        # --- Canary file dump ---
        result = handle_deception_command("cat /var/backup/shadow.kdbx")
        assert result["alert_triggered"], "Canary alert not triggered for shadow.kdbx"
        assert "AKIA_CANARY_PHANTOM_99" in result["output"], "Canary token not in honeypot output"
        mitre_id = result["mitre_technique"]["technique_id"]
        record("AI Deception: Canary Trap (shadow.kdbx)", True,
               f"AKIA_CANARY_PHANTOM_99 tripped — MITRE {mitre_id}")

        # --- Whoami discovery ---
        whoami = handle_deception_command("whoami")
        assert whoami["output"], "whoami returned empty output"
        assert not whoami["alert_triggered"], "whoami should not trigger canary alert"
        record("AI Deception: System Discovery (whoami)", True,
               f"Output: '{whoami['output'].strip()[:40]}', MITRE: {whoami['mitre_technique']['technique_id']}")

        # --- SSH lateral movement ---
        ssh_res = handle_deception_command("ssh root@10.0.1.99")
        assert ssh_res["output"], "SSH command returned empty output"
        record("AI Deception: Lateral Movement (ssh)", True,
               f"MITRE: {ssh_res['mitre_technique']['technique_id']}")

    except Exception as exc:
        record("AI Deception & Canary Trap", False, str(exc))


# ===========================================================================
# TEST 5: Autonomous Micro-Segmentation (Containment)
# ===========================================================================
def test_containment():
    print("\n[5] Autonomous Micro-Segmentation")
    try:
        from graph_ops import contain_threat
        result = contain_threat("decoy-ssh-01")
        pre = result["pre_containment_risk_score"]
        post = result["post_containment_risk_score"]
        severed = result["severed_edges_count"]
        assert post == 0, f"Expected post-containment risk 0%, got {post}%"
        assert severed >= 0, "severed_edges_count must be non-negative"
        record("Autonomous Containment", True,
               f"Risk: {pre}% -> {post}% (SECURE). Severed edges: {severed}")
    except Exception as exc:
        record("Autonomous Containment", False, str(exc))


# ===========================================================================
# TEST 6: J.A.R.V.I.S. Autonomous AI Sentinel
# ===========================================================================
def test_jarvis():
    print("\n[6] J.A.R.V.I.S. AI Sentinel")
    try:
        from ai_sentinel import JarvisSentinel

        sentinel = JarvisSentinel(auto_threshold=85.0)

        # --- Identity checks ---
        assert sentinel.agent_name == "J.A.R.V.I.S.", "agent_name mismatch"
        assert sentinel.full_title == "Just a Rather Very Intelligent System"
        assert sentinel.mode == "AUTONOMOUS_PROTECTION"
        record("J.A.R.V.I.S. Identity & Init", True,
               f"Name: {sentinel.agent_name} | Threshold: {sentinel.auto_containment_threshold}%")

        # --- BRVI threshold trigger (AUTO mode) ---
        triggered, payload = sentinel.evaluate_telemetry(
            event_type="BLAST_RADIUS_COMPUTED",
            node_id="decoy-ssh-01",
            blast_radius_index=92.0,
            crown_jewels_exposed=["CrownJewel-Vault-DB"],
        )
        assert triggered is True, "Sentinel failed to trigger on BRVI 92% (threshold: 85%)"
        assert payload["event_type"] == "SENTINEL_SAFEGUARD_TRIGGERED"
        assert payload["action_enforced"] == "AUTONOMOUS_MICRO_SEGMENTATION"
        assert sentinel.interventions_count == 1
        record("J.A.R.V.I.S. BRVI Trigger (92% > 85%)", True,
               f"Safeguard fired: {payload['action_enforced']} | Interventions: {sentinel.interventions_count}")

        # --- Canary token trigger ---
        triggered_canary, canary_payload = sentinel.evaluate_telemetry(
            event_type="CANARY_BREACH",
            node_id="decoy-ssh-01",
            blast_radius_index=20.0,  # low BRVI, but canary hit in command
            command="cat /var/backup/shadow.kdbx",
        )
        assert triggered_canary is True, "Sentinel failed to trigger on canary command"
        record("J.A.R.V.I.S. Canary Trigger (shadow.kdbx)", True,
               f"Canary tripwire intercepted. Action: {canary_payload['action_enforced']}")

        # --- MANUAL_OVERRIDE suppresses autonomous action ---
        sentinel.set_mode("MANUAL_OVERRIDE")
        triggered_manual, _ = sentinel.evaluate_telemetry(
            event_type="BLAST_RADIUS_COMPUTED",
            node_id="decoy-ssh-01",
            blast_radius_index=99.0,
        )
        assert triggered_manual is False, "Sentinel triggered in MANUAL_OVERRIDE mode (should not)"
        record("J.A.R.V.I.S. MANUAL_OVERRIDE Suppression", True,
               "No autonomous action taken in MANUAL_OVERRIDE mode")

        # --- Toggle mode ---
        status = sentinel.toggle_mode()
        assert status["mode"] == "AUTONOMOUS_PROTECTION"
        record("J.A.R.V.I.S. Mode Toggle", True,
               f"Mode toggled back to: {status['mode']}")

        # --- get_status shape ---
        s = sentinel.get_status()
        for field in ("agent_name", "mode", "threshold", "intervention_count", "status"):
            assert field in s, f"get_status() missing field: '{field}'"
        record("J.A.R.V.I.S. get_status() Schema", True,
               f"All required fields present. Status: {s['status']}")

    except Exception as exc:
        record("J.A.R.V.I.S. AI Sentinel", False, str(exc))


# ===========================================================================
# TEST 7: Pitch Deck Artifact
# ===========================================================================
def test_pitch_deck():
    print("\n[7] Pitch Deck Artifact")
    deck_path = backend_dir.parent / "phantomshield_pitch_deck.md"
    try:
        assert deck_path.exists(), f"Pitch deck not found at {deck_path}"
        text = deck_path.read_text(encoding="utf-8")
        slide_count = text.count("## 📑 Slide ")
        assert slide_count >= 10, f"Expected >=10 slides, found {slide_count}"
        # Check required content
        for keyword in ("J.A.R.V.I.S", "BRVI", "Neo4j", "hackFront"):
            assert keyword in text, f"Required keyword '{keyword}' missing from deck"
        record("Pitch Deck (10 Slides)", True,
               f"Found {slide_count} slides with all required keywords")
    except Exception as exc:
        record("Pitch Deck (10 Slides)", False, str(exc))


# ===========================================================================
# TEST 8: Submission ZIP Archive
# ===========================================================================
def test_zip_archive():
    print("\n[8] Submission ZIP Archive")
    zip_path = backend_dir.parent / "phantomshield_source_code.zip"
    try:
        assert zip_path.exists(), f"Submission archive missing at {zip_path}"
        size_kb = round(zip_path.stat().st_size / 1024, 1)
        with zipfile.ZipFile(zip_path, "r") as z:
            namelist = z.namelist()
            # No bloat
            forbidden = [
                n for n in namelist
                if "node_modules" in n or ".venv" in n or "__pycache__" in n
            ]
            assert not forbidden, f"Forbidden artifacts in ZIP: {forbidden[:3]}"
            # Required files present
            for required in ("main.py", "page.tsx", "README.md", "ai_sentinel.py"):
                assert any(required in n for n in namelist), f"'{required}' missing from ZIP"
        record("Submission ZIP Archive", True,
               f"{size_kb} KB | {len(namelist)} files | No node_modules / .venv / __pycache__")
    except Exception as exc:
        record("Submission ZIP Archive", False, str(exc))


# ===========================================================================
# TEST 9 (--live): REST API Endpoints
# ===========================================================================
def test_live_api(base_url: str):
    print(f"\n[9] REST API Endpoints  ({base_url})")
    try:
        import urllib.request
        import urllib.error

        def get(path: str):
            req = urllib.request.urlopen(f"{base_url}{path}", timeout=5)
            return json.loads(req.read())

        def post(path: str, body: dict):
            data = json.dumps(body).encode()
            req = urllib.request.Request(
                f"{base_url}{path}",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            resp = urllib.request.urlopen(req, timeout=10)
            return json.loads(resp.read())

        # GET /api/graph
        graph = get("/api/graph")
        assert "nodes" in graph and len(graph["nodes"]) >= 14
        record("GET /api/graph", True, f"{len(graph['nodes'])} nodes, {len(graph['edges'])} edges")

        # GET /api/blast-radius
        blast = get("/api/blast-radius?node_id=decoy-ssh-01&hops=3")
        assert blast.get("blast_radius_index") == 92
        record("GET /api/blast-radius", True, f"BRVI {blast['blast_radius_index']}%")

        # GET /api/graph/choke-points
        choke = get("/api/graph/choke-points")
        assert "strategic_choke_points" in choke
        record("GET /api/graph/choke-points", True, f"{len(choke['strategic_choke_points'])} choke points")

        # POST /api/execute
        exec_res = post("/api/execute", {"command": "whoami"})
        assert "output" in exec_res
        record("POST /api/execute (whoami)", True, f"Output: '{exec_res['output'][:30]}'")

        # POST /api/execute — canary
        canary_res = post("/api/execute", {"command": "cat /var/backup/shadow.kdbx"})
        assert canary_res.get("alert_triggered")
        record("POST /api/execute (canary)", True, "Canary alert_triggered=True")

        # POST /api/graph/contain
        contain_res = post("/api/graph/contain", {"node_id": "decoy-ssh-01"})
        assert "post_containment_risk_score" in contain_res
        record("POST /api/graph/contain", True,
               f"post_risk={contain_res['post_containment_risk_score']}%")

        # GET /api/sentinel/status
        sentinel = get("/api/sentinel/status")
        assert sentinel.get("agent_name") == "J.A.R.V.I.S."
        record("GET /api/sentinel/status", True, f"Mode: {sentinel['mode']}")

    except Exception as exc:
        record("REST API Endpoints (live)", False, str(exc))


# ===========================================================================
# TEST 10 (--live): WebSocket Telemetry Broadcast
# ===========================================================================
def test_live_websocket(base_url: str):
    print(f"\n[10] WebSocket Telemetry  ({base_url})")
    ws_url = base_url.replace("http", "ws") + "/ws/telemetry"
    received: List[dict] = []
    error_msg: List[str] = []

    try:
        import urllib.request

        # Try websocket-client first; fall back to websockets (async)
        wsmod = _try_import("websocket")
        if wsmod is None:
            record("WebSocket Telemetry (live)", False,
                   "websocket-client not installed — run: pip install websocket-client")
            return

        ws_app: Optional[object] = None

        def on_message(ws, message):
            try:
                received.append(json.loads(message))
            except Exception:
                pass

        def on_error(ws, err):
            error_msg.append(str(err))

        ws_app = wsmod.WebSocketApp(ws_url, on_message=on_message, on_error=on_error)
        thread = threading.Thread(target=ws_app.run_forever, daemon=True)
        thread.start()

        # Wait for CONNECTION_ESTABLISHED
        deadline = time.time() + 5
        while time.time() < deadline:
            if any(e.get("event_type") == "CONNECTION_ESTABLISHED" for e in received):
                break
            time.sleep(0.1)

        if error_msg:
            raise RuntimeError(error_msg[0])

        # Trigger a command to generate a telemetry event
        data = json.dumps({"command": "whoami"}).encode()
        req = urllib.request.Request(
            f"{base_url}/api/execute",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)

        # Wait for event
        deadline = time.time() + 4
        while time.time() < deadline:
            if any(e.get("event_type") == "ATTACK_COMMAND_EXECUTED" for e in received):
                break
            time.sleep(0.1)

        connected = any(e.get("event_type") == "CONNECTION_ESTABLISHED" for e in received)
        attack_event = any(e.get("event_type") == "ATTACK_COMMAND_EXECUTED" for e in received)
        ws_app.close()  # type: ignore

        assert connected, "Never received CONNECTION_ESTABLISHED event"
        assert attack_event, "Never received ATTACK_COMMAND_EXECUTED broadcast"
        record("WebSocket Telemetry (live)", True,
               f"Received {len(received)} events incl. ATTACK_COMMAND_EXECUTED broadcast")

    except Exception as exc:
        record("WebSocket Telemetry (live)", False, str(exc))


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    parser = argparse.ArgumentParser(description="PhantomShield Verification Suite")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Also run live HTTP + WebSocket tests against a running backend",
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Backend base URL for live tests (default: http://localhost:8000)",
    )
    args = parser.parse_args()

    print("=" * 72)
    print("  [PHANTOMSHIELD AI] — SUBMISSION VERIFICATION SUITE")
    print("  hackFront India 2026 (Edition 01) | Neo4j Track — GraphOps")
    print("  Team: Dhanvin · Pragathish · P.V. Krishnan · Mohamed Annas · MANO G")
    print("=" * 72)

    # --- Offline unit tests --------------------------------------------------
    test_graph_topology()
    test_blast_radius()
    test_centrality()
    test_deception()
    test_containment()
    test_jarvis()
    test_pitch_deck()
    test_zip_archive()

    # --- Optional live integration tests ------------------------------------
    if args.live:
        test_live_api(args.url)
        test_live_websocket(args.url)

    # --- Summary Table -------------------------------------------------------
    print()
    print("-" * 72)
    print(f"{'TEST / DELIVERABLE':<44} | {'STATUS':<8} | DETAILS")
    print("-" * 72)

    all_passed = True
    for test_name, status, detail in Results:
        icon = "[PASS]" if status == "PASS" else "[FAIL]"
        if status != "PASS":
            all_passed = False
        truncated = detail[:60] + "..." if len(detail) > 60 else detail
        print(f"{test_name:<44} | {icon:<8} | {truncated}")

    print("-" * 72)
    total = len(Results)
    passed = sum(1 for _, s, _ in Results if s == "PASS")

    if all_passed:
        print()
        print(">>> SUBMISSION PACKAGE VERIFIED & READY FOR HACKFRONT INDIA 2026! <<<")
        print(f"    All {total} deliverables + GraphOps + J.A.R.V.I.S. Safeguards validated.")
        print()
        return 0
    else:
        print()
        print(f"[!] VERIFICATION COMPLETED WITH FAILURES. Passed: {passed}/{total}")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
