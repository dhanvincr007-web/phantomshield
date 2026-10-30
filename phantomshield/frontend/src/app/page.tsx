"use client";

import React, { useState, useEffect, useCallback } from "react";
import { 
  ShieldAlert, 
  Terminal, 
  Share2, 
  Play, 
  RefreshCw, 
  Users, 
  Award
} from "lucide-react";

import GraphView, { GraphNode, GraphEdge } from "@/components/GraphView";
import ShellView from "@/components/ShellView";
import CTIView, { BlastRadiusReport, ChokePoint, TelemetryEvent } from "@/components/CTIView";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const WS_BASE = API_BASE.replace(/^http/, "ws");

export default function DashboardPage() {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>("DMZ-Web-Prod");
  const [blastReport, setBlastReport] = useState<BlastRadiusReport | null>(null);
  const [chokePoints, setChokePoints] = useState<ChokePoint[]>([]);
  const [telemetryEvents, setTelemetryEvents] = useState<TelemetryEvent[]>([]);
  
  const [activeTab, setActiveTab] = useState<"graph" | "split" | "shell">("split");
  const [wsConnected, setWsConnected] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isContainmentLoading, setIsContainmentLoading] = useState(false);
  const [showTeamModal, setShowTeamModal] = useState(false);

  const fetchGraphData = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/graph`);
      if (res.ok) {
        const data = await res.json();
        setNodes(data.nodes || []);
        setEdges(data.edges || []);
      }
    } catch {
      console.warn("Backend not reached yet, using default topology state.");
    }
  }, []);

  const fetchBlastRadius = useCallback(async (nodeId: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/blast-radius?node_id=${encodeURIComponent(nodeId)}&hops=3`);
      if (res.ok) {
        const data = await res.json();
        setBlastReport(data);
      }
    } catch {
      console.warn("Failed to fetch blast radius.");
    }
  }, []);

  const fetchCentrality = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/centrality`);
      if (res.ok) {
        const data = await res.json();
        setChokePoints(data.strategic_choke_points || []);
      }
    } catch {
      console.warn("Failed to fetch centrality.");
    }
  }, []);

  useEffect(() => {
    fetchGraphData();
    fetchCentrality();
  }, [fetchGraphData, fetchCentrality]);

  useEffect(() => {
    if (selectedNodeId) {
      fetchBlastRadius(selectedNodeId);
    }
  }, [selectedNodeId, fetchBlastRadius]);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimer: NodeJS.Timeout | null = null;

    const connectWebSocket = () => {
      try {
        ws = new WebSocket(`${WS_BASE}/ws/telemetry`);

        ws.onopen = () => {
          setWsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            setTelemetryEvents((prev) => [data, ...prev.slice(0, 50)]);

            if (["GRAPH_SEEDED", "NODE_CONTAINED", "DECEPTION_TRAP_TRIGGERED", "SIMULATION_AUTO_CONTAINED"].includes(data.event_type)) {
              fetchGraphData();
              fetchCentrality();
              if (selectedNodeId) fetchBlastRadius(selectedNodeId);
            }
          } catch (e) {
            console.error("WebSocket message parse error:", e);
          }
        };

        ws.onclose = () => {
          setWsConnected(false);
          reconnectTimer = setTimeout(connectWebSocket, 3000);
        };

        ws.onerror = () => {
          ws?.close();
        };
      } catch (err) {
        reconnectTimer = setTimeout(connectWebSocket, 3000);
      }
    };

    connectWebSocket();

    return () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      ws?.close();
    };
  }, [fetchGraphData, fetchCentrality, fetchBlastRadius, selectedNodeId]);

  const handleExecuteCommand = async (command: string) => {
    const res = await fetch(`${API_BASE}/api/shell/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command }),
    });
    const data = await res.json();
    
    fetchGraphData();
    if (selectedNodeId) fetchBlastRadius(selectedNodeId);

    return data;
  };

  const handleContainNode = async (nodeId: string) => {
    setIsContainmentLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/contain`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ node_id: nodeId }),
      });
      if (res.ok) {
        await fetchGraphData();
        await fetchBlastRadius(nodeId);
      }
    } finally {
      setIsContainmentLoading(false);
    }
  };

  const handleSeedDatabase = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/seed`, { method: "POST" });
      if (res.ok) {
        await fetchGraphData();
        await fetchCentrality();
        if (selectedNodeId) await fetchBlastRadius(selectedNodeId);
      }
    } catch {
      console.warn("Failed to seed database.");
    }
  };

  const handleSimulateAttack = async () => {
    setIsSimulating(true);
    try {
      await fetch(`${API_BASE}/api/simulate-attack`, { method: "POST" });
      await fetchGraphData();
      await fetchCentrality();
      if (selectedNodeId) await fetchBlastRadius(selectedNodeId);
    } finally {
      setIsSimulating(false);
    }
  };

  const blastNodeIds: string[] = [];
  if (blastReport?.hops) {
    Object.values(blastReport.hops).forEach((hopList) => {
      hopList.forEach((item) => blastNodeIds.push(item.node_id));
    });
  }

  return (
    <div className="min-h-screen bg-[#050811] text-slate-100 flex flex-col">
      <header className="border-b border-slate-800 bg-[#090e1c] px-6 py-3.5 flex flex-wrap items-center justify-between gap-4 sticky top-0 z-50 backdrop-blur-md">
        <div className="flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 via-blue-600 to-indigo-600 p-0.5 shadow-lg shadow-cyan-500/20">
            <div className="w-full h-full bg-[#070b16] rounded-[10px] flex items-center justify-center">
              <ShieldAlert className="w-5 h-5 text-cyan-400" />
            </div>
          </div>

          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-base font-black tracking-wide text-white flex items-center space-x-1.5">
                <span>PhantomShield</span>
                <span className="text-cyan-400 font-mono text-xs px-1.5 py-0.5 bg-cyan-950/80 rounded border border-cyan-500/40">
                  GraphShield AI
                </span>
              </h1>
              <span className="text-[10px] uppercase font-bold px-2 py-0.5 bg-purple-950 text-purple-300 rounded border border-purple-600/40 font-mono">
                hackFront India 2026
              </span>
            </div>
            <p className="text-xs text-slate-400">
              GraphOps Engine for Autonomous Threat Hunting, AI Deception & Real-Time Blast Radius Containment
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-medium border ${
            wsConnected 
              ? 'bg-emerald-950/80 border-emerald-500/50 text-emerald-300' 
              : 'bg-red-950/80 border-red-500/50 text-red-300'
          }`}>
            <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-emerald-400 animate-ping' : 'bg-red-500'}`} />
            <span>{wsConnected ? "SOC Stream Live" : "Offline Simulation"}</span>
          </div>

          <button
            onClick={handleSimulateAttack}
            disabled={isSimulating}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white rounded-lg font-bold text-xs shadow-lg shadow-red-600/20 transition disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{isSimulating ? "Simulating Attack..." : "Simulate Cyber Attack"}</span>
          </button>

          <button
            onClick={handleSeedDatabase}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium border border-slate-700 transition"
            title="Reset to default enterprise network topology"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reset Graph</span>
          </button>

          <button
            onClick={() => setShowTeamModal(true)}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-cyan-950/60 hover:bg-cyan-900/80 border border-cyan-500/40 text-cyan-300 rounded-lg text-xs font-medium transition"
          >
            <Users className="w-3.5 h-3.5" />
            <span>Team & Problem</span>
          </button>
        </div>
      </header>

      <main className="flex-1 p-6 grid grid-cols-1 xl:grid-cols-12 gap-6 max-w-[1920px] mx-auto w-full">
        <div className="xl:col-span-8 flex flex-col space-y-4">
          <div className="flex items-center justify-between bg-[#090e1c] p-1.5 rounded-xl border border-slate-800">
            <div className="flex space-x-1">
              <button
                onClick={() => setActiveTab("split")}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center space-x-1.5 ${
                  activeTab === "split" ? "bg-cyan-600 text-black shadow" : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <span>Dual View (Graph + Terminal)</span>
              </button>
              <button
                onClick={() => setActiveTab("graph")}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center space-x-1.5 ${
                  activeTab === "graph" ? "bg-cyan-600 text-black shadow" : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <Share2 className="w-3.5 h-3.5" />
                <span>Full Graph Visualizer</span>
              </button>
              <button
                onClick={() => setActiveTab("shell")}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center space-x-1.5 ${
                  activeTab === "shell" ? "bg-cyan-600 text-black shadow" : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <Terminal className="w-3.5 h-3.5" />
                <span>Attacker Terminal</span>
              </button>
            </div>

            <span className="text-[11px] text-slate-500 font-mono pr-2">
              Neo4j Cypher Engine • NetworkX Centrality • MITRE ATT&CK
            </span>
          </div>

          {activeTab === "split" && (
            <div className="space-y-4">
              <GraphView
                nodes={nodes}
                edges={edges}
                selectedNodeId={selectedNodeId}
                blastRadiusNodes={blastNodeIds}
                onSelectNode={(id) => setSelectedNodeId(id)}
                onContainNode={handleContainNode}
                onRefresh={fetchGraphData}
                isSimulating={isSimulating}
              />
              <ShellView onExecuteCommand={handleExecuteCommand} />
            </div>
          )}

          {activeTab === "graph" && (
            <div className="h-[800px]">
              <GraphView
                nodes={nodes}
                edges={edges}
                selectedNodeId={selectedNodeId}
                blastRadiusNodes={blastNodeIds}
                onSelectNode={(id) => setSelectedNodeId(id)}
                onContainNode={handleContainNode}
                onRefresh={fetchGraphData}
                isSimulating={isSimulating}
              />
            </div>
          )}

          {activeTab === "shell" && (
            <div className="h-[800px]">
              <ShellView onExecuteCommand={handleExecuteCommand} />
            </div>
          )}
        </div>

        <div className="xl:col-span-4">
          <CTIView
            blastReport={blastReport}
            chokePoints={chokePoints}
            events={telemetryEvents}
            selectedNodeId={selectedNodeId}
            onContainNode={handleContainNode}
            isContainmentLoading={isContainmentLoading}
          />
        </div>
      </main>

      {showTeamModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0b1222] border border-cyan-500/50 rounded-2xl max-w-xl w-full p-6 shadow-2xl relative space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2">
                <Award className="w-5 h-5 text-cyan-400" />
                <h2 className="text-base font-black text-white">PhantomShield (GraphShield AI)</h2>
              </div>
              <button
                onClick={() => setShowTeamModal(false)}
                className="text-slate-400 hover:text-white font-mono text-sm px-2 py-0.5 rounded bg-slate-800"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs leading-relaxed text-slate-300">
              <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800 space-y-1">
                <div className="font-bold text-cyan-300">hackFront India 2026 (Edition 01)</div>
                <div><span className="text-slate-400">Track:</span> Cybersecurity Track → Neo4j Track</div>
                <div>
                  <span className="text-slate-400">Problem Statement:</span> GraphOps: Graph analytics for proactive threat hunting and blast radius containment in security operations centers
                </div>
              </div>

              <div>
                <h4 className="font-bold text-slate-200 mb-2 uppercase tracking-wider text-[11px]">
                  Team Members:
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 font-mono">
                  <div className="p-2 bg-slate-900/60 rounded border border-slate-800">
                    <div className="font-bold text-cyan-300">1. Dhanvin (Team Lead)</div>
                    <div className="text-slate-500 text-[10px]">dhanvincr007@gmail.com</div>
                  </div>
                  <div className="p-2 bg-slate-900/60 rounded border border-slate-800">
                    <div className="font-bold text-slate-200">2. Pragathish Palsamy</div>
                    <div className="text-slate-500 text-[10px]">pragathishpalsamy@gmail.com</div>
                  </div>
                  <div className="p-2 bg-slate-900/60 rounded border border-slate-800">
                    <div className="font-bold text-slate-200">3. P.V. Krishnan</div>
                    <div className="text-slate-500 text-[10px]">pvkrishnan38@gmail.com</div>
                  </div>
                  <div className="p-2 bg-slate-900/60 rounded border border-slate-800">
                    <div className="font-bold text-slate-200">4. Mohamed Annas</div>
                    <div className="text-slate-500 text-[10px]">mohamedannas023@gmail.com</div>
                  </div>
                  <div className="p-2 bg-slate-900/60 rounded border border-slate-800 sm:col-span-2">
                    <div className="font-bold text-slate-200">5. MANO G</div>
                    <div className="text-slate-500 text-[10px]">rr0839880@gmail.com</div>
                  </div>
                </div>
              </div>

              <div className="p-3 bg-cyan-950/40 border border-cyan-500/30 rounded-lg space-y-1">
                <span className="font-bold text-cyan-300">Core Architecture:</span>
                <p className="text-slate-400 text-[11px]">
                  Neo4j Cypher knowledge graph transforms siloed logs into multi-hop attack graphs. AI Deception honeypots drop strategic honeytokens at choke points identified via Betweenness Centrality, collapsing attacker velocity and executing real-time blast radius micro-segmentation.
                </p>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setShowTeamModal(false)}
                className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-black font-bold rounded-lg text-xs"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

