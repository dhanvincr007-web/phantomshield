"use client";

import React from "react";
import { 
  ShieldAlert, 
  Target, 
  Lock, 
  AlertTriangle, 
  Layers, 
  Workflow, 
  Activity
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
  onContainNode: (nodeId: string) => void;
  isContainmentLoading: boolean;
}

export default function CTIView({
  blastReport,
  chokePoints,
  events,
  selectedNodeId,
  onContainNode,
  isContainmentLoading
}: CTIViewProps) {
  const riskScore = blastReport?.blast_radius_index ?? 0;
  const isHighRisk = riskScore >= 70;
  const targetNode = selectedNodeId || blastReport?.compromised_node || "DMZ-Web-Prod";

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-red-500 border-red-500 bg-red-950/40";
    if (score >= 50) return "text-amber-400 border-amber-400 bg-amber-950/40";
    return "text-emerald-400 border-emerald-400 bg-emerald-950/40";
  };

  return (
    <div className="w-full space-y-4">
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
            Node: <span className="text-cyan-400 font-bold">{targetNode}</span>
          </span>
        </div>

        {blastReport ? (
          <div className="space-y-3">
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className={`p-2.5 rounded-lg border ${getScoreColor(riskScore)}`}>
                <div className="text-2xl font-black font-mono">{riskScore}</div>
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
                blastReport.crown_jewel_breach_imminent 
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

            {blastReport.crown_jewel_breach_imminent && (
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

            {blastReport.hops && (
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

            <button
              onClick={() => onContainNode(targetNode)}
              disabled={isContainmentLoading}
              className={`w-full py-2.5 px-3 rounded-lg font-bold text-xs flex items-center justify-center space-x-2 shadow-lg transition ${
                isHighRisk 
                  ? 'bg-red-600 hover:bg-red-500 text-white animate-pulse' 
                  : 'bg-cyan-600 hover:bg-cyan-500 text-black'
              }`}
            >
              <Lock className="w-4 h-4" />
              <span>
                {isContainmentLoading 
                  ? "Quarantining & Severing Egress Paths..." 
                  : `Trigger Autonomous Micro-Segmentation (${targetNode})`}
              </span>
            </button>
          </div>
        ) : (
          <div className="text-center py-6 text-slate-500 text-xs">
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

      {/* 3. Live MITRE ATT&CK Telemetry Stream */}
      <div className="bg-[#090e1c] border border-slate-800 rounded-xl p-4 shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-2.5">
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-emerald-400" />
            <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider">
              Live MITRE ATT&CK Telemetry
            </h3>
          </div>
          <span className="flex items-center space-x-1.5 text-[10px] text-emerald-400 font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
            <span>WebSocket Live</span>
          </span>
        </div>

        <div className="space-y-2 max-h-48 overflow-y-auto text-xs pr-1">
          {events.length > 0 ? (
            events.map((ev, index) => (
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
            ))
          ) : (
            <div className="text-center py-4 text-slate-500 text-xs">
              Waiting for honeypot telemetry stream...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

