"""
voice_engine.py — J.A.R.V.I.S. Neural Voice Engine
Two-tier TTS pipeline:
  Tier 1: ElevenLabs custom voice (optional, via ELEVENLABS_API_KEY + ELEVENLABS_VOICE_ID)
  Tier 2: edge-tts en-GB-RyanNeural (zero-config British neural fallback)
"""

import io
import os
import asyncio
import logging
from typing import Literal

import httpx

logger = logging.getLogger("jarvis.voice")

# ---------------------------------------------------------------------------
# Intent type alias
# ---------------------------------------------------------------------------
IntentType = Literal["status", "containment", "simulate", "reset", "generic"]


class JARVISVoiceEngine:
    """J.A.R.V.I.S. voice synthesis & intent parsing engine."""

    # ElevenLabs config (read from environment at import time)
    _elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")
    _elevenlabs_voice_id: str = os.getenv("ELEVENLABS_VOICE_ID", "")
    _elevenlabs_model: str = "eleven_flash_v2_5"

    # edge-tts config
    _edge_voice: str = "en-GB-RyanNeural"
    _edge_rate: str = "-4%"
    _edge_pitch: str = "-3Hz"

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    async def synthesize(self, text: str) -> bytes:
        """Return MP3 audio bytes for *text* using the best available TTS tier."""
        if self._elevenlabs_api_key and self._elevenlabs_voice_id:
            try:
                return await self._elevenlabs_synthesize(text)
            except Exception as exc:
                logger.warning(
                    "ElevenLabs TTS failed (%s); falling back to edge-tts.", exc
                )
        return await self._edge_synthesize(text)

    # -----------------------------------------------------------------------
    # British-butler briefing builders
    # -----------------------------------------------------------------------

    def build_status_briefing(
        self,
        brvi: float,
        choke_points: int,
        compromised_nodes: int,
        mode: str,
    ) -> str:
        severity = "critical" if brvi >= 70 else "elevated" if brvi >= 40 else "nominal"
        mode_str = (
            "Autonomous Protection"
            if mode == "AUTONOMOUS_PROTECTION"
            else "Manual Override"
        )
        return (
            f"Status report, sir. "
            f"The current Blast Radius Vulnerability Index stands at {brvi:.0f} percent — "
            f"severity is {severity}. "
            f"I have identified {choke_points} critical choke point{'s' if choke_points != 1 else ''} "
            f"and {compromised_nodes} compromised node{'s' if compromised_nodes != 1 else ''} "
            f"across the topology. "
            f"J.A.R.V.I.S. is operating in {mode_str} mode. "
            f"All perimeter sensors remain active, sir. Shall I proceed with containment?"
        )

    def build_containment_briefing(self, target_node: str) -> str:
        node_name = target_node.replace("-", " ").replace("_", " ").title()
        return (
            f"At once, sir. Initiating micro-segmentation protocol on {node_name}. "
            f"I am severing all outgoing egress paths and isolating lateral movement vectors. "
            f"Blast radius collapse in progress. "
            f"The network perimeter will be restored momentarily, sir."
        )

    def build_simulation_briefing(self) -> str:
        return (
            "Initiating live adversary simulation on the DMZ Web Production node, sir. "
            "I will execute a full MITRE ATT&CK kill-chain sequence across the topology — "
            "reconnaissance, lateral movement, privilege escalation, and exfiltration. "
            "Stand by for telemetry. This is a controlled exercise, sir."
        )

    def build_reset_briefing(self) -> str:
        return (
            "Infrastructure topology restored to baseline parameters, sir. "
            "All node statuses have been cleared, edge weights recalibrated, "
            "and canary tokens re-armed. "
            "The graph is clean. I am resuming continuous threat surveillance, sir."
        )

    def build_quarantine_alert_briefing(self, node_id: str) -> str:
        node_name = node_id.replace("-", " ").replace("_", " ").title()
        return (
            f"Alert, sir. A high-value canary token has been breached on {node_name}. "
            f"I have autonomously severed all outgoing egress connections and "
            f"collapsed the blast radius to zero. "
            f"The network is now secure. Incident report dispatched to Team Lead. "
            f"Awaiting your instructions, sir."
        )

    def build_generic_response(self, query: str) -> str:
        q = query.lower().strip()
        if any(w in q for w in ["hello", "hey", "hi", "good"]):
            return (
                "Good day, sir. J.A.R.V.I.S. online and fully operational. "
                "All PhantomShield subsystems are nominal. How may I assist you?"
            )
        if any(w in q for w in ["thank", "thanks", "cheers"]):
            return (
                "My pleasure, sir. That is precisely what I am here for. "
                "Is there anything else you require?"
            )
        if any(w in q for w in ["who are you", "what are you", "introduce"]):
            return (
                "I am J.A.R.V.I.S. — Just a Rather Very Intelligent System, sir. "
                "I serve as PhantomShield's autonomous AI GraphOps sentinel: "
                "continuously hunting threats, evaluating blast radius thresholds, "
                "and enforcing real-time topological micro-segmentation. "
                "At your service, sir."
            )
        return (
            f"Understood, sir. Processing your request: '{query}'. "
            f"I have relayed the command to the PhantomShield operations core. "
            f"Please stand by for confirmation."
        )

    # -----------------------------------------------------------------------
    # Intent parser
    # -----------------------------------------------------------------------

    def parse_intent(self, query: str) -> IntentType:
        """
        Map natural-language queries to structured intent labels.
        Returns one of: 'status' | 'containment' | 'simulate' | 'reset' | 'generic'
        """
        q = query.lower()

        status_keywords = [
            "status", "report", "overview", "how are", "situation",
            "blast radius", "brvi", "health", "monitor", "check",
        ]
        containment_keywords = [
            "contain", "quarantine", "isolate", "sever", "cut", "block",
            "lockdown", "micro-segment", "microsegment", "stop the threat",
            "neutralise", "neutralize",
        ]
        simulate_keywords = [
            "simulat", "attack", "run", "execute", "judge", "pentest",
            "red team", "adversary", "exploit",
        ]
        reset_keywords = [
            "reset", "restore", "clear", "baseline", "clean", "revert",
            "reinitialise", "reinitialize",
        ]

        if any(kw in q for kw in status_keywords):
            return "status"
        if any(kw in q for kw in containment_keywords):
            return "containment"
        if any(kw in q for kw in simulate_keywords):
            return "simulate"
        if any(kw in q for kw in reset_keywords):
            return "reset"
        return "generic"

    # -----------------------------------------------------------------------
    # Private TTS helpers
    # -----------------------------------------------------------------------

    async def _elevenlabs_synthesize(self, text: str) -> bytes:
        """Call ElevenLabs streaming TTS endpoint and return MP3 bytes."""
        url = (
            f"https://api.elevenlabs.io/v1/text-to-speech"
            f"/{self._elevenlabs_voice_id}/stream"
        )
        payload = {
            "text": text,
            "model_id": self._elevenlabs_model,
            "voice_settings": {
                "stability": 0.65,
                "similarity_boost": 0.80,
            },
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers={
                    "xi-api-key": self._elevenlabs_api_key,
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            return response.content

    async def _edge_synthesize(self, text: str) -> bytes:
        """Use edge-tts (en-GB-RyanNeural) to synthesize *text* → MP3 bytes."""
        import edge_tts  # lazy import — only required when falling back

        communicate = edge_tts.Communicate(
            text,
            voice=self._edge_voice,
            rate=self._edge_rate,
            pitch=self._edge_pitch,
        )
        buf = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                buf.write(chunk["data"])
        audio_bytes = buf.getvalue()
        if not audio_bytes:
            raise RuntimeError("edge-tts returned empty audio buffer.")
        return audio_bytes


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
jarvis_voice = JARVISVoiceEngine()

