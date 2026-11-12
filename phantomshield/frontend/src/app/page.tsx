"use client";

import React, { useState, useEffect, useCallback, useRef } from "react";
import {
  ShieldAlert,
  Terminal,
  Share2,
  Play,
  RefreshCw,
  Users,
  Sparkles,
  Lock,
  Radio,
  AlertCircle,
  HelpCircle,
  Award,
  ExternalLink,
  Flame,
  CheckCircle2,
  Cpu,
  ChevronRight,
  ShieldCheck,
  Zap,
  RotateCcw
} from "lucide-react";

import GraphView, { GraphNode, GraphEdge } from "@/components/GraphView";
import ShellView from "@/components/ShellView";
import CTIView, { BlastRadiusReport, ChokePoint, TelemetryEvent } from "@/components/CTIView";
import JarvisVoiceAssistant from "@/components/JarvisVoiceAssistant";

const RAW_API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_BASE = RAW_API_BASE.trim().replace(/\/+$/, "");
const WS_BASE = API_BASE.replace(/^http/, "ws");

const SCENARIO_STAGES = [
  {
    step: 1,
    title: "Reconnaissance",
    mitre: "TA0007: System Info Discovery",
    desc: "Attacker probes decoy-ssh-01 running whoami and uname -a",
    badge: "0s - RECON",
  },
  {
    step: 2,
    title: "Credential Dumping",
    mitre: "TA0006: Credential Access",
    desc: "Attacker attempts shadow file dump; trips canary AKIA_CANARY_PHANTOM_99",
    badge: "2s - CANARY TRIPPED",
  },
  {
    step: 3,
    title: "Real-Time Blast Radius",
    mitre: "GraphOps: Multi-Hop Risk",
    desc: "Calculates 3-hop blast radius; BRVI spikes to 92% (CRITICAL) exposing Crown Jewel Vault",
    badge: "4s - BRVI 92%",
  },
  {
    step: 4,
    title: "Choke Point Analysis",
    mitre: "Network Centrality",
    desc: "Betweenness centrality flags Internal-Core-Switch as the strategic bridge",
    badge: "6s - CHOKE POINT",
  },
  {
    step: 5,
    title: "Autonomous Micro-Segmentation",
    mitre: "Containment & Remediation",
    desc: "Autonomous graph isolation severs egress edges; collapses BRVI down to 0% (SECURE)",
    badge: "8s - CONTAINED",
  },
];

