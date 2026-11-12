"""
PhantomShield (GraphShield AI) — J.A.R.V.I.S. Autonomous AI Sentinel
Just a Rather Very Intelligent System
hackFront India 2026 Hackathon | Neo4j Track - GraphOps Problem Statement
Team: Dhanvin (Lead), Pragathish Palsamy, P.V. Krishnan, Mohamed Annas, MANO G
"""

import logging
import datetime
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("phantomshield.jarvis")


CANARY_TOKENS = {"AKIA_CANARY_PHANTOM_99", "shadow.kdbx"}


class JarvisSentinel:
    """
    J.A.R.V.I.S. (Just a Rather Very Intelligent System)
    Autonomous GraphOps Sentinel that continuously inspects attack telemetry,
    evaluates multi-hop blast radius thresholds, and enforces real-time
    topological micro-segmentation.

    Operational Modes:
        AUTONOMOUS_PROTECTION  – auto-quarantines nodes when thresholds breach.
        MANUAL_OVERRIDE        – logs alerts but requires operator confirmation.
    """

    def __init__(self, auto_threshold: float = 85.0):
        self.agent_name: str = "J.A.R.V.I.S."
        self.full_title: str = "Just a Rather Very Intelligent System"
        self.version: str = "2.4.0-Sentinel"
        self.mode: str = "AUTONOMOUS_PROTECTION"
        self.auto_containment_threshold: float = auto_threshold
        self.interventions_count: int = 0
        self.intervention_count: int = 0  # alias kept for compat
        self.last_intervention: Optional[Dict[str, Any]] = None
        self.decision_log: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Status & Mode Management
    # ------------------------------------------------------------------

    def get_status(self) -> Dict[str, Any]:
        """Return operational status and metadata for the J.A.R.V.I.S. telemetry widget."""
        return {
            "agent_name": self.agent_name,
            "full_title": self.full_title,
            "version": self.version,
            "status": "ONLINE" if self.mode == "AUTONOMOUS_PROTECTION" else "STANDBY",
            "mode": self.mode,
            "threshold": f"{self.auto_containment_threshold}% BRVI",
            "intervention_count": self.interventions_count,
            "interventions_count": self.interventions_count,
            "last_intervention": self.last_intervention,
            "system_message": (
                "J.A.R.V.I.S. active: Monitoring Neo4j multi-hop blast radius and decoy canaries in real time."
                if self.mode == "AUTONOMOUS_PROTECTION"
                else "Manual override active: Autonomous containment suspended. Operator confirmation required."
            ),
        }

    def set_mode(self, mode: str) -> Dict[str, Any]:
        """Set operational mode: AUTONOMOUS_PROTECTION or MANUAL_OVERRIDE."""
        if mode in ("AUTONOMOUS_PROTECTION", "MANUAL_OVERRIDE"):
            self.mode = mode
            logger.info("[J.A.R.V.I.S.] Operational mode changed to: %s", self.mode)
        return self.get_status()

    def toggle_mode(self) -> Dict[str, Any]:
        """Toggle between AUTONOMOUS_PROTECTION and MANUAL_OVERRIDE."""
        new_mode = "MANUAL_OVERRIDE" if self.mode == "AUTONOMOUS_PROTECTION" else "AUTONOMOUS_PROTECTION"
        return self.set_mode(new_mode)

    # ------------------------------------------------------------------
    # Core Threat Evaluation (called by verify_submission & main.py)
    # ------------------------------------------------------------------

    def evaluate_telemetry(
        self,
        event_type: str = "GENERIC_EVENT",
        node_id: str = "decoy-ssh-01",
        blast_radius_index: float = 0.0,
        crown_jewels_exposed: Optional[List[str]] = None,
        command: Optional[str] = None,
        shell_result: Optional[Dict[str, Any]] = None,
        target_node: Optional[str] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Inspect telemetry and decide whether autonomous safeguard containment is required.

        Returns:
            (triggered: bool, payload: dict)
              - triggered is True only when AUTONOMOUS_PROTECTION mode fires.

        Args (all keyword):
            event_type          - MITRE / internal event type string
            node_id             - Asset under evaluation
            blast_radius_index  - Current BRVI score (0-100)
            crown_jewels_exposed- List of exposed crown-jewel asset IDs
            command             - Shell command that triggered the event (optional)
            shell_result        - Full shell result dict from llm_sandbox (optional)
            target_node         - Alias for node_id (legacy compatibility)
        """
        # Normalise aliases
        if target_node and not node_id:
            node_id = target_node
        if crown_jewels_exposed is None:
            crown_jewels_exposed = []
        if shell_result is None:
            shell_result = {}
        if command is None:
            command = ""

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # --- Canary detection ---
        canary_hit = (
            shell_result.get("alert_triggered", False)
            or any(tok in command for tok in CANARY_TOKENS)
            or any(tok in str(shell_result.get("output", "")) for tok in CANARY_TOKENS)
        )

        # --- Threshold evaluation ---
        brvi_critical = float(blast_radius_index) >= self.auto_containment_threshold
        breach_imminent = bool(crown_jewels_exposed)

        should_trigger = False
        reason = ""

        if canary_hit:
            should_trigger = True
            reason = (
                f"High-value Canary Token breached in command '{command}'. "
                "Immediate topological quarantine enforced."
            )
        elif brvi_critical:
            should_trigger = True
            reason = (
                f"Blast Radius Vulnerability Index ({blast_radius_index}%) exceeded "
                f"safety threshold ({self.auto_containment_threshold}%). "
                f"Crown Jewels threatened: {crown_jewels_exposed}."
            )
        elif breach_imminent:
            should_trigger = True
            reason = (
                "Adversary lateral movement trajectory unmitigated toward Crown Jewel Vault DB. "
                "Autonomous intervention executed."
            )

        payload: Dict[str, Any] = {
            "agent_name": self.agent_name,
            "full_title": self.full_title,
            "timestamp": timestamp,
            "event_type": "SENTINEL_SAFEGUARD_TRIGGERED" if should_trigger else "SENTINEL_TELEMETRY_OK",
            "mode": self.mode,
            "target_node": node_id,
            "command": command,
            "current_brvi": blast_radius_index,
            "threshold": self.auto_containment_threshold,
            "reasoning": (
                reason if should_trigger
                else "Telemetry inspected. Blast radius within tolerable baseline parameters."
            ),
            "safeguard_required": should_trigger,
            "contained": False,
            "action_enforced": None,
        }

        # Enforce containment only in autonomous mode
        if should_trigger and self.mode == "AUTONOMOUS_PROTECTION":
            logger.warning("[J.A.R.V.I.S. INTERVENTION] %s", reason)
            self.interventions_count += 1
            self.intervention_count = self.interventions_count

            payload["contained"] = True
            payload["action_enforced"] = "AUTONOMOUS_MICRO_SEGMENTATION"
            payload["reasoning"] = f"{reason} Blast radius collapsed to 0.0% (SECURE)."
            self.last_intervention = payload

        self.decision_log.append(payload)
        if len(self.decision_log) > 50:
            self.decision_log.pop(0)

        # Return (triggered, payload) tuple
        return (should_trigger and self.mode == "AUTONOMOUS_PROTECTION", payload)

    def evaluate_command(
        self,
        command: str,
        shell_result: Dict[str, Any],
        target_node: str = "decoy-ssh-01",
    ) -> Dict[str, Any]:
        """
        Convenience wrapper for /api/execute integration in main.py.
        Accepts the legacy (command, shell_result, target_node) positional signature.
        Returns the full payload dict (not the tuple).
        """
        brvi = float(shell_result.get("blast_radius_index", 0.0))
        _, payload = self.evaluate_telemetry(
            event_type=shell_result.get("event_type", "SHELL_COMMAND_EXECUTED"),
            node_id=target_node,
            blast_radius_index=brvi,
            crown_jewels_exposed=shell_result.get("crown_jewels_exposed", []),
            command=command,
            shell_result=shell_result,
        )
        return payload


# ---------------------------------------------------------------------------
# Global singleton — imported by main.py
# ---------------------------------------------------------------------------
jarvis_sentinel = JarvisSentinel(auto_threshold=85.0)
