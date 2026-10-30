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
    execute_autonomous_containment
)
from llm_sandbox import handle_deception_command

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
def get_graph():
    return get_full_graph()

@app.get("/api/blast-radius")
def get_blast_radius(
    node_id: str = Query("DMZ-Web-Prod", description="Compromised node ID to calculate blast radius from"),
    hops: int = Query(3, ge=1, le=5, description="Number of hops to traverse")
):
    result = calculate_blast_radius(node_id, max_hops=hops)
    return result

@app.get("/api/centrality")
def get_centrality_and_choke_points():
    return compute_centrality_and_choke_points()

@app.get("/api/attack-paths")
def get_attack_paths(
    source: str = Query("DMZ-Web-Prod", description="Source compromised node"),
    target: str = Query("CrownJewel-Vault-DB", description="Target high-value crown jewel")
):
    return find_attack_paths(source, target)

@app.post("/api/contain")
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

@app.post("/api/shell/execute")
async def execute_shell_command(payload: ShellCommandRequest):
    result = handle_deception_command(payload.command)
    
    # Send WebSocket alert if honeytoken or security event triggered
    if result["alert_triggered"]:
        await telemetry_manager.broadcast({
            "event_type": "DECEPTION_TRAP_TRIGGERED",
            "command": payload.command,
            "mitre": result["mitre_technique"],
            "alert_details": result["alert_details"],
            "graph_update": result["graph_update"],
            "summary": f"ALERT: Attacker executed '{payload.command}'. MITRE: {result['mitre_technique']['technique_id']} ({result['mitre_technique']['technique_name']})"
        })
    elif result["mitre_technique"]["technique_id"] != "T1059.004":
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

