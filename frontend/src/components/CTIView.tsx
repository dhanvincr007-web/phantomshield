"use client";

import React from "react";
import { 
  ShieldAlert, 
  Target, 
  Cpu, 
  Lock, 
  CheckCircle, 
  AlertTriangle, 
  Radio, 
  Layers, 
  Workflow, 
  Zap,
  Activity,
  ArrowRight,
  Bot,
  Sparkles,
  ToggleLeft,
  ToggleRight,
  ShieldCheck,
  Flame
} from "lucide-react";

export interface BlastRadiusReport {
  compromised_node: string;
  blast_radius_index: number;
  threat_severity: string;
  total_reachable_assets: number;
  crown_jewels_exposed: string[];
  crown_jewel_breach_imminent: boolean;
  containment_recommendation: string;
  hops?: Record<number, Array<{
    node_id: string;
    name: string;
    type: string;
    criticality: string;
    status: string;
    hop_depth: number;
  }>>;
}

export interface ChokePoint {
  node_id: string;
  name: string;
  type: string;
  criticality: string;
  betweenness_score: number;
  in_degree: number;
  out_degree: number;
  is_choke_point: boolean;
}

export interface TelemetryEvent {
  event_type: string;
  summary: string;
  agent_name?: string;
  full_title?: string;
  reasoning?: string;
  mode?: string;
  mitre_tactic?: string;
  target_node?: string;
  command?: string;
  mitre?: {
    technique_id: string;
    technique_name: string;
    tactic: string;
    severity: string;
  };
  time?: string;
}

interface CTIViewProps {
  blastReport: BlastRadiusReport | null;
  chokePoints: ChokePoint[];
  events: TelemetryEvent[];
  selectedNodeId: string | null;
  onContainNode: (nodeId?: string) => void;
  isContainmentLoading: boolean;
  sentinelMode?: string;
  onToggleSentinel?: () => void;
  sentinelInterventions?: number;
  lastIntervention?: any;
}