export default function DashboardPage() {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>("decoy-ssh-01");
  const [blastReport, setBlastReport] = useState<BlastRadiusReport | null>(null);
  const [chokePoints, setChokePoints] = useState<ChokePoint[]>([]);
  const [telemetryEvents, setTelemetryEvents] = useState<TelemetryEvent[]>([]);

  const [activeTab, setActiveTab] = useState<"triple" | "split" | "graph" | "shell">("split");
  const [wsConnected, setWsConnected] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isContainmentLoading, setIsContainmentLoading] = useState(false);
  const [showTeamModal, setShowTeamModal] = useState(false);

  // Scenario Execution State
  const [isScenarioRunning, setIsScenarioRunning] = useState(false);
  const [currentScenarioStep, setCurrentScenarioStep] = useState<number>(0);
  const [scenarioBannerText, setScenarioBannerText] = useState<string | null>(null);

  // J.A.R.V.I.S. Autonomous AI Sentinel State
  const [sentinelMode, setSentinelMode] = useState<string>("AUTONOMOUS_PROTECTION");
  const [sentinelInterventions, setSentinelInterventions] = useState<number>(0);
  const [lastIntervention, setLastIntervention] = useState<any>(null);

  // 1. Fetch Graph Topology
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

  // 2. Fetch Blast Radius for Selected Node
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

  // 3. Fetch Centrality and Choke Points
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

  // 3b. Fetch J.A.R.V.I.S. Sentinel Status
  const fetchSentinelStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/sentinel/status`);
      if (res.ok) {
        const data = await res.json();
        setSentinelMode(data.mode || "AUTONOMOUS_PROTECTION");
        setSentinelInterventions(data.intervention_count || 0);
      }
    } catch {
      console.warn("Failed to fetch sentinel status.");
    }
  }, []);

  // Initial Load
  useEffect(() => {
    fetchGraphData();
    fetchCentrality();
    fetchSentinelStatus();
  }, [fetchGraphData, fetchCentrality, fetchSentinelStatus]);

  // Update blast radius when selected node changes
  useEffect(() => {
    if (selectedNodeId) {
      fetchBlastRadius(selectedNodeId);
    }
  }, [selectedNodeId, fetchBlastRadius]);

  // 4. WebSocket Telemetry Listener
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

            // Handle Scenario Progression
            if (data.event_type === "SCENARIO_STAGE_CHANGE") {
              const stageNum = data.step || data.payload?.stage || 1;
              setCurrentScenarioStep(stageNum);
              setScenarioBannerText(data.summary || data.title || `Stage ${stageNum}/5 executing...`);
              setIsScenarioRunning(true);

              if (stageNum >= 2) {
                setSelectedNodeId("decoy-ssh-01");
              }

              // Refresh topology & blast radius live during scenario
              fetchGraphData();
              fetchCentrality();
              fetchBlastRadius("decoy-ssh-01");

              if (stageNum === 5) {
                setTimeout(() => {
                  setIsScenarioRunning(false);
                }, 3000);
              }
            }

            // Handle Graph Reset
            if (data.event_type === "GRAPH_RESET") {
              setCurrentScenarioStep(0);
              setIsScenarioRunning(false);
              setScenarioBannerText("Graph restored to baseline healthy state.");
              fetchGraphData();
              fetchCentrality();
              setSelectedNodeId("decoy-ssh-01");
              fetchBlastRadius("decoy-ssh-01");
            }

            // Handle J.A.R.V.I.S. Sentinel Mode Change
            if (data.event_type === "SENTINEL_MODE_CHANGED") {
              setSentinelMode(data.mode || data.new_mode || "AUTONOMOUS_PROTECTION");
            }

            // Handle J.A.R.V.I.S. Autonomous Safeguard Triggered
            if (data.event_type === "SENTINEL_SAFEGUARD_TRIGGERED") {
              setSentinelInterventions(prev => prev + 1);
              setLastIntervention(data);
              setBlastReport({
                compromised_node: data.target_node || "decoy-ssh-01",
                blast_radius_index: 0,
                threat_severity: "SECURE",
                total_reachable_assets: 0,
                crown_jewels_exposed: [],
                crown_jewel_breach_imminent: false,
                containment_recommendation: data.reasoning || "Autonomous micro-segmentation enforced by J.A.R.V.I.S.",
                hops: {}
              });
              setNodes(prev => prev.map(n =>
                (n.id === data.target_node || n.id === "decoy-ssh-01")
                  ? { ...n, status: "ISOLATED", last_alert: `Autonomous quarantine by J.A.R.V.I.S.` }
                  : n
              ));
              setEdges(prev => prev.map(e =>
                (e.source === data.target_node || e.target === data.target_node || e.source === "decoy-ssh-01")
                  ? { ...e, status: "QUARANTINED" }
                  : e
              ));
              fetchGraphData();
              fetchCentrality();
            }

            // Refresh graph if an event altered topology or status
            if ([
              "GRAPH_SEEDED",
              "NODE_CONTAINED",
              "DECEPTION_TRAP_TRIGGERED",
              "SIMULATION_AUTO_CONTAINED",
              "BLAST_RADIUS_COMPUTED",
              "CENTRALITY_COMPUTED",
              "SENTINEL_SAFEGUARD_TRIGGERED"
            ].includes(data.event_type)) {
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
      } catch {
        reconnectTimer = setTimeout(connectWebSocket, 3000);
      }
    };

    connectWebSocket();

    return () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      ws?.close();
    };
  }, [fetchGraphData, fetchCentrality, fetchBlastRadius, selectedNodeId]);

  // 5. Shell Command Execution Handler (Bound to /api/execute)
  const handleExecuteCommand = async (command: string) => {
    let data;
    try {
      const res = await fetch(`${API_BASE}/api/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command }),
      });
      if (res.ok) {
        data = await res.json();
      } else {
        const res2 = await fetch(`${API_BASE}/api/shell/execute`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ command }),
        });
        data = await res2.json();
      }
    } catch {
      // Local high-fidelity honeypot simulation fallback
      data = {
        output: command === "whoami" ? "www-data" :
          command === "cat /etc/passwd" ? "root:x:0:0:root:/root:/bin/bash\nwww-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\noperator:x:1001:1001:Operator:/home/operator:/bin/bash" :
            command.includes("shadow.kdbx") ? "=== KEEPASS CANARY VAULT ===\nUsername: admin_vault\nSecretKey: AKIA_CANARY_PHANTOM_99\nTarget: http://10.0.0.50:8200" :
              `[Honeypot Sandbox] Executed '${command}'.`,
        alert_triggered: command.includes("shadow.kdbx"),
        alert_details: command.includes("shadow.kdbx") ? "CANARY_ALERT: AKIA_CANARY_PHANTOM_99 tripped" : undefined,
        mitre_technique: {
          technique_id: command.includes("shadow.kdbx") ? "T1552.004" : (command === "whoami" ? "T1033" : "T1003.008"),
          technique_name: command.includes("shadow.kdbx") ? "Unsecured Credentials" : (command === "whoami" ? "System Discovery" : "OS Credential Dumping"),
          tactic: command.includes("shadow.kdbx") ? "Credential Access" : "Discovery",
          severity: command.includes("shadow.kdbx") ? "CRITICAL" : "HIGH"
        }
      };
    }

    // If canary was tripped, update state immediately
    if (data.alert_triggered || command.includes("shadow.kdbx")) {
      setSelectedNodeId("decoy-ssh-01");
      setNodes(prev => prev.map(n =>
        (n.id === "decoy-ssh-01" || n.id === "Honey-Bastion-SSH")
          ? { ...n, status: "COMPROMISED", last_alert: "Canary AKIA_CANARY_PHANTOM_99 tripped" }
          : n
      ));
      fetchBlastRadius("decoy-ssh-01");
      setTelemetryEvents(prev => [
        {
          event_type: "DECEPTION_TRAP_TRIGGERED",
          summary: `ALERT: Attacker executed '${command}'. MITRE: T1552.004 (Unsecured Credentials: AKIA_CANARY_PHANTOM_99)`,
          time: new Date().toLocaleTimeString(),
          mitre: data.mitre_technique
        },
        ...prev.slice(0, 50)
      ]);
    } else {
      fetchGraphData();
      if (selectedNodeId) fetchBlastRadius(selectedNodeId);
    }

    return data;
  };

  // 6. Autonomous Containment Action (Bound to POST /api/graph/contain)
  const handleContainNode = async (nodeId?: string) => {
    setIsContainmentLoading(true);
    const target = nodeId || selectedNodeId || "decoy-ssh-01";
    try {
      let res = await fetch(`${API_BASE}/api/graph/contain`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ node_id: target }),
      });
      if (!res.ok) {
        res = await fetch(`${API_BASE}/api/contain`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ node_id: target }),
        });
      }
    } catch (err) {
      console.warn("Containment API request handled:", err);
    } finally {
      // 1. Set brvi score from 92 down to 0 & clear red critical alert banner
      setBlastReport({
        compromised_node: target,
        blast_radius_index: 0,
        threat_severity: "SECURE",
        total_reachable_assets: 0,
        crown_jewels_exposed: [],
        crown_jewel_breach_imminent: false,
        containment_recommendation: "Threat contained. Egress paths severed. Risk collapsed to 0.0%.",
        hops: {}
      });

      // 2. Update graph node statuses so compromised nodes display as ISOLATED (Purple/Gray ring)
      setNodes(prev => prev.map(n =>
        (n.id === target || n.status === "COMPROMISED" || n.id === "decoy-ssh-01" || n.id === "Honey-Bastion-SSH")
          ? { ...n, status: "ISOLATED", last_alert: "Quarantined by Operator" }
          : n
      ));

      // 3. Sever edges in graph state
      setEdges(prev => prev.map(e =>
        (e.source === target || e.target === target || e.source === "decoy-ssh-01" || e.source === "Honey-Bastion-SSH")
          ? { ...e, status: "QUARANTINED" }
          : e
      ));

      // 4. Append live log to LIVE MITRE ATT&CK TELEMETRY
      setTelemetryEvents(prev => [
        {
          event_type: "NODE_CONTAINED",
          summary: "NODE_CONTAINED: Egress paths severed. Blast radius collapsed to 0.0%",
          time: new Date().toLocaleTimeString(),
          mitre: {
            technique_id: "CONTAINMENT",
            technique_name: "Micro-Segmentation",
            tactic: "Remediation",
            severity: "LOW"
          }
        },
        ...prev.slice(0, 50)
      ]);

      // 5. Restore button text back once the async call resolves
      setIsContainmentLoading(false);

      // Sync fresh graph topology
      await fetchGraphData();
    }
  };

  // 7. Seed Database Action
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

  // 8. Reset Infrastructure Graph Action (Bound to POST /api/graph/reset)
  const handleResetGraph = async () => {
    try {
      await fetch(`${API_BASE}/api/graph/reset`, { method: "POST" });
    } catch (e) {
      console.warn("Reset graph API warning:", e);
    } finally {
      setCurrentScenarioStep(0);
      setIsScenarioRunning(false);
      setScenarioBannerText("Graph restored to baseline healthy state.");

      // Reset brvi to baseline 0%
      setBlastReport({
        compromised_node: "None",
        blast_radius_index: 0,
        threat_severity: "HEALTHY",
        total_reachable_assets: 0,
        crown_jewels_exposed: [],
        crown_jewel_breach_imminent: false,
        containment_recommendation: "Perimeter secure. All systems nominal.",
        hops: {}
      });

      // Clear logs
      setTelemetryEvents([]);

      // Restore initial topology edges and fetch fresh state
      await fetchGraphData();
      await fetchCentrality();
      setSelectedNodeId("DMZ-Web-Prod");
    }
  };

  // 8b. Toggle J.A.R.V.I.S. Sentinel Autonomous Protection Mode
  const handleToggleSentinel = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/sentinel/toggle`, { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setSentinelMode(data.mode);
        setTelemetryEvents(prev => [
          {
            event_type: "SENTINEL_MODE_CHANGED",
            summary: `J.A.R.V.I.S. operational mode switched to ${data.mode}. Safeguards active: ${data.mode === "AUTONOMOUS_PROTECTION" ? "ENGAGED" : "MANUAL STANDBY"}`,
            agent_name: "J.A.R.V.I.S.",
            full_title: "Just a Rather Very Intelligent System",
            mode: data.mode,
            time: new Date().toLocaleTimeString(),
          },
          ...prev
        ]);
      } else {
        const nextMode = sentinelMode === "AUTONOMOUS_PROTECTION" ? "MANUAL_OVERRIDE" : "AUTONOMOUS_PROTECTION";
        setSentinelMode(nextMode);
      }
    } catch {
      const nextMode = sentinelMode === "AUTONOMOUS_PROTECTION" ? "MANUAL_OVERRIDE" : "AUTONOMOUS_PROTECTION";
      setSentinelMode(nextMode);
    }
  };

  // 9. Run Live Judge Attack Simulation (Bound to POST /api/simulation/run-scenario)
  const handleRunJudgeScenario = async () => {
    setIsScenarioRunning(true);
    setCurrentScenarioStep(1);
    setScenarioBannerText("Stage 1/5: Reconnaissance (whoami, uname -a). Attacker executing system discovery.");
    setSelectedNodeId("decoy-ssh-01");

    // Add immediate Step 1 telemetry log
    setTelemetryEvents(prev => [
      {
        event_type: "SCENARIO_STAGE_CHANGE",
        summary: "Stage 1/5: Reconnaissance (whoami, uname -a). Attacker executing system discovery.",
        time: new Date().toLocaleTimeString(),
        mitre: {
          technique_id: "TA0007",
          technique_name: "System Information Discovery",
          tactic: "Discovery",
          severity: "HIGH"
        }
      },
      ...prev
    ]);

    try {
      const res = await fetch(`${API_BASE}/api/simulation/run-scenario`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (res.ok) {
        const data = await res.json();
        // If WebSocket is not connected, playback timeline directly
        if (!wsConnected && data.timeline) {
          data.timeline.forEach((item: any, idx: number) => {
            setTimeout(() => {
              setCurrentScenarioStep(item.step || idx + 1);
              setScenarioBannerText(item.summary || item.title);
              if (item.step >= 2) setSelectedNodeId("decoy-ssh-01");
              setTelemetryEvents(prev => [item, ...prev.slice(0, 50)]);
              fetchGraphData();
              fetchCentrality();
              fetchBlastRadius("decoy-ssh-01");
            }, idx * 1500);
          });
        }
      } else {
        runLocalScenarioAnimation();
      }
    } catch (err) {
      console.warn("Running client-driven scenario animation:", err);
      runLocalScenarioAnimation();
    }
  };

  const runLocalScenarioAnimation = () => {
    // Step 2 at 2s
    setTimeout(() => {
      setCurrentScenarioStep(2);
      setScenarioBannerText("Stage 2/5: Attacker dumps credentials. Canary alert 'AKIA_CANARY_PHANTOM_99' triggered! Decoy host marked COMPROMISED.");
      setSelectedNodeId("decoy-ssh-01");
      setNodes(prev => prev.map(n => (n.id === "decoy-ssh-01" || n.id === "Honey-Bastion-SSH") ? { ...n, status: "COMPROMISED" } : n));
      setBlastReport(prev => prev ? { ...prev, blast_radius_index: 92, threat_severity: "CRITICAL", crown_jewel_breach_imminent: true, crown_jewels_exposed: ["CrownJewel-Vault-DB"] } : null);
      setTelemetryEvents(prev => [{
        event_type: "DECEPTION_TRAP_TRIGGERED",
        summary: "Stage 2/5: Canary token AKIA_CANARY_PHANTOM_99 tripped in /var/backup/shadow.kdbx!",
        time: new Date().toLocaleTimeString(),
        mitre: { technique_id: "T1552.004", technique_name: "Unsecured Credentials", tactic: "Credential Access", severity: "CRITICAL" }
      }, ...prev]);
    }, 2000);

    // Step 3 at 4s
    setTimeout(() => {
      setCurrentScenarioStep(3);
      setScenarioBannerText("Stage 3/5: Blast Radius calculated. BRVI spiked to 92% (CRITICAL)! Imminent path to CrownJewel-Vault-DB.");
      setBlastReport({
        compromised_node: "decoy-ssh-01",
        blast_radius_index: 92,
        threat_severity: "CRITICAL",
        total_reachable_assets: 8,
        crown_jewels_exposed: ["CrownJewel-Vault-DB"],
        crown_jewel_breach_imminent: true,
        containment_recommendation: "IMMEDIATE CONTAINMENT REQUIRED: Crown Jewel Vault Database directly reachable.",
        hops: {
          1: [{ node_id: "Internal-Core-Switch", name: "Internal Core Switch", type: "switch", criticality: "High", status: "HEALTHY", hop_depth: 1 }],
          2: [{ node_id: "AD-Domain-Controller", name: "Active Directory DC", type: "server", criticality: "Critical", status: "HEALTHY", hop_depth: 2 }],
          3: [{ node_id: "CrownJewel-Vault-DB", name: "Production Secrets Vault", type: "vault", criticality: "CrownJewel", status: "HEALTHY", hop_depth: 3 }]
        }
      });
    }, 4000);

    // Step 4 at 6s
    setTimeout(() => {
      setCurrentScenarioStep(4);
      setScenarioBannerText("Stage 4/5: Betweenness Centrality executed. 'Internal-Core-Switch' flagged as critical choke point.");
      setTelemetryEvents(prev => [{
        event_type: "CENTRALITY_COMPUTED",
        summary: "Stage 4/5: Internal-Core-Switch identified as strategic choke point (CB: 0.4286).",
        time: new Date().toLocaleTimeString(),
        mitre: { technique_id: "CHOKE_POINT", technique_name: "Betweenness Centrality", tactic: "Defense Insight", severity: "HIGH" }
      }, ...prev]);
    }, 6000);

    // Step 5 at 8s
    setTimeout(() => {
      setCurrentScenarioStep(5);
      setScenarioBannerText("Stage 5/5: J.A.R.V.I.S. AI Sentinel triggered autonomous micro-segmentation! Blast radius collapsed to 0% (SECURE).");
      setSentinelInterventions(prev => prev + 1);
      setTelemetryEvents(prev => [
        {
          event_type: "SENTINEL_SAFEGUARD_TRIGGERED",
          summary: "J.A.R.V.I.S. Autonomous Safeguard engaged! Critical risk (BRVI: 92%) mitigated via dynamic graph quarantine.",
          agent_name: "J.A.R.V.I.S.",
          full_title: "Just a Rather Very Intelligent System",
          mode: sentinelMode,
          reasoning: "Blast radius index (92%) exceeded safety threshold (85.0%) and decoy canary AKIA_CANARY_PHANTOM_99 was breached. Autonomous topology quarantine enforced.",
          target_node: "decoy-ssh-01",
          time: new Date().toLocaleTimeString(),
          mitre: {
            technique_id: "AUTONOMOUS_CONTAINMENT",
            technique_name: "AI Micro-Segmentation",
            tactic: "Remediation",
            severity: "CRITICAL"
          }
        },
        ...prev
      ]);
      handleContainNode("decoy-ssh-01");
      setTimeout(() => setIsScenarioRunning(false), 2000);
    }, 8000);
  };

  // Extract blast radius node IDs for visualization highlight
  const blastNodeIds: string[] = [];
  if (blastReport?.hops) {
    Object.values(blastReport.hops).forEach((hopList) => {
      hopList.forEach((item) => blastNodeIds.push(item.node_id));
    });
  }

  return (
    <div className="min-h-screen bg-[#050811] text-slate-100 flex flex-col font-sans">
      {/* Top Cyber Command Header */}
      <header className="border-b border-slate-800 bg-[#090e1c] px-6 py-3.5 flex flex-wrap items-center justify-between gap-4 sticky top-0 z-50 backdrop-blur-md">
        {/* Brand & Track Details */}
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

        {/* Global Controls & Status */}
        <div className="flex items-center space-x-2.5">
          {/* WebSocket Live Pill */}
          <div className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-medium border ${wsConnected
            ? 'bg-emerald-950/80 border-emerald-500/50 text-emerald-300'
            : 'bg-red-950/80 border-red-500/50 text-red-300'
            }`}>
            <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-emerald-400 animate-ping' : 'bg-red-500'}`} />
            <span>{wsConnected ? "SOC Telemetry Live" : "Offline Simulation"}</span>
          </div>

          {/* J.A.R.V.I.S. AI Sentinel Mode Pill */}
          <button
            onClick={handleToggleSentinel}
            className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-medium border transition cursor-pointer ${sentinelMode === "AUTONOMOUS_PROTECTION"
              ? "bg-cyan-950/90 border-cyan-500/50 text-cyan-300 hover:border-cyan-400 shadow-md shadow-cyan-500/20"
              : "bg-amber-950/90 border-amber-500/50 text-amber-300 hover:border-amber-400 shadow-md shadow-amber-500/20"
              }`}
            title="Click to toggle J.A.R.V.I.S. operational mode between Autonomous Protection and Manual Override"
          >
            <span className={`w-2 h-2 rounded-full ${sentinelMode === "AUTONOMOUS_PROTECTION" ? "bg-cyan-400 animate-pulse" : "bg-amber-400"}`} />
            <span>{sentinelMode === "AUTONOMOUS_PROTECTION" ? "J.A.R.V.I.S. AUTO GUARD" : "J.A.R.V.I.S. MANUAL"}</span>
          </button>

          {/* Primary Judge Simulation Trigger */}
          <button
            onClick={handleRunJudgeScenario}
            disabled={isScenarioRunning}
            className="flex items-center space-x-2 px-3.5 py-1.5 bg-gradient-to-r from-red-600 via-rose-600 to-amber-600 hover:from-red-500 hover:to-amber-500 text-white rounded-lg font-bold text-xs shadow-lg shadow-red-600/30 transition disabled:opacity-50 border border-red-400/40 animate-pulse cursor-pointer"
            title="Sequentially executes end-to-end 5-step attack and micro-segmentation scenario"
          >
            <Zap className="w-3.5 h-3.5 fill-current text-amber-200" />
            <span>{isScenarioRunning ? `Simulating Stage ${currentScenarioStep}/5...` : "⚡ Run Live Judge Attack Simulation"}</span>
          </button>

          {/* Reset Infrastructure Graph */}
          <button
            onClick={handleResetGraph}
            disabled={isScenarioRunning}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium border border-slate-700 transition disabled:opacity-50 cursor-pointer"
            title="Restore all nodes to pristine HEALTHY status and re-attach network topology"
          >
            <RotateCcw className="w-3.5 h-3.5 text-cyan-400" />
            <span>🔄 Reset Infrastructure Graph</span>
          </button>

          {/* J.A.R.V.I.S. Voice Assistant Widget */}
          <JarvisVoiceAssistant wsUrl={WS_BASE} apiBase={API_BASE} />

          {/* Team Info Button */}
          <button
            onClick={() => setShowTeamModal(true)}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-cyan-950/60 hover:bg-cyan-900/80 border border-cyan-500/40 text-cyan-300 rounded-lg text-xs font-medium transition"
          >
            <Users className="w-3.5 h-3.5" />
            <span>Team & Problem</span>
          </button>
        </div>
      </header>

      {/* Scenario Progress / Stage Tracker Bar */}
      <section className="bg-[#070c18] border-b border-slate-800/80 px-6 py-2.5">
        <div className="max-w-[1920px] mx-auto flex flex-col lg:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-3 w-full lg:w-auto">
            <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-bold flex items-center space-x-1.5 shrink-0">
              <Flame className="w-3.5 h-3.5 text-amber-400" />
              <span>Judge Attack Chain:</span>
            </span>

            {/* Stage Pills */}
            <div className="grid grid-cols-5 gap-1.5 w-full lg:w-auto">
              {SCENARIO_STAGES.map((st) => {
                const isActive = currentScenarioStep === st.step;
                const isPassed = currentScenarioStep > st.step;
                return (
                  <div
                    key={st.step}
                    className={`px-2 py-1 rounded text-[11px] font-mono transition flex items-center space-x-1 border ${isActive
                      ? "bg-amber-950/90 border-amber-500 text-amber-200 font-bold shadow-lg shadow-amber-500/20 animate-pulse"
                      : isPassed
                        ? "bg-emerald-950/60 border-emerald-500/50 text-emerald-300"
                        : "bg-slate-900/80 border-slate-800 text-slate-500"
                      }`}
                  >
                    <span className="w-4 h-4 rounded-full bg-black/40 flex items-center justify-center text-[10px]">
                      {isPassed ? "✓" : st.step}
                    </span>
                    <span className="truncate hidden sm:inline">{st.title}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Current Stage Description Banner */}
          {scenarioBannerText && (
            <div className="w-full lg:w-auto bg-slate-900/90 border border-cyan-500/30 rounded px-3 py-1 text-xs font-mono text-cyan-300 flex items-center space-x-2">
              <Radio className="w-3 h-3 text-cyan-400 animate-pulse shrink-0" />
              <span className="truncate">{scenarioBannerText}</span>
            </div>
          )}
        </div>
      </section>

      {/* Main Workspace Layout */}
      <main className="flex-1 p-6 max-w-[1920px] mx-auto w-full">
        {/* View Tab Selector Bar */}
        <div className="flex items-center justify-between bg-[#090e1c] p-1.5 rounded-xl border border-slate-800 mb-5">
          <div className="flex space-x-1">
            <button
              onClick={() => setActiveTab("triple")}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center space-x-1.5 ${activeTab === "triple" ? "bg-cyan-600 text-black shadow" : "text-slate-400 hover:text-slate-200"
                }`}
            >
              <span>3-Panel Cockpit (Shell | Graph | CTI)</span>
            </button>
            <button
              onClick={() => setActiveTab("split")}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center space-x-1.5 ${activeTab === "split" ? "bg-cyan-600 text-black shadow" : "text-slate-400 hover:text-slate-200"
                }`}
            >
              <span>Dual View (Graph + Terminal)</span>
            </button>
            <button
              onClick={() => setActiveTab("graph")}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center space-x-1.5 ${activeTab === "graph" ? "bg-cyan-600 text-black shadow" : "text-slate-400 hover:text-slate-200"
                }`}
            >
              <Share2 className="w-3.5 h-3.5" />
              <span>Full Graph Visualizer</span>
            </button>
            <button
              onClick={() => setActiveTab("shell")}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center space-x-1.5 ${activeTab === "shell" ? "bg-cyan-600 text-black shadow" : "text-slate-400 hover:text-slate-200"
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

        {/* 3-Panel Cockpit View */}
        {activeTab === "triple" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 w-full">
            {/* Left Panel: ShellView */}
            <div className="lg:col-span-4 xl:col-span-3 h-[780px]">
              <ShellView onExecuteCommand={handleExecuteCommand} />
            </div>

            {/* Center Panel: GraphView */}
            <div className="lg:col-span-8 xl:col-span-5 h-[780px]">
              <GraphView
                nodes={nodes}
                edges={edges}
                selectedNodeId={selectedNodeId}
                blastRadiusNodes={blastNodeIds}
                onSelectNode={(id) => setSelectedNodeId(id)}
                onContainNode={handleContainNode}
                onRefresh={fetchGraphData}
                isSimulating={isScenarioRunning || isSimulating}
              />
            </div>

            {/* Right Panel: CTIView */}
            <div className="lg:col-span-12 xl:col-span-4 h-[780px] overflow-y-auto">
              <CTIView
                blastReport={blastReport}
                chokePoints={chokePoints}
                events={telemetryEvents}
                selectedNodeId={selectedNodeId}
                onContainNode={handleContainNode}
                isContainmentLoading={isContainmentLoading}
                sentinelMode={sentinelMode}
                onToggleSentinel={handleToggleSentinel}
                sentinelInterventions={sentinelInterventions}
                lastIntervention={lastIntervention}
              />
            </div>
          </div>
        )}

        {/* Other Layouts (Split, Full Graph, Full Shell) */}
        {activeTab !== "triple" && (
          <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 w-full">
            {/* Left & Center Panels: Graph & Terminal */}
            <div className="xl:col-span-8 flex flex-col space-y-4">
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
                    isSimulating={isScenarioRunning || isSimulating}
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
                    isSimulating={isScenarioRunning || isSimulating}
                  />
                </div>
              )}

              {activeTab === "shell" && (
                <div className="h-[800px]">
                  <ShellView onExecuteCommand={handleExecuteCommand} />
                </div>
              )}
            </div>

            {/* Right Panel: Cyber Threat Intelligence & GraphOps Blast Radius */}
            <div className="xl:col-span-4">
              <CTIView
                blastReport={blastReport}
                chokePoints={chokePoints}
                events={telemetryEvents}
                selectedNodeId={selectedNodeId}
                onContainNode={handleContainNode}
                isContainmentLoading={isContainmentLoading}
                sentinelMode={sentinelMode}
                onToggleSentinel={handleToggleSentinel}
                sentinelInterventions={sentinelInterventions}
                lastIntervention={lastIntervention}
              />
            </div>
          </div>
        )}
      </main>

      {/* Team & Hackathon Modal */}
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
