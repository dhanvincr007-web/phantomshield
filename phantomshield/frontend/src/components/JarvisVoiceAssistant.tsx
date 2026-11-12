"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
type JarvisStatus = "IDLE" | "LISTENING" | "PROCESSING" | "SPEAKING";

interface JarvisVoiceAssistantProps {
  wsUrl: string;
  apiBase: string;
}

// ---------------------------------------------------------------------------
// Quick Command Chips
// ---------------------------------------------------------------------------
const QUICK_COMMANDS = [
  { label: "📊 Status Report", query: "JARVIS, give me a full status report" },
  { label: "🛡️ Quarantine Threat", query: "JARVIS, quarantine the compromised node immediately" },
  { label: "⚡ Run Simulation", query: "JARVIS, run a live attack simulation" },
  { label: "🔄 Reset Network", query: "JARVIS, reset the infrastructure graph to baseline" },
];

// ---------------------------------------------------------------------------
// Arc Reactor SVG Component
// ---------------------------------------------------------------------------
function ArcReactor({ status }: { status: JarvisStatus }) {
  const pulseClass =
    status === "SPEAKING"
      ? "animate-spin"
      : status === "LISTENING"
      ? "animate-pulse"
      : status === "PROCESSING"
      ? "animate-ping"
      : "";

  const glowColor =
    status === "LISTENING"
      ? "#f59e0b"
      : status === "SPEAKING"
      ? "#06b6d4"
      : status === "PROCESSING"
      ? "#a855f7"
      : "#0e7490";

  return (
    <svg viewBox="0 0 100 100" className="w-10 h-10" aria-label="J.A.R.V.I.S. Arc Reactor">
      {/* Outer glow ring */}
      <circle
        cx="50"
        cy="50"
        r="46"
        fill="none"
        stroke={glowColor}
        strokeWidth="1.5"
        opacity={0.3}
        className={pulseClass}
      />
      {/* Middle ring */}
      <circle
        cx="50"
        cy="50"
        r="38"
        fill="none"
        stroke={glowColor}
        strokeWidth="2"
        opacity={0.5}
        strokeDasharray={status === "IDLE" ? "none" : "8 4"}
        className={status !== "IDLE" ? "animate-spin" : ""}
        style={{ animationDuration: "3s" }}
      />
      {/* Inner ring */}
      <circle
        cx="50"
        cy="50"
        r="28"
        fill="none"
        stroke={glowColor}
        strokeWidth="2.5"
        opacity={0.7}
        strokeDasharray={status !== "IDLE" ? "12 6" : "none"}
        className={status !== "IDLE" ? "animate-spin" : ""}
        style={{ animationDuration: "2s", animationDirection: "reverse" }}
      />
      {/* Core glow */}
      <circle cx="50" cy="50" r="16" fill={glowColor} opacity={0.15} />
      <circle
        cx="50"
        cy="50"
        r="10"
        fill={glowColor}
        opacity={status === "IDLE" ? 0.4 : 0.75}
        className={status !== "IDLE" ? "animate-pulse" : ""}
      />
      {/* Center dot */}
      <circle cx="50" cy="50" r="4" fill="white" opacity={0.9} />
      {/* Triangular spokes */}
      {[0, 60, 120, 180, 240, 300].map((angle) => (
        <line
          key={angle}
          x1="50"
          y1="50"
          x2={50 + 36 * Math.cos((angle * Math.PI) / 180)}
          y2={50 + 36 * Math.sin((angle * Math.PI) / 180)}
          stroke={glowColor}
          strokeWidth="1"
          opacity={0.25}
        />
      ))}
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------
export default function JarvisVoiceAssistant({
  wsUrl,
  apiBase,
}: JarvisVoiceAssistantProps) {
  const [status, setStatus] = useState<JarvisStatus>("IDLE");
  const [isMuted, setIsMuted] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [lastResponse, setLastResponse] = useState<string>("");
  const [transcript, setTranscript] = useState<string>("");
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const recognitionRef = useRef<any>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // -------------------------------------------------------------------------
  // Audio Playback
  // -------------------------------------------------------------------------
  const playAudio = useCallback(
    async (text: string) => {
      if (isMuted) return;
      setStatus("SPEAKING");
      try {
        const res = await fetch(`${apiBase}/api/jarvis/speak`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        });
        if (!res.ok) {
          setStatus("IDLE");
          return;
        }
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        audioRef.current = audio;

        audio.onended = () => {
          setStatus("IDLE");
          URL.revokeObjectURL(url);
        };
        audio.onerror = () => {
          setStatus("IDLE");
          URL.revokeObjectURL(url);
        };
        await audio.play();
      } catch {
        setStatus("IDLE");
      }
    },
    [apiBase, isMuted]
  );

  // -------------------------------------------------------------------------
  // Ask J.A.R.V.I.S. (text query → intent → response + audio)
  // -------------------------------------------------------------------------
  const askJarvis = useCallback(
    async (query: string) => {
      setStatus("PROCESSING");
      setTranscript(query);
      try {
        const res = await fetch(`${apiBase}/api/jarvis/ask`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query }),
        });
        if (!res.ok) {
          setStatus("IDLE");
          return;
        }
        const data = await res.json();
        setLastResponse(data.text || "");
        await playAudio(data.text || "Understood, sir.");
      } catch {
        setLastResponse("Communications disrupted, sir. Please try again.");
        setStatus("IDLE");
      }
    },
    [apiBase, playAudio]
  );

  // -------------------------------------------------------------------------
  // WebSocket listener for auto-voice-briefings
  // -------------------------------------------------------------------------
  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

    const connect = () => {
      try {
        ws = new WebSocket(`${wsUrl}/ws/telemetry`);
        wsRef.current = ws;

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            // Auto-play voice briefing on sentinel triggers or notifications
            if (
              !isMuted &&
              (data.event_type === "SENTINEL_SAFEGUARD_TRIGGERED" ||
                data.event_type === "NOTIFICATION_DISPATCHED") &&
              data.voice_briefing
            ) {
              playAudio(data.voice_briefing);
            }
          } catch {
            // ignore parse errors
          }
        };

        ws.onclose = () => {
          reconnectTimer = setTimeout(connect, 5000);
        };

        ws.onerror = () => {
          ws?.close();
        };
      } catch {
        reconnectTimer = setTimeout(connect, 5000);
      }
    };

    connect();

    return () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      ws?.close();
    };
  }, [wsUrl, isMuted, playAudio]);

  // -------------------------------------------------------------------------
  // Speech Recognition (STT)
  // -------------------------------------------------------------------------
  const startListening = useCallback(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setLastResponse("Speech recognition is not supported in this browser, sir.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.continuous = false;

    recognition.onstart = () => {
      setStatus("LISTENING");
      setTranscript("");
    };

    recognition.onresult = (event: any) => {
      const spoken = event.results[0][0].transcript;
      setTranscript(spoken);
      askJarvis(spoken);
    };

    recognition.onerror = () => {
      setStatus("IDLE");
      setLastResponse("I didn't catch that, sir. Please try again.");
    };

    recognition.onend = () => {
      if (status === "LISTENING") setStatus("IDLE");
    };

    recognitionRef.current = recognition;
    recognition.start();
  }, [askJarvis, status]);

  const stopListening = useCallback(() => {
    recognitionRef.current?.stop();
    setStatus("IDLE");
  }, []);

  // -------------------------------------------------------------------------
  // Stop Audio
  // -------------------------------------------------------------------------
  const stopAudio = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    setStatus("IDLE");
  }, []);

  // -------------------------------------------------------------------------
  // Status label + color helpers
  // -------------------------------------------------------------------------
  const statusLabel =
    status === "LISTENING"
      ? "Listening..."
      : status === "PROCESSING"
      ? "Processing..."
      : status === "SPEAKING"
      ? "Speaking..."
      : "Standby";

  const statusColor =
    status === "LISTENING"
      ? "text-amber-400"
      : status === "SPEAKING"
      ? "text-cyan-400"
      : status === "PROCESSING"
      ? "text-purple-400"
      : "text-slate-500";

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------
  return (
    <div className="relative">
      {/* Compact Pill (always visible in header) */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className={`flex items-center space-x-2 px-2 py-1 rounded-full text-xs font-mono font-medium border transition cursor-pointer ${
          status !== "IDLE"
            ? "bg-cyan-950/90 border-cyan-400/60 text-cyan-300 shadow-lg shadow-cyan-500/30"
            : "bg-slate-900/80 border-slate-700 text-slate-400 hover:border-cyan-500/50 hover:text-cyan-300"
        }`}
        title="J.A.R.V.I.S. Voice Assistant — Click to expand"
      >
        <ArcReactor status={status} />
        <span className="hidden sm:inline">J.A.R.V.I.S. Voice</span>
        <span className={`text-[10px] ${statusColor}`}>{statusLabel}</span>
      </button>

      {/* Expanded Panel */}
      {isExpanded && (
        <div className="absolute right-0 top-full mt-2 w-[360px] bg-[#0a0f1e] border border-cyan-500/40 rounded-xl shadow-2xl shadow-cyan-500/10 z-50 overflow-hidden">
          {/* Panel Header */}
          <div className="bg-gradient-to-r from-cyan-950 to-slate-900 px-4 py-3 border-b border-cyan-500/30 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <ArcReactor status={status} />
              <div>
                <div className="text-xs font-bold text-cyan-300 font-mono">
                  J.A.R.V.I.S. VOICE COMMS
                </div>
                <div className="text-[10px] text-slate-500">
                  Just a Rather Very Intelligent System
                </div>
              </div>
            </div>
            <button
              onClick={() => setIsExpanded(false)}
              className="text-slate-500 hover:text-white text-xs px-1.5 py-0.5 rounded bg-slate-800/80"
            >
              ✕
            </button>
          </div>

          {/* Status + Controls */}
          <div className="px-4 py-3 space-y-3">
            {/* Mic / Mute / Stop Row */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {/* Push-to-Talk Mic Button */}
                <button
                  onClick={status === "LISTENING" ? stopListening : startListening}
                  disabled={status === "PROCESSING" || status === "SPEAKING"}
                  className={`w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold transition-all duration-200 border-2 disabled:opacity-40 ${
                    status === "LISTENING"
                      ? "bg-amber-500/20 border-amber-400 text-amber-300 shadow-lg shadow-amber-500/30 animate-pulse"
                      : "bg-slate-800 border-slate-600 text-slate-300 hover:border-cyan-400 hover:text-cyan-300"
                  }`}
                  title={status === "LISTENING" ? "Stop listening" : "Push to talk"}
                >
                  🎙️
                </button>

                {/* Stop Audio */}
                {status === "SPEAKING" && (
                  <button
                    onClick={stopAudio}
                    className="w-8 h-8 rounded-full bg-red-900/40 border border-red-500/50 text-red-300 flex items-center justify-center text-sm hover:bg-red-800/60 transition"
                    title="Stop J.A.R.V.I.S. speaking"
                  >
                    ⏹
                  </button>
                )}
              </div>

              {/* Mute Toggle */}
              <button
                onClick={() => setIsMuted(!isMuted)}
                className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono border transition ${
                  isMuted
                    ? "bg-red-950/60 border-red-500/50 text-red-300"
                    : "bg-emerald-950/60 border-emerald-500/50 text-emerald-300"
                }`}
              >
                <span>{isMuted ? "🔇" : "🔊"}</span>
                <span>{isMuted ? "MUTED" : "ACTIVE"}</span>
              </button>
            </div>

            {/* Live Transcript */}
            {transcript && (
              <div className="bg-slate-900/80 rounded-lg border border-slate-800 px-3 py-2">
                <div className="text-[10px] text-slate-500 uppercase font-mono mb-1">
                  Operator Input
                </div>
                <div className="text-xs text-slate-300 italic">&ldquo;{transcript}&rdquo;</div>
              </div>
            )}

            {/* Last J.A.R.V.I.S. Response */}
            {lastResponse && (
              <div className="bg-cyan-950/30 rounded-lg border border-cyan-500/20 px-3 py-2">
                <div className="text-[10px] text-cyan-500 uppercase font-mono mb-1">
                  J.A.R.V.I.S. Response
                </div>
                <div className="text-xs text-cyan-200 leading-relaxed">
                  {lastResponse}
                </div>
              </div>
            )}

            {/* Quick Command Chips */}
            <div className="space-y-1.5">
              <div className="text-[10px] text-slate-500 uppercase font-mono">
                Quick Voice Commands
              </div>
              <div className="grid grid-cols-2 gap-1.5">
                {QUICK_COMMANDS.map((cmd) => (
                  <button
                    key={cmd.query}
                    onClick={() => askJarvis(cmd.query)}
                    disabled={status !== "IDLE"}
                    className="px-2.5 py-1.5 bg-slate-800/80 hover:bg-slate-700/90 border border-slate-700 hover:border-cyan-500/50 rounded-lg text-[11px] text-slate-300 hover:text-cyan-200 font-mono transition text-left truncate disabled:opacity-40 cursor-pointer"
                  >
                    {cmd.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="bg-slate-900/60 border-t border-slate-800 px-4 py-2 flex items-center justify-between">
            <span className="text-[10px] text-slate-600 font-mono">
              edge-tts · en-GB-RyanNeural
            </span>
            <span className={`text-[10px] font-mono ${statusColor}`}>
              {statusLabel}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