export default function CTIView({
  blastReport,
  chokePoints,
  events,
  selectedNodeId,
  onContainNode,
  isContainmentLoading,
  sentinelMode = "AUTONOMOUS_PROTECTION",
  onToggleSentinel,
  sentinelInterventions = 0,
  lastIntervention
}: CTIViewProps) {
  const riskScore = blastReport?.blast_radius_index ?? 0;
  const isHighRisk = riskScore >= 70;
  const targetNode = selectedNodeId || blastReport?.compromised_node || "decoy-ssh-01";
  const isAutonomous = sentinelMode === "AUTONOMOUS_PROTECTION";

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-red-500 border-red-500 bg-red-950/40";
    if (score >= 50) return "text-amber-400 border-amber-400 bg-amber-950/40";
    return "text-emerald-400 border-emerald-400 bg-emerald-950/40";
  };

  return (
    <div className="w-full space-y-4 font-sans">
      {/* 0. J.A.R.V.I.S. Autonomous AI Sentinel Control Widget */}
      <div className="bg-gradient-to-br from-[#071322] via-[#09152b] to-[#0d1024] border border-cyan-500/40 rounded-xl p-4 shadow-2xl relative overflow-hidden">
        {/* Glow backdrop accent */}
        <div className="absolute -top-12 -right-12 w-32 h-32 bg-cyan-500/10 rounded-full blur-2xl pointer-events-none" />

        <div className="flex items-center justify-between border-b border-cyan-500/20 pb-3 mb-3">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-cyan-950 border border-cyan-500/50 flex items-center justify-center text-cyan-300 shadow-lg shadow-cyan-500/20">
              <Bot className="w-4 h-4 text-cyan-400 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <h3 className="text-xs font-black text-white tracking-wider font-mono">
                  J.A.R.V.I.S. AI SENTINEL
                </h3>
                <span className="text-[9px] uppercase px-1.5 py-0.2 rounded bg-cyan-900/60 text-cyan-300 border border-cyan-500/40 font-mono">
                  v2.4
                </span>
              </div>
              <p className="text-[10px] text-slate-400 italic font-mono">
                Just a Rather Very Intelligent System
              </p>
            </div>
          </div>

          {/* Mode Switch Toggle Button */}
          <button
            onClick={onToggleSentinel}
            className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-lg text-[11px] font-mono font-bold transition border cursor-pointer ${
              isAutonomous
                ? "bg-emerald-950/80 border-emerald-500/60 text-emerald-300 hover:bg-emerald-900/80 shadow-md shadow-emerald-500/20"
                : "bg-amber-950/80 border-amber-500/60 text-amber-300 hover:bg-amber-900/80"
            }`}
            title="Click to toggle between Autonomous Protection and Manual Override"
          >
            {isAutonomous ? (
              <>
                <ToggleRight className="w-4 h-4 text-emerald-400" />
                <span>AUTO GUARD</span>
              </>
            ) : (
              <>
                <ToggleLeft className="w-4 h-4 text-amber-400" />
                <span>MANUAL OVERRIDE</span>
              </>
            )}
          </button>
        </div>

        {/* Sentinel Live Status Strip */}
        <div className="grid grid-cols-3 gap-2 text-center text-[11px] font-mono mb-3">
          <div className={`p-2 rounded-lg border ${
            isAutonomous 
              ? "bg-emerald-950/40 border-emerald-500/40 text-emerald-300" 
              : "bg-amber-950/40 border-amber-500/40 text-amber-300"
          }`}>
            <div className="text-[9px] uppercase text-slate-400">Sentinel Mode</div>
            <div className="font-bold truncate mt-0.5">
              {isAutonomous ? "ONLINE (AUTONOMOUS)" : "MANUAL STANDBY"}
            </div>
          </div>

          <div className="p-2 rounded-lg border border-slate-800 bg-slate-900/70 text-slate-200">
            <div className="text-[9px] uppercase text-slate-400">Trigger Threshold</div>
            <div className="font-bold text-amber-300 mt-0.5">&gt; 85% BRVI / CANARY</div>
          </div>

          <div className="p-2 rounded-lg border border-slate-800 bg-slate-900/70 text-slate-200">
            <div className="text-[9px] uppercase text-slate-400">Interventions</div>
            <div className="font-bold text-cyan-300 mt-0.5">{sentinelInterventions} Enforced</div>
          </div>
        </div>

        {/* Dynamic Safeguard Banner */}
        <div className="text-[11px] font-mono text-cyan-200/90 bg-cyan-950/40 border border-cyan-500/30 rounded-lg p-2 flex items-start space-x-2">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />
          <p className="leading-tight">
            {isAutonomous
              ? "J.A.R.V.I.S. continuously evaluates blast radii and canary breadcrumbs. Autonomous micro-segmentation fires when BRVI > 85%."
              : "Manual override active: Autonomous micro-segmentation suspended. Awaiting operator confirmation."}
          </p>
        </div>
      </div>

      {/* 1. Real-Time Blast Radius Containment Engine */}
      <div className="bg-[#090e1c] border border-slate-800 rounded-xl p-4 shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-3">
          <div className="flex items-center space-x-2">
            <Target className="w-4 h-4 text-red-400" />
            <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider">
              GraphOps Blast Radius Analytics
            </h3>
          </div>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
            Target: <span className="text-cyan-400 font-bold">{targetNode}</span>
          </span>
        </div>

        {blastReport ? (
          <div className="space-y-3">
            {/* Score & Metrics Row */}
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className={`p-2.5 rounded-lg border ${getScoreColor(riskScore)}`}>
                <div className="text-2xl font-black font-mono">{riskScore}%</div>
                <div className="text-[10px] uppercase font-bold tracking-wider mt-0.5">
                  Vulnerability Index
                </div>
              </div>

              <div className="p-2.5 rounded-lg border border-slate-800 bg-slate-900/60">
                <div className="text-2xl font-black font-mono text-cyan-400">
                  {blastReport.total_reachable_assets}
                </div>
                <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider mt-0.5">
                  Reachable Assets
                </div>
              </div>

              <div className={`p-2.5 rounded-lg border ${
                blastReport.crown_jewel_breach_imminent && riskScore > 0
                  ? 'border-red-600 bg-red-950/60 text-red-300' 
                  : 'border-slate-800 bg-slate-900/60 text-slate-400'
              }`}>
                <div className="text-2xl font-black font-mono text-purple-400">
                  {blastReport.crown_jewels_exposed.length}
                </div>
                <div className="text-[10px] uppercase font-bold tracking-wider mt-0.5">
                  Crown Jewels Exposed
                </div>
              </div>
            </div>

            {/* Imminent Breach Alert */}
            {blastReport.crown_jewel_breach_imminent && blastReport.blast_radius_index > 0 && (
              <div className="p-2.5 bg-red-950/70 border border-red-500 rounded-lg text-red-200 text-xs flex items-start space-x-2">
                <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5 animate-pulse" />
                <div className="space-y-0.5">
                  <span className="font-bold">CRITICAL ATTACK PATH DETECTED:</span>
                  <p className="text-[11px] text-red-300">
                    Direct path from <span className="font-mono text-white">{targetNode}</span> to Crown Jewel <span className="font-mono font-bold text-purple-300">CrownJewel-Vault-DB</span> is unmitigated.
                  </p>
                </div>
              </div>
            )}

            {/* Multi-Hop Breakdown */}
            {blastReport.hops && Object.keys(blastReport.hops).length > 0 && (
              <div className="space-y-1.5 text-xs">
                <div className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider flex items-center space-x-1">
                  <Layers className="w-3 h-3 text-cyan-400" />
                  <span>Traversed Hop Reachability:</span>
                </div>
                <div className="space-y-1">
                  {Object.entries(blastReport.hops).map(([hop, items]) => (
                    <div key={hop} className="flex items-center space-x-2 text-[11px] p-1.5 bg-slate-900/60 rounded border border-slate-800/80">
                      <span className="px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 font-mono font-bold">
                        Hop {hop}
                      </span>
                      <span className="text-slate-300 font-mono flex-1 truncate">
                        {items.map(i => i.name).join(", ") || "None"}
                      </span>
                      <span className="text-slate-500 text-[10px]">({items.length} nodes)</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Micro-Segmentation Quarantine Button */}
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onContainNode(targetNode);
              }}
              disabled={isContainmentLoading}
              className={`w-full py-2.5 px-3 rounded-lg font-bold text-xs flex items-center justify-center space-x-2 shadow-lg transition ${
                isContainmentLoading 
                  ? 'bg-slate-700 text-slate-300 cursor-wait'
                  : isHighRisk 
                  ? 'bg-red-600 hover:bg-red-500 text-white animate-pulse cursor-pointer' 
                  : 'bg-cyan-600 hover:bg-cyan-500 text-black cursor-pointer'
              }`}
            >
              <Lock className="w-4 h-4" />
              <span>
                {isContainmentLoading 
                  ? "Quarantining & Severing Egress Paths..." 
                  : "🛡️ Trigger Micro-Segmentation Containment"}
              </span>
            </button>
          </div>
        ) : (
          <div className="text-center py-6 text-slate-500 text-xs font-mono">
            Calculating topological blast radius...
          </div>
        )}
      </div>

      {/* 2. Strategic Choke Points & Centrality Leaderboard */}
      <div className="bg-[#090e1c] border border-slate-800 rounded-xl p-4 shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-3">
          <div className="flex items-center space-x-2">
            <Workflow className="w-4 h-4 text-cyan-400" />
            <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider">
              Betweenness Centrality & Choke Points
            </h3>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
            Algorithm: C_B(v)
          </span>
        </div>

        <p className="text-[11px] text-slate-400 mb-3 leading-relaxed">
          Nodes with highest Betweenness Centrality act as critical bottlenecks. Placing AI deception honeytokens here neutralizes attack velocity before crown jewels are reached.
        </p>

        <div className="space-y-1.5">
          {chokePoints.slice(0, 4).map((cp, idx) => (
            <div 
              key={cp.node_id}
              className={`flex items-center justify-between p-2 rounded-lg border text-xs ${
                cp.is_choke_point 
                  ? 'bg-cyan-950/30 border-cyan-500/50 text-slate-200' 
                  : 'bg-slate-900/40 border-slate-800/80 text-slate-400'
              }`}
            >
              <div className="flex items-center space-x-2 truncate">
                <span className="font-mono text-[10px] text-cyan-400 font-bold">#{idx + 1}</span>
                <span className="font-semibold text-slate-200 truncate">{cp.name}</span>
                {cp.is_choke_point && (
                  <span className="px-1.5 py-0.2 rounded bg-amber-950 text-amber-300 border border-amber-600/60 font-mono text-[9px]">
                    CHOKE POINT
                  </span>
                )}
              </div>

              <div className="flex items-center space-x-2 font-mono text-[11px] shrink-0">
                <span className="text-slate-400">Score:</span>
                <span className="text-cyan-300 font-bold">{cp.betweenness_score}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 3. Live MITRE ATT&CK Telemetry Stream & J.A.R.V.I.S. Telepathy Feed */}
      <div className="bg-[#090e1c] border border-slate-800 rounded-xl p-4 shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-2.5">
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-emerald-400" />
            <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider">
              Live MITRE ATT&CK & J.A.R.V.I.S. Stream
            </h3>
          </div>
          <span className="flex items-center space-x-1.5 text-[10px] text-emerald-400 font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
            <span>WebSocket Live</span>
          </span>
        </div>

        <div className="space-y-2 max-h-56 overflow-y-auto text-xs pr-1">
          {events.length > 0 ? (
            events.map((ev, index) => {
              const isJarvisEvent = ev.agent_name === "J.A.R.V.I.S." || ev.event_type === "SENTINEL_SAFEGUARD_TRIGGERED";
              
              if (isJarvisEvent) {
                return (
                  <div key={index} className="p-2.5 bg-gradient-to-r from-cyan-950/90 via-blue-950/80 to-purple-950/80 rounded-lg border border-cyan-400/60 space-y-1.5 shadow-md shadow-cyan-500/10">
                    <div className="flex items-center justify-between text-[10px]">
                      <div className="flex items-center space-x-1 text-cyan-300 font-bold font-mono">
                        <Bot className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
                        <span>J.A.R.V.I.S. SENTINEL SAFEGUARD</span>
                      </div>
                      <span className="px-1.5 py-0.2 rounded bg-purple-950 text-purple-300 border border-purple-500 font-mono font-bold">
                        AUTONOMOUS INTERVENTION
                      </span>
                    </div>
                    <p className="text-cyan-100 text-[11px] font-mono leading-tight">
                      {ev.reasoning || ev.summary}
                    </p>
                    <div className="flex items-center justify-between text-[9.5px] font-mono text-cyan-400/80 pt-0.5 border-t border-cyan-500/20">
                      <span>Target: {ev.target_node || "decoy-ssh-01"}</span>
                      <span>BRVI $\to$ 0.0% (SECURE)</span>
                    </div>
                  </div>
                );
              }

              return (
                <div key={index} className="p-2 bg-slate-900/80 rounded border border-slate-800 space-y-1">
                  <div className="flex items-center justify-between text-[10px]">
                    <span className="font-mono text-cyan-400 font-semibold">{ev.event_type}</span>
                    {ev.mitre && (
                      <span className="px-1.5 py-0.2 rounded bg-red-950 text-red-300 border border-red-700/60 font-mono font-bold">
                        {ev.mitre.technique_id}
                      </span>
                    )}
                  </div>
                  <p className="text-slate-300 text-[11px] font-sans leading-tight">
                    {ev.summary}
                  </p>
                </div>
              );
            })
          ) : (
            <div className="text-center py-4 text-slate-500 text-xs font-mono">
              Waiting for honeypot telemetry stream...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
