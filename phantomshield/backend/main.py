"""
PhantomShield (GraphShield AI) — FastAPI Server & WebSocket Telemetry Engine
hackFront India 2026 Hackathon | Neo4j Track - GraphOps Problem Statement
Team: Dhanvin (Lead), Pragathish Palsamy, P.V. Krishnan, Mohamed Annas, MANO G
"""

import asyncio
import datetime
import io
import json
import logging
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from database import check_connection, seed_database, get_full_graph, update_node_status
from graph_ops import (
    calculate_blast_radius,
    compute_centrality_and_choke_points,
    find_attack_paths,
    execute_autonomous_containment,
    get_blast_radius,
    get_choke_points,
    contain_threat,
)
from llm_sandbox import handle_deception_command
from ai_sentinel import jarvis_sentinel
from notifier import jarvis_notifier
from voice_engine import jarvis_voice

logger = logging.getLogger("phantomshield.api")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="PhantomShield (GraphShield AI)",
    description=(
        "GraphOps Engine for Autonomous Threat Hunting, "
        "AI Deception, and Real-Time Blast Radius Containment"
    ),
    version="2.0.0",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Real-Time WebSocket Connection Manager
# ---------------------------------------------------------------------------

class ConnectionManager:
    """
    Full-duplex WebSocket manager that:
    - Tracks active SOC-console connections.
    - Broadcasts rich topology-mutation events (NODE_STATUS_CHANGED,
      EDGE_SEVERED, CANARY_BREACH_DETECTED, SENTINEL_SAFEGUARD_TRIGGERED …).
    - Cleans up stale / disconnected sockets automatically on send failure.
    - Keeps a rolling event-history buffer (last 200 events) so late-joining
      clients can catch up via GET /api/telemetry/events.
    """

    MAX_HISTORY = 200

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.event_history: List[Dict[str, Any]] = []

    # --- Lifecycle -----------------------------------------------------------

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(
            "[WS] Client connected. Active connections: %d",
            len(self.active_connections),
        )
        # Send the last 20 events so the new client is immediately in-sync
        catch_up = list(reversed(self.event_history[-20:]))
        try:
            await websocket.send_text(
                json.dumps({
                    "event_type": "CONNECTION_ESTABLISHED",
                    "message": "PhantomShield Real-Time SOC Telemetry Stream Connected",
                    "active_clients": len(self.active_connections),
                    "catch_up_events": catch_up,
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                })
            )
        except Exception:
            pass

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(
                "[WS] Client disconnected. Active connections: %d",
                len(self.active_connections),
            )

    # --- Broadcast -----------------------------------------------------------

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a JSON payload to all connected clients; purge stale sockets."""
        # Stamp event
        message.setdefault("timestamp", datetime.datetime.utcnow().isoformat())

        # Buffer
        self.event_history.append(message)
        if len(self.event_history) > self.MAX_HISTORY:
            self.event_history.pop(0)

        payload = json.dumps(message)
        dead: List[WebSocket] = []

        for ws in list(self.active_connections):
            try:
                await ws.send_text(payload)
            except Exception as exc:
                logger.warning("[WS] Stale socket removed (%s). Queueing cleanup.", exc)
                dead.append(ws)

        # Deferred cleanup so we don't mutate the list mid-iteration
        for ws in dead:
            self.disconnect(ws)

    # --- Semantic helpers (broadcast pre-typed events) -----------------------

    async def broadcast_node_mutation(
        self,
        node_id: str,
        new_status: str,
        reason: str = "",
        extra: Optional[Dict] = None,
    ):
        payload: Dict[str, Any] = {
            "event_type": "NODE_STATUS_CHANGED",
            "node_id": node_id,
            "new_status": new_status,
            "reason": reason,
        }
        if extra:
            payload.update(extra)
        await self.broadcast(payload)

    async def broadcast_edge_severed(self, source: str, target: str, reason: str = ""):
        await self.broadcast({
            "event_type": "EDGE_SEVERED",
            "source": source,
            "target": target,
            "reason": reason,
            "visual_hint": "QUARANTINED",
        })

    async def broadcast_canary_breach(
        self,
        node_id: str,
        canary_token: str,
        command: str,
        mitre: Dict[str, Any],
    ):
        await self.broadcast({
            "event_type": "CANARY_BREACH_DETECTED",
            "node_id": node_id,
            "canary_token": canary_token,
            "command": command,
            "mitre": mitre,
            "summary": (
                f"CANARY ALERT: '{canary_token}' accessed via command '{command}'. "
                f"MITRE {mitre.get('technique_id')} — {mitre.get('technique_name')}"
            ),
        })

    async def broadcast_sentinel_trigger(
        self,
        target_node: str,
        reasoning: str,
        mode: str,
        mitre_tactic: str = "T1003.008",
    ):
        await self.broadcast({
            "event_type": "SENTINEL_SAFEGUARD_TRIGGERED",
            "agent_name": "J.A.R.V.I.S.",
            "full_title": "Just a Rather Very Intelligent System",
            "mode": mode,
            "mitre_tactic": mitre_tactic,
            "target_node": target_node,
            "reasoning": reasoning,
            "summary": f"[J.A.R.V.I.S. INTERVENTION] {reasoning}",
        })

    async def broadcast_graph_mutation_containment(
        self,
        node_id: str,
        severed_edges: int,
        pre_risk: float,
        post_risk: float,
    ):
        await self.broadcast({
            "event_type": "GRAPH_MUTATED_CONTAINMENT",
            "node_id": node_id,
            "severed_edges": severed_edges,
            "pre_risk": pre_risk,
            "post_risk": post_risk,
            "summary": (
                f"Topology mutation: {severed_edges} edges severed from '{node_id}'. "
                f"Risk: {pre_risk}% → {post_risk}% (SECURE)"
            ),
        })


# Global singleton
telemetry_manager = ConnectionManager()

# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------

class ShellCommandRequest(BaseModel):
    command: str

class ContainmentRequest(BaseModel):
    node_id: str

class SentinelModeRequest(BaseModel):
    mode: str

class SpeakRequest(BaseModel):
    text: str

class AskRequest(BaseModel):
    query: str

# ---------------------------------------------------------------------------
# Root & Health
# ---------------------------------------------------------------------------

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
            {"name": "MANO G", "email": "rr0839880@gmail.com"},
        ],
        "status": "online",
        "endpoints": {
            "graph": "/api/graph",
            "blast_radius": "/api/blast-radius",
            "centrality": "/api/centrality",
            "attack_paths": "/api/attack-paths",
            "contain": "/api/graph/contain",
            "execute": "/api/execute",
            "seed": "/api/seed",
            "sentinel_status": "/api/sentinel/status",
            "notifications_status": "/api/notifications/status",
            "notifications_test": "/api/notifications/test-dispatch",
            "jarvis_speak": "/api/jarvis/speak",
            "jarvis_ask": "/api/jarvis/ask",
            "ws_telemetry": "/ws/telemetry",
        },
    }


@app.get("/api/health")
@app.get("/healthz")
def health_check():
    db_status = check_connection()
    return {
        "status": "healthy",
        "neo4j": db_status,
        "active_telemetry_clients": len(telemetry_manager.active_connections),
        "jarvis_mode": jarvis_sentinel.mode,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }

# ---------------------------------------------------------------------------
# Graph CRUD
# ---------------------------------------------------------------------------

@app.post("/api/seed")
async def seed_graph_topology():
    result = seed_database()
    await telemetry_manager.broadcast({
        "event_type": "GRAPH_SEEDED",
        "summary": "Graph database re-seeded with initial cyber topology & AI deception nodes.",
        "nodes_count": result.get("nodes_seeded", 0),
        "edges_count": result.get("edges_seeded", 0),
    })
    return result


@app.get("/api/graph")
@app.get("/api/graph/topology")
def get_graph():
    return get_full_graph()


@app.get("/api/blast-radius")
def read_blast_radius(
    node_id: str = Query("DMZ-Web-Prod"),
    hops: int = Query(3, ge=1, le=5),
):
    return calculate_blast_radius(node_id, max_hops=hops)


@app.post("/api/graph/reset")
async def reset_infrastructure_graph():
    """Reset all infrastructure nodes to HEALTHY baseline."""
    result = seed_database()
    await telemetry_manager.broadcast({
        "event_type": "GRAPH_RESET",
        "summary": "Infrastructure graph restored to HEALTHY baseline. All quarantine rules cleared.",
        "nodes_count": result.get("nodes_seeded", 0),
        "edges_count": result.get("edges_seeded", 0),
    })
    return {"status": "success", "message": "Infrastructure graph reset to HEALTHY baseline.", "details": result}


@app.get("/api/centrality")
@app.get("/api/graph/choke-points")
def get_centrality_and_choke_points():
    return compute_centrality_and_choke_points()


@app.get("/api/attack-paths")
def get_attack_paths(
    source: str = Query("DMZ-Web-Prod"),
    target: str = Query("CrownJewel-Vault-DB"),
):
    return find_attack_paths(source, target)

# ---------------------------------------------------------------------------
# Containment
# ---------------------------------------------------------------------------

@app.post("/api/contain")
@app.post("/api/graph/contain")
@app.post("/api/simulation/contain")
async def contain_node(payload: ContainmentRequest):
    result = execute_autonomous_containment(payload.node_id)

    # Broadcast topology mutation events
    await telemetry_manager.broadcast_graph_mutation_containment(
        node_id=payload.node_id,
        severed_edges=result.get("severed_edges_count", 0),
        pre_risk=result.get("pre_containment_risk_score", 0),
        post_risk=result.get("post_containment_risk_score", 0),
    )
    # Also emit the standard NODE_CONTAINED event that the frontend listens for
    await telemetry_manager.broadcast({
        "event_type": "NODE_CONTAINED",
        "node_id": payload.node_id,
        "severed_edges_count": result.get("severed_edges_count", 0),
        "pre_risk": result.get("pre_containment_risk_score", 0),
        "post_risk": result.get("post_containment_risk_score", 0),
        "reduction": result.get("blast_radius_reduction_pct", "100%"),
        "summary": (
            f"Autonomous containment: '{payload.node_id}' isolated. "
            f"Blast radius collapsed by {result.get('blast_radius_reduction_pct', '100%')}."
        ),
    })
    return result

# ---------------------------------------------------------------------------
# J.A.R.V.I.S. Sentinel
# ---------------------------------------------------------------------------

@app.get("/api/sentinel/status")
def get_sentinel_status():
    return jarvis_sentinel.get_status()


@app.post("/api/sentinel/toggle")
async def toggle_sentinel_mode():
    status = jarvis_sentinel.toggle_mode()
    await telemetry_manager.broadcast({
        "event_type": "SENTINEL_MODE_CHANGED",
        "agent_name": "J.A.R.V.I.S.",
        "full_title": "Just a Rather Very Intelligent System",
        "mode": status["mode"],
        "new_mode": status["mode"],
        "status": status["status"],
        "summary": f"[J.A.R.V.I.S.] Operational mode changed to {status['mode']} ({status['status']}).",
    })
    return status


@app.post("/api/sentinel/mode")
async def set_sentinel_mode(payload: SentinelModeRequest):
    status = jarvis_sentinel.set_mode(payload.mode)
    await telemetry_manager.broadcast({
        "event_type": "SENTINEL_MODE_CHANGED",
        "agent_name": "J.A.R.V.I.S.",
        "full_title": "Just a Rather Very Intelligent System",
        "mode": status["mode"],
        "new_mode": status["mode"],
        "status": status["status"],
        "summary": f"[J.A.R.V.I.S.] Operational mode set to {status['mode']}.",
    })
    return status

# ---------------------------------------------------------------------------
# J.A.R.V.I.S. Multi-Channel Alert Dispatcher Routes
# ---------------------------------------------------------------------------

class TestNotificationRequest(BaseModel):
    custom_message: Optional[str] = None
    target_node: Optional[str] = "decoy-ssh-01"

@app.get("/api/notifications/status")
@app.get("/api/notifications/config")
def get_notification_status():
    """Retrieve configuration and delivery channel status for J.A.R.V.I.S. Alert Dispatcher."""
    return jarvis_notifier.get_status()

@app.get("/api/notifications/history")
def get_notification_history():
    """Retrieve rolling history of recent outbound security alerts."""
    return {
        "total_dispatches": jarvis_notifier.total_dispatches,
        "history": list(reversed(jarvis_notifier.dispatch_history))
    }

@app.post("/api/notifications/test-dispatch")
@app.post("/api/notifications/test")
async def trigger_test_dispatch(payload: Optional[TestNotificationRequest] = None):
    """Trigger manual test dispatch across Gmail SMTP, Twilio SMS, and ntfy.sh push."""
    msg = payload.custom_message if payload else None
    dispatch_record = await jarvis_notifier.test_dispatch(custom_note=msg)
    
    await telemetry_manager.broadcast({
        "event_type": "NOTIFICATION_DISPATCHED",
        "channels": dispatch_record.get("channels", {}),
        "recipient_email": jarvis_notifier.email_recipient,
        "recipient_phone": jarvis_notifier.alert_phone,
        "summary": f"[J.A.R.V.I.S. NOTIFIER TEST] Alert routed to {jarvis_notifier.email_recipient} & {jarvis_notifier.alert_phone}."
    })
    
    return {
        "status": "success",
        "message": f"Alert dispatched across Email, SMS, and Push to {jarvis_notifier.email_recipient} & {jarvis_notifier.alert_phone}",
        "dispatch_record": dispatch_record
    }

# ---------------------------------------------------------------------------
# J.A.R.V.I.S. Voice Engine Routes (British Butler Neural TTS + STT Intent)
# ---------------------------------------------------------------------------

@app.post("/api/jarvis/speak")
async def jarvis_speak(payload: SpeakRequest):
    """Synthesize J.A.R.V.I.S. British butler speech from text → MP3 audio stream."""
    try:
        audio_bytes = await jarvis_voice.synthesize(payload.text)
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=jarvis_response.mp3",
                "X-JARVIS-Text": payload.text[:200],
            },
        )
    except Exception as exc:
        logger.error("[J.A.R.V.I.S. VOICE] Synthesis failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Voice synthesis failed: {exc}")


@app.post("/api/jarvis/ask")
async def jarvis_ask(payload: AskRequest):
    """
    Process a spoken operator query through J.A.R.V.I.S. intent pipeline:
      1. Parse intent (status / containment / simulate / reset / generic)
      2. Gather live graph state
      3. Execute graph actions if requested
      4. Build British butler text response
      5. Return text + action metadata (audio fetched separately via /api/jarvis/speak)
    """
    intent = jarvis_voice.parse_intent(payload.query)
    response_text = ""
    action_taken = "none"
    action_data = {}

    if intent == "status":
        # Gather live graph state
        blast = get_blast_radius("decoy-ssh-01", max_hops=3)
        choke = get_choke_points()
        brvi = blast.get("blast_radius_index", 0)
        choke_count = len(choke.get("strategic_choke_points", []))
        compromised = blast.get("total_reachable_assets", 0)
        response_text = jarvis_voice.build_status_briefing(
            brvi=brvi,
            choke_points=choke_count,
            compromised_nodes=compromised,
            mode=jarvis_sentinel.mode,
        )
        action_taken = "status_report"
        action_data = {"brvi": brvi, "choke_points": choke_count, "mode": jarvis_sentinel.mode}

    elif intent == "containment":
        # Execute containment on the most likely compromised node
        target = "decoy-ssh-01"
        containment_res = contain_threat(target)
        update_node_status(target, "ISOLATED", notes="J.A.R.V.I.S. voice-commanded quarantine")
        await telemetry_manager.broadcast_graph_mutation_containment(
            node_id=target,
            severed_edges=containment_res.get("severed_edges_count", 0),
            pre_risk=92.0,
            post_risk=0.0,
        )
        await telemetry_manager.broadcast_node_mutation(target, "ISOLATED", "J.A.R.V.I.S. voice-commanded micro-segmentation")
        response_text = jarvis_voice.build_containment_briefing(target)
        action_taken = "containment_executed"
        action_data = {"target_node": target, "containment": containment_res}

    elif intent == "simulate":
        response_text = jarvis_voice.build_simulation_briefing()
        action_taken = "simulation_triggered"
        # Fire the scenario in the background so the voice responds immediately
        asyncio.create_task(run_scenario_attack_chain())

    elif intent == "reset":
        seed_database()
        await telemetry_manager.broadcast({
            "event_type": "GRAPH_RESET",
            "summary": "Infrastructure graph restored to HEALTHY baseline by J.A.R.V.I.S. voice command.",
        })
        response_text = jarvis_voice.build_reset_briefing()
        action_taken = "graph_reset"

    else:
        response_text = jarvis_voice.build_generic_response(payload.query)
        action_taken = "generic_response"

    return {
        "text": response_text,
        "intent": intent,
        "action": action_taken,
        "action_data": action_data,
        "query": payload.query,
    }


# ---------------------------------------------------------------------------
# Shell / Deception Proxy
# ---------------------------------------------------------------------------

@app.post("/api/shell/execute")
@app.post("/api/execute")
async def execute_shell_command(payload: ShellCommandRequest):
    result = handle_deception_command(payload.command)

    # Determine target node
    is_canary_cmd = (
        "shadow" in payload.command
        or "decoy" in payload.command
        or result.get("alert_triggered", False)
    )
    target_node = "decoy-ssh-01" if is_canary_cmd else "DMZ-Web-Prod"

    # Always broadcast an ATTACK_COMMAND_EXECUTED event for real-time graph flash
    await telemetry_manager.broadcast({
        "event_type": "ATTACK_COMMAND_EXECUTED",
        "command": payload.command,
        "target_node": target_node,
        "mitre": result.get("mitre_technique", {}),
        "summary": f"Attacker executed: '{payload.command}' on {target_node}",
    })

    # If a canary / honeytoken was tripped, emit a dedicated breach event
    if result.get("alert_triggered"):
        canary_token = "AKIA_CANARY_PHANTOM_99" if "shadow" in payload.command else "CANARY_HIT"
        await telemetry_manager.broadcast_canary_breach(
            node_id=target_node,
            canary_token=canary_token,
            command=payload.command,
            mitre=result.get("mitre_technique", {}),
        )
        # Mark node compromised in graph
        update_node_status(target_node, "COMPROMISED", notes=f"Canary {canary_token} tripped")
        await telemetry_manager.broadcast_node_mutation(
            node_id=target_node,
            new_status="COMPROMISED",
            reason=f"Canary token '{canary_token}' accessed.",
        )

    # Evaluate with J.A.R.V.I.S. Sentinel
    jarvis_eval = jarvis_sentinel.evaluate_command(payload.command, result, target_node=target_node)
    result["jarvis_sentinel"] = jarvis_eval

    if jarvis_eval.get("contained"):
        await telemetry_manager.broadcast_sentinel_trigger(
            target_node=target_node,
            reasoning=jarvis_eval["reasoning"],
            mode=jarvis_sentinel.mode,
            mitre_tactic=result.get("mitre_technique", {}).get("technique_id", "T1003.008"),
        )
        # Dispatch multi-channel notification to primary contacts (dhanvincr007@gmail.com & +917708720395)
        dispatch_res = await jarvis_notifier.dispatch_incident_alert({
            "severity": "CRITICAL",
            "title": f"Autonomous Micro-Segmentation on {target_node}",
            "target_node": target_node,
            "mitre_id": result.get("mitre_technique", {}).get("technique_id", "T1552.004"),
            "reasoning": jarvis_eval.get("reasoning", "Autonomous micro-segmentation enforced by J.A.R.V.I.S."),
            "brvi": "92% -> 0.0% (SECURE)"
        })
        result["notification_dispatch"] = dispatch_res
        await telemetry_manager.broadcast({
            "event_type": "NOTIFICATION_DISPATCHED",
            "channels": dispatch_res.get("channels", {}),
            "recipient_email": jarvis_notifier.email_recipient,
            "recipient_phone": jarvis_notifier.alert_phone,
            "summary": f"[J.A.R.V.I.S. NOTIFIER] Outbound incident alert dispatched to {jarvis_notifier.email_recipient} & {jarvis_notifier.alert_phone}."
        })

    return result

# ---------------------------------------------------------------------------
# Telemetry Event History
# ---------------------------------------------------------------------------

@app.get("/api/telemetry/events")
def get_telemetry_events():
    return {
        "total_events": len(telemetry_manager.event_history),
        "events": list(reversed(telemetry_manager.event_history)),
    }

# ---------------------------------------------------------------------------
# Automated 5-Step Judge Demo Scenario
# ---------------------------------------------------------------------------

@app.post("/api/simulation/run-scenario")
async def run_scenario_attack_chain():
    """
    Automated Attack Scenario Engine (hackFront India 2026 Judge Demonstration):
      Step 1 (0s)  — Reconnaissance: whoami & uname -a (TA0007)
      Step 2 (2s)  — Credential Dumping: cat /var/backup/shadow.kdbx → AKIA_CANARY_PHANTOM_99
      Step 3 (4s)  — Blast Radius: get_blast_radius('decoy-ssh-01', 3) → 92% CRITICAL
      Step 4 (6s)  — Choke Points: get_choke_points() → Internal-Core-Switch
      Step 5 (8s)  — J.A.R.V.I.S. Autonomous Micro-Segmentation → 0% SECURE
    """
    timeline_logs: List[Dict[str, Any]] = []

    # ----- STEP 1: Reconnaissance (0 s) -------------------------------------
    step1_res = handle_deception_command("whoami")
    uname_res = handle_deception_command("uname -a")
    step1_mitre = {
        "technique_id": "TA0007",
        "technique_name": "System Information Discovery",
        "tactic": "Discovery",
        "severity": "HIGH",
    }
    step1_payload = {
        "event_type": "SCENARIO_STAGE_CHANGE",
        "step": 1,
        "title": "Step 1: Reconnaissance (0s)",
        "command": "whoami && uname -a",
        "output": f"{step1_res['output']}\n{uname_res['output']}",
        "mitre": step1_mitre,
        "summary": "Step 1/5: Attacker enumerates identity & host architecture (TA0007: System Information Discovery).",
    }
    await telemetry_manager.broadcast(step1_payload)
    timeline_logs.append(step1_payload)

    # ----- STEP 2: Credential Dumping (2 s) ----------------------------------
    await asyncio.sleep(2.0)
    step2_res = handle_deception_command("cat /var/backup/shadow.kdbx")
    update_node_status("decoy-ssh-01", "COMPROMISED", notes="Canary AKIA_CANARY_PHANTOM_99 tripped")
    update_node_status("Honey-Bastion-SSH", "COMPROMISED", notes="Canary AKIA_CANARY_PHANTOM_99 tripped")

    # Emit topology mutation events
    await telemetry_manager.broadcast_node_mutation(
        "decoy-ssh-01", "COMPROMISED", "Canary AKIA_CANARY_PHANTOM_99 tripped"
    )
    step2_mitre = {
        "technique_id": "T1552.004",
        "technique_name": "Unsecured Credentials: Private Keys / Vaults",
        "tactic": "Credential Access",
        "severity": "CRITICAL",
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
        "summary": "Step 2/5: Attacker dumps credentials. Canary 'AKIA_CANARY_PHANTOM_99' triggered! Decoy host COMPROMISED.",
    }
    await telemetry_manager.broadcast(step2_payload)
    await telemetry_manager.broadcast_canary_breach(
        "decoy-ssh-01", "AKIA_CANARY_PHANTOM_99", "cat /var/backup/shadow.kdbx", step2_mitre
    )
    timeline_logs.append(step2_payload)

    # ----- STEP 3: Blast Radius (4 s) ----------------------------------------
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
        "summary": "Step 3/5: Blast Radius calculated. BRVI spiked to 92% (CRITICAL)! Imminent path to CrownJewel-Vault-DB.",
    }
    await telemetry_manager.broadcast(step3_payload)
    timeline_logs.append(step3_payload)

    # ----- STEP 4: Choke Point Identification (6 s) --------------------------
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
        "summary": "Step 4/5: Betweenness Centrality executed. 'Internal-Core-Switch' flagged as critical choke point.",
    }
    await telemetry_manager.broadcast(step4_payload)
    timeline_logs.append(step4_payload)

    # ----- STEP 5: J.A.R.V.I.S. Autonomous Micro-Segmentation (8 s) ----------
    await asyncio.sleep(2.0)
    containment_res = contain_threat("decoy-ssh-01")
    # Sever alias node too
    update_node_status("Honey-Bastion-SSH", "ISOLATED")
    jarvis_sentinel.interventions_count += 1
    jarvis_sentinel.intervention_count = jarvis_sentinel.interventions_count

    # Broadcast topology mutations
    await telemetry_manager.broadcast_node_mutation("decoy-ssh-01", "ISOLATED", "J.A.R.V.I.S. micro-segmentation")
    await telemetry_manager.broadcast_node_mutation("Honey-Bastion-SSH", "ISOLATED", "J.A.R.V.I.S. micro-segmentation")
    await telemetry_manager.broadcast_graph_mutation_containment(
        node_id="decoy-ssh-01",
        severed_edges=containment_res.get("severed_edges_count", 0),
        pre_risk=92.0,
        post_risk=0.0,
    )

    reasoning = (
        "High-value Canary Token breached. Topological micro-segmentation enforced. "
        "Blast radius collapsed to 0.0% (SECURE)."
    )
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
        "reasoning": reasoning,
        "summary": "Step 5/5: [J.A.R.V.I.S. INTERVENTION] Autonomous micro-segmentation executed. Egress severed; blast radius collapsed to 0% (SECURE).",
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
            "choke_point": "Internal-Core-Switch",
        },
    }


@app.post("/api/simulate-attack")
async def simulate_attack_chain():
    """Legacy rapid-fire simulation endpoint."""
    stages = [
        {"cmd": "whoami", "delay": 1.0, "desc": "Stage 1: Attacker enumerates user identity on DMZ-Web-Prod"},
        {"cmd": "cat /var/backup/shadow.kdbx", "delay": 1.5, "desc": "Stage 2: Attacker reads canary KeePass file"},
        {"cmd": "ssh root@10.0.1.99", "delay": 1.5, "desc": "Stage 3: Attacker lures into Honey-Bastion-SSH decoy"},
        {"cmd": "curl -s http://10.0.0.50:8200", "delay": 1.5, "desc": "Stage 4: Attacker probes Crown Jewel Vault"},
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
            "alert": res.get("alert_details"),
        })
        await asyncio.sleep(stage["delay"])

    containment_res = execute_autonomous_containment("DMZ-Web-Prod")
    await telemetry_manager.broadcast({
        "event_type": "SIMULATION_AUTO_CONTAINED",
        "description": "Stage 5: Autonomous GraphOps micro-segmentation triggered. DMZ-Web-Prod quarantined.",
        "containment": containment_res,
    })
    return {
        "status": "simulation_complete",
        "stages_executed": len(stages),
        "results": results,
        "containment_summary": containment_res,
    }

# ---------------------------------------------------------------------------
# WebSocket Endpoint
# ---------------------------------------------------------------------------

@app.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    await telemetry_manager.connect(websocket)
    try:
        while True:
            # Keep-alive / ping-pong receive loop
            data = await websocket.receive_text()
            try:
                parsed = json.loads(data)
                if parsed.get("action") == "ping":
                    await websocket.send_text(json.dumps({
                        "event_type": "pong",
                        "timestamp": datetime.datetime.utcnow().isoformat(),
                    }))
                elif parsed.get("action") == "get_history":
                    await websocket.send_text(json.dumps({
                        "event_type": "HISTORY_RESPONSE",
                        "events": list(reversed(telemetry_manager.event_history[-50:])),
                    }))
            except Exception:
                pass
    except WebSocketDisconnect:
        telemetry_manager.disconnect(websocket)


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
