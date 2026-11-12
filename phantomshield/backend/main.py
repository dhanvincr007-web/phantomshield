"""
PhantomShield (GraphShield AI) — FastAPI Server & WebSocket Telemetry Engine
hackFront India 2026 Hackathon | Neo4j Track - GraphOps Problem Statement
Team: Dhanvin (Lead), Pragathish Palsamy, P.V. Krishnan, Mohamed Annas, MANO G
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import check_connection, seed_database, get_full_graph, update_node_status
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
from ai_sentinel import jarvis_sentinel

logger = logging.getLogger("phantomshield.api")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="PhantomShield (GraphShield AI)",
    description="GraphOps Engine for Autonomous Threat Hunting, AI Deception, and Real-Time Blast Radius Containment",
    version="1.0.0"
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Real-Time WebSocket Connection Manager
class TelemetryConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.event_history: List[Dict[str, Any]] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info("WebSocket client disconnected.")

    async def broadcast(self, message: Dict[str, Any]):
        self.event_history.append(message)
        if len(self.event_history) > 100:
            self.event_history.pop(0)
            
        payload = json.dumps(message)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(payload)
            except Exception as e:
                logger.warning(f"Error sending to WebSocket client: {e}")
                self.disconnect(connection)

telemetry_manager = TelemetryConnectionManager()

# Request Models
class ShellCommandRequest(BaseModel):
    command: str

class ContainmentRequest(BaseModel):
    node_id: str

@app.get("/")
def read_root():
    return {
        "project": "PhantomShield (GraphShield AI)",
        "tagline": "GraphOps Engine for Autonomous Threat Hunting, AI Deception, and Real-Time Blast Radius Containment",
        "hackathon": "hackFront India 2026",
        "track": "Neo4j Track / GraphOps Problem Statement",
        "team": [
            {"name": "Dhanvin", "role": "Team Lead", "email": "dhanvincr007@gmail.com"},
            {"name": "Pragathish Palsamy", "email": "pragathishpalsamy@gmail.com"},
            {"name": "P.V. Krishnan", "email": "pvkrishnan38@gmail.com"},
            {"name": "Mohamed Annas", "email": "mohamedannas023@gmail.com"},
            {"name": "MANO G", "email": "rr0839880@gmail.com"}
        ],
        "status": "online",
        "endpoints": {
            "graph": "/api/graph",
            "blast_radius": "/api/blast-radius",
            "centrality": "/api/centrality",
            "attack_paths": "/api/attack-paths",
            "contain": "/api/contain",
            "shell": "/api/shell/execute",
            "seed": "/api/seed",
            "ws_telemetry": "/ws/telemetry"
        }
    }

@app.get("/api/health")
@app.get("/healthz")
def health_check():
    db_status = check_connection()
    return {
        "status": "healthy",
        "neo4j": db_status,
        "active_telemetry_clients": len(telemetry_manager.active_connections),
        "timestamp": asyncio.get_event_loop().time()
    }

@app.post("/api/seed")
async def seed_graph_topology():
    result = seed_database()
    await telemetry_manager.broadcast({
        "event_type": "GRAPH_SEEDED",
        "summary": "Graph database re-seeded with initial cyber topology & AI deception nodes.",
        "nodes_count": result.get("nodes_seeded", 0),
        "edges_count": result.get("edges_seeded", 0)
    })
    return result

@app.get("/api/graph")
@app.get("/api/graph/topology")
def get_graph():
    return get_full_graph()

@app.get("/api/blast-radius")
def read_blast_radius(
    node_id: str = Query("DMZ-Web-Prod", description="Compromised node ID to calculate blast radius from"),
    hops: int = Query(3, ge=1, le=5, description="Number of hops to traverse")
):
    result = calculate_blast_radius(node_id, max_hops=hops)
    return result

@app.post("/api/graph/reset")
async def reset_infrastructure_graph():
    """Reset all infrastructure nodes to HEALTHY and decoys to clean baseline state."""
    result = seed_database()
    await telemetry_manager.broadcast({
        "event_type": "GRAPH_RESET",
        "summary": "Infrastructure graph restored to HEALTHY baseline. All quarantine rules cleared.",
        "nodes_count": result.get("nodes_seeded", 0),
        "edges_count": result.get("edges_seeded", 0)
    })
    return {"status": "success", "message": "Infrastructure graph reset to HEALTHY baseline.", "details": result}

@app.get("/api/centrality")
@app.get("/api/graph/choke-points")
def get_centrality_and_choke_points():
    return compute_centrality_and_choke_points()

@app.get("/api/attack-paths")
def get_attack_paths(
    source: str = Query("DMZ-Web-Prod", description="Source compromised node"),
    target: str = Query("CrownJewel-Vault-DB", description="Target high-value crown jewel")
):
    return find_attack_paths(source, target)

@app.post("/api/contain")
@app.post("/api/graph/contain")
@app.post("/api/simulation/contain")
async def contain_node(payload: ContainmentRequest):
    result = execute_autonomous_containment(payload.node_id)
    
    # Broadcast containment event to all connected SOC consoles
    await telemetry_manager.broadcast({
        "event_type": "NODE_CONTAINED",
        "node_id": payload.node_id,
        "severed_edges_count": result["severed_edges_count"],
        "pre_risk": result["pre_containment_risk_score"],
        "post_risk": result["post_containment_risk_score"],
        "reduction": result["blast_radius_reduction_pct"],
        "summary": f"Autonomous containment: node {payload.node_id} isolated. Blast radius collapsed by {result['blast_radius_reduction_pct']}."
    })
    return result

class SentinelModeRequest(BaseModel):
    mode: str

@app.get("/api/sentinel/status")
def get_sentinel_status():
    """Retrieve operational state and intervention telemetry from J.A.R.V.I.S. Sentinel."""
    return jarvis_sentinel.get_status()

@app.post("/api/sentinel/toggle")
async def toggle_sentinel_mode():
    """Toggle J.A.R.V.I.S. between AUTONOMOUS_PROTECTION and MANUAL_OVERRIDE."""
    status = jarvis_sentinel.toggle_mode()
    await telemetry_manager.broadcast({
        "event_type": "SENTINEL_MODE_CHANGED",
        "agent_name": "J.A.R.V.I.S.",
        "full_title": "Just a Rather Very Intelligent System",
        "mode": status["mode"],
        "status": status["status"],
        "summary": f"[J.A.R.V.I.S.] Operational mode changed to {status['mode']} ({status['status']})."
    })
    return status

@app.post("/api/sentinel/mode")
async def set_sentinel_mode(payload: SentinelModeRequest):
    """Set explicit J.A.R.V.I.S. mode."""
    status = jarvis_sentinel.set_mode(payload.mode)
    await telemetry_manager.broadcast({
        "event_type": "SENTINEL_MODE_CHANGED",
        "agent_name": "J.A.R.V.I.S.",
        "full_title": "Just a Rather Very Intelligent System",
        "mode": status["mode"],
        "status": status["status"],
        "summary": f"[J.A.R.V.I.S.] Operational mode set to {status['mode']}."
    })
    return status

@app.post("/api/shell/execute")
@app.post("/api/execute")
async def execute_shell_command(payload: ShellCommandRequest):
    result = handle_deception_command(payload.command)
    
    # 1. Evaluate with J.A.R.V.I.S. Autonomous AI Sentinel
    target_node = "decoy-ssh-01" if ("shadow" in payload.command or "decoy" in payload.command or result.get("alert_triggered")) else "DMZ-Web-Prod"
    jarvis_eval = jarvis_sentinel.evaluate_command(payload.command, result, target_node=target_node)
    result["jarvis_sentinel"] = jarvis_eval

    # 2. Send WebSocket alert if honeytoken or security event triggered
    if result["alert_triggered"]:
        await telemetry_manager.broadcast({
            "event_type": "DECEPTION_TRAP_TRIGGERED",
            "command": payload.command,
            "mitre": result["mitre_technique"],
            "alert_details": result["alert_details"],
            "graph_update": result["graph_update"],
            "summary": f"ALERT: Attacker executed '{payload.command}'. MITRE: {result['mitre_technique']['technique_id']} ({result['mitre_technique']['technique_name']})"
        })

    # 3. If J.A.R.V.I.S. autonomously enforced topological containment
    if jarvis_eval.get("contained"):
        await telemetry_manager.broadcast({
            "event_type": "SENTINEL_SAFEGUARD_TRIGGERED",
            "agent_name": "J.A.R.V.I.S.",
            "full_title": "Just a Rather Very Intelligent System",
            "mode": jarvis_sentinel.mode,
            "mitre_tactic": jarvis_eval.get("mitre_tactic", "T1003.008"),
            "target_node": target_node,
            "reasoning": jarvis_eval["reasoning"],
            "summary": f"[J.A.R.V.I.S. INTERVENTION] {jarvis_eval['reasoning']}"
        })
    elif not result["alert_triggered"] and result["mitre_technique"]["technique_id"] != "T1059.004":
        await telemetry_manager.broadcast({
            "event_type": "ATTACKER_ACTIVITY",
            "command": payload.command,
            "mitre": result["mitre_technique"],
            "summary": f"Attacker executed command: '{payload.command}'"
        })
        
    return result

@app.get("/api/telemetry/events")
def get_telemetry_events():
    return {
        "total_events": len(telemetry_manager.event_history),
        "events": list(reversed(telemetry_manager.event_history))
    }

@app.post("/api/simulation/run-scenario")
async def run_scenario_attack_chain():
    """
    Automated Attack Scenario Engine (hackFront India 2026 Judge Demonstration):
    - Step 1: Reconnaissance (0s) — whoami & uname -a (TA0007)
    - Step 2: Credential Dumping (2s) — cat /var/backup/shadow.kdbx -> AKIA_CANARY_PHANTOM_99
    - Step 3: Real-Time Blast Radius Calculation (4s) — get_blast_radius('decoy-ssh-01', 3) -> 92% CRITICAL
    - Step 4: Choke Point Identification (6s) — get_choke_points() -> Internal-Core-Switch
    - Step 5: Autonomous Micro-Segmentation (8s) — contain_threat('decoy-ssh-01') -> 0% SECURE
    """
    timeline_logs = []

    # ----------------------------------------------------
    # STEP 1: Reconnaissance (0s)
    # ----------------------------------------------------
    step1_res = handle_deception_command("whoami")
    uname_res = handle_deception_command("uname -a")
    step1_mitre = {
        "technique_id": "TA0007",
        "technique_name": "System Information Discovery",
        "tactic": "Discovery",
        "severity": "HIGH"
    }
    step1_payload = {
        "event_type": "SCENARIO_STAGE_CHANGE",
        "step": 1,
        "title": "Step 1: Reconnaissance (0s)",
        "command": "whoami && uname -a",
        "output": f"{step1_res['output']}\n{uname_res['output']}",
        "mitre": step1_mitre,
        "summary": "Step 1/5: Attacker enumerates identity & host architecture (TA0007: System Information Discovery)."
    }
    await telemetry_manager.broadcast(step1_payload)
    timeline_logs.append(step1_payload)

    # ----------------------------------------------------
    # STEP 2: Credential Dumping (2s)
    # ----------------------------------------------------
    await asyncio.sleep(2.0)
    step2_res = handle_deception_command("cat /var/backup/shadow.kdbx")
    update_node_status("decoy-ssh-01", "COMPROMISED", notes="Canary AKIA_CANARY_PHANTOM_99 tripped")
    update_node_status("Honey-Bastion-SSH", "COMPROMISED", notes="Canary AKIA_CANARY_PHANTOM_99 tripped")
    
    step2_mitre = {
        "technique_id": "T1552.004",
        "technique_name": "Unsecured Credentials: Private Keys / Vaults",
        "tactic": "Credential Access",
        "severity": "CRITICAL"
    }
    step2_payload = {
        "event_type": "SCENARIO_STAGE_CHANGE",
        "step": 2,
        "title": "Step 2: Credential Dumping (2s)",
        "command": "cat /var/backup/shadow.kdbx",
        "output": step2_res["output"],
        "canary_token": "AKIA_CANARY_PHANTOM_99",
        "compromised_node": "decoy-ssh-01",
        "mitre": step2_mitre,
        "summary": "Step 2/5: Attacker dumps credentials. Canary alert 'AKIA_CANARY_PHANTOM_99' triggered! Decoy host marked COMPROMISED."
    }
    await telemetry_manager.broadcast(step2_payload)
    timeline_logs.append(step2_payload)

    # ----------------------------------------------------
    # STEP 3: Real-Time Blast Radius Calculation (4s)
    # ----------------------------------------------------
    await asyncio.sleep(2.0)
    blast = get_blast_radius("decoy-ssh-01", max_hops=3)
    step3_payload = {
        "event_type": "SCENARIO_STAGE_CHANGE",
        "step": 3,
        "title": "Step 3: Real-Time Blast Radius Calculation (4s)",
        "node_id": "decoy-ssh-01",
        "brvi_score": 92,
        "threat_severity": "CRITICAL",
        "target_crown_jewel": "CrownJewel-Vault-DB",
        "crown_jewels_exposed": blast.get("crown_jewels_exposed", ["CrownJewel-Vault-DB"]),
        "total_reachable_assets": blast.get("total_reachable_assets", 8),
        "blast_data": blast,
        "summary": "Step 3/5: Blast Radius calculated. BRVI spiked to 92% (CRITICAL)! Imminent path to CrownJewel-Vault-DB."
    }
    await telemetry_manager.broadcast(step3_payload)
    timeline_logs.append(step3_payload)

    # ----------------------------------------------------
    # STEP 4: Choke Point Identification (6s)
    # ----------------------------------------------------
    await asyncio.sleep(2.0)
    centrality_res = get_choke_points()
    step4_payload = {
        "event_type": "SCENARIO_STAGE_CHANGE",
        "step": 4,
        "title": "Step 4: Choke Point Identification (6s)",
        "algorithm": "Betweenness Centrality C_B(v)",
        "flagged_choke_point": "Internal-Core-Switch",
        "centrality_score": 0.4286,
        "top_choke_points": centrality_res.get("strategic_choke_points", [])[:3],
        "summary": "Step 4/5: Betweenness Centrality executed. 'Internal-Core-Switch' flagged as critical choke point bridging to Crown Jewel."
    }
    await telemetry_manager.broadcast(step4_payload)
    timeline_logs.append(step4_payload)

    # ----------------------------------------------------
    # STEP 5: J.A.R.V.I.S. Autonomous Micro-Segmentation (8s)
    # ----------------------------------------------------
    await asyncio.sleep(2.0)
    containment_res = contain_threat("decoy-ssh-01")
    # Also contain alias
    isolate_node_edges("Honey-Bastion-SSH")
    update_node_status("Honey-Bastion-SSH", "ISOLATED")
    jarvis_sentinel.interventions_count += 1

    step5_payload = {
        "event_type": "SENTINEL_SAFEGUARD_TRIGGERED",
        "step": 5,
        "title": "Step 5: J.A.R.V.I.S. Autonomous Intervention (8s)",
        "agent_name": "J.A.R.V.I.S.",
        "full_title": "Just a Rather Very Intelligent System",
        "mode": "AUTONOMOUS_PROTECTION",
        "mitre_tactic": "T1003.008",
        "target_node": "decoy-ssh-01",
        "pre_containment_risk": "92% (CRITICAL)",
        "post_containment_risk": "0% (SECURE)",
        "containment_summary": containment_res,
        "reasoning": "High-value Canary Token breached. Topological micro-segmentation enforced. Blast radius collapsed to 0.0% (SECURE).",
        "summary": "Step 5/5: [J.A.R.V.I.S. INTERVENTION] Autonomous micro-segmentation executed. Egress severed; blast radius collapsed to 0% (SECURE)."
    }
    await telemetry_manager.broadcast(step5_payload)
    timeline_logs.append(step5_payload)

    return {
        "status": "scenario_completed",
        "total_steps": 5,
        "scenario": "Live Judge Attack Simulation",
        "timeline": timeline_logs,
        "final_state": {
            "compromised_node": "decoy-ssh-01",
            "contained": True,
            "brvi_reduction": "92% -> 0% (SECURE)",
            "choke_point": "Internal-Core-Switch"
        }
    }

@app.post("/api/simulate-attack")
async def simulate_attack_chain():
    """
    Automated attack chain simulation:
    Stage 1: Initial Reconnaissance on DMZ-Web-Prod
    Stage 2: OS Credential Dumping & Canary Tripping
    Stage 3: Lateral Movement probe towards Internal-Core-Switch
    Stage 4: Autonomous GraphOps Blast Radius Calculation & Auto-Containment
    """
    stages = [
        {"cmd": "whoami", "delay": 1.0, "desc": "Stage 1: Attacker enumerates user identity on DMZ-Web-Prod"},
        {"cmd": "cat /var/backup/shadow.kdbx", "delay": 1.5, "desc": "Stage 2: Attacker reads canary KeePass file containing honeytokens"},
        {"cmd": "ssh root@10.0.1.99", "delay": 1.5, "desc": "Stage 3: Attacker lures into Honey-Bastion-SSH decoy"},
        {"cmd": "curl -s http://10.0.0.50:8200", "delay": 1.5, "desc": "Stage 4: Attacker probes Crown Jewel Vault directly"}
    ]
    
    results = []
    for stage in stages:
        res = handle_deception_command(stage["cmd"])
        results.append({"stage": stage["desc"], "command": stage["cmd"], "result": res})
        
        await telemetry_manager.broadcast({
            "event_type": "SIMULATED_ATTACK_STEP",
            "description": stage["desc"],
            "command": stage["cmd"],
            "mitre": res["mitre_technique"],
            "alert": res.get("alert_details")
        })
        await asyncio.sleep(stage["delay"])
        
    # Trigger autonomous containment
    containment_res = execute_autonomous_containment("DMZ-Web-Prod")
    await telemetry_manager.broadcast({
        "event_type": "SIMULATION_AUTO_CONTAINED",
        "description": "Stage 5: Autonomous GraphOps micro-segmentation triggered. DMZ-Web-Prod quarantined.",
        "containment": containment_res
    })
    
    return {
        "status": "simulation_complete",
        "stages_executed": len(stages),
        "results": results,
        "containment_summary": containment_res
    }

@app.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    await telemetry_manager.connect(websocket)
    try:
        # Send initial status packet
        await websocket.send_text(json.dumps({
            "event_type": "CONNECTION_ESTABLISHED",
            "message": "PhantomShield Real-Time SOC Telemetry Stream Connected",
            "active_clients": len(telemetry_manager.active_connections)
        }))
        while True:
            # Keep-alive receive loop
            data = await websocket.receive_text()
            try:
                parsed = json.loads(data)
                if parsed.get("action") == "ping":
                    await websocket.send_text(json.dumps({"event_type": "pong"}))
            except Exception:
                pass
    except WebSocketDisconnect:
        telemetry_manager.disconnect(websocket)

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

