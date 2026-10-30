"use client";

import React, { useState, useEffect, useRef } from "react";
import { 
  ShieldAlert, 
  Server, 
  Lock, 
  Sparkles, 
  Database, 
  Key, 
  RefreshCw, 
  Zap, 
  Eye, 
  Radio, 
  Cpu, 
  Activity,
  Maximize2,
  ZoomIn,
  ZoomOut
} from "lucide-react";

export interface GraphNode {
  id: string;
  name: string;
  label: string;
  type: string;
  ip: string;
  os: string;
  criticality: string;
  status: "HEALTHY" | "COMPROMISED" | "ISOLATED" | "DECOY" | "ALERTED" | "DECOY_TRIGGERED";
  vulnerability?: string;
  cve?: string;
  description?: string;
  x?: number;
  y?: number;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relationship: string;
  protocol: string;
  port: number;
  weight: number;
  status: "ACTIVE" | "QUARANTINED" | "DECEPTIVE";
}

interface GraphViewProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedNodeId: string | null;
  blastRadiusNodes: string[];
  onSelectNode: (nodeId: string) => void;
  onContainNode: (nodeId: string) => void;
  onRefresh: () => void;
  isSimulating: boolean;
}

// Initial deterministic 2D layout coordinates for consistent, clean layout
const DEFAULT_NODE_POSITIONS: Record<string, { x: number; y: number }> = {
  "Internet-Gateway": { x: 100, y: 260 },
  "DMZ-Web-Prod": { x: 280, y: 170 },
  "Honey-Bastion-SSH": { x: 280, y: 390 },
  "API-Gateway-01": { x: 460, y: 120 },
  "Canary-File-Passwd": { x: 420, y: 280 },
  "HoneyToken-AdminKey": { x: 460, y: 440 },
  "Auth-Service-OAuth": { x: 640, y: 90 },
  "Internal-Core-Switch": { x: 580, y: 230 },
  "Honey-CRM-Database": { x: 620, y: 360 },
  "DevOps-Workstation-04": { x: 740, y: 170 },
  "Production-K8s-Cluster": { x: 920, y: 120 },
  "AD-Domain-Controller": { x: 800, y: 310 },
  "CrownJewel-Vault-DB": { x: 970, y: 250 },
  "Backup-DR-Storage": { x: 1100, y: 360 },
};

export default function GraphView({
  nodes,
  edges,
  selectedNodeId,
  blastRadiusNodes,
  onSelectNode,
  onContainNode,
  onRefresh,
  isSimulating
}: GraphViewProps) {
  const [positions, setPositions] = useState<Record<string, { x: number; y: number }>>(DEFAULT_NODE_POSITIONS);
  const [draggingNode, setDraggingNode] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(0.85);
  const [pan, setPan] = useState({ x: 20, y: 30 });
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });
  const svgRef = useRef<SVGSVGElement | null>(null);

  // Auto-align coordinates on mount or when nodes change
  useEffect(() => {
    setPositions(prev => {
      const updated = { ...prev };
      nodes.forEach((node, idx) => {
        if (!updated[node.id]) {
          const col = Math.floor(idx / 3);
          const row = idx % 3;
          updated[node.id] = { x: 200 + col * 180, y: 120 + row * 140 };
        }
      });
      return updated;
    });
  }, [nodes]);

  const handleMouseDownNode = (e: React.MouseEvent, nodeId: string) => {
    e.stopPropagation();
    setDraggingNode(nodeId);
    const pos = positions[nodeId] || { x: 0, y: 0 };
    setDragOffset({
      x: e.clientX / zoom - pos.x,
      y: e.clientY / zoom - pos.y
    });
    onSelectNode(nodeId);
  };

  const handleMouseDownSvg = (e: React.MouseEvent) => {
    if (e.target === svgRef.current || (e.target as HTMLElement).tagName === "svg") {
      setIsPanning(true);
      setPanStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (draggingNode) {
      const newX = e.clientX / zoom - dragOffset.x;
      const newY = e.clientY / zoom - dragOffset.y;
      setPositions(prev => ({
        ...prev,
        [draggingNode]: { x: Math.max(50, Math.min(1300, newX)), y: Math.max(50, Math.min(700, newY)) }
      }));
    } else if (isPanning) {
      setPan({
        x: e.clientX - panStart.x,
        y: e.clientY - panStart.y
      });
    }
  };

  const handleMouseUp = () => {
    setDraggingNode(null);
    setIsPanning(false);
  };

  const selectedNode = nodes.find(n => n.id === selectedNodeId);

  // Helper for node styling
  const getNodeColor = (node: GraphNode) => {
    if (node.status === "ISOLATED") return "#64748b"; // Gray
    if (node.status === "COMPROMISED") return "#ef4444"; // Pulsing Red
    if (node.status === "DECOY_TRIGGERED" || node.status === "ALERTED") return "#f97316"; // Bright Orange
    if (node.criticality === "Honeypot" || node.status === "DECOY") return "#f59e0b"; // Gold / Amber
    if (node.criticality === "CrownJewel") return "#a855f7"; // Neon Purple
    if (node.criticality === "Critical") return "#e11d48"; // Rose
    if (node.label === "Gateway") return "#06b6d4"; // Cyan
    return "#3b82f6"; // Blue
  };

  const getNodeIcon = (node: GraphNode) => {
    if (node.status === "ISOLATED") return <Lock className="w-4 h-4 text-slate-300" />;
    if (node.status === "COMPROMISED") return <ShieldAlert className="w-4 h-4 text-red-200 animate-pulse" />;
    if (node.criticality === "CrownJewel") return <Database className="w-4 h-4 text-purple-200" />;
    if (node.criticality === "Honeypot" || node.type === "canary" || node.type === "honeytoken") {
      return <Sparkles className="w-4 h-4 text-amber-300 animate-spin" style={{ animationDuration: '6s' }} />;
    }
    if (node.type === "workstation") return <Cpu className="w-4 h-4 text-cyan-200" />;
    return <Server className="w-4 h-4 text-blue-200" />;
  };

  return (
    <div className="relative w-full h-[620px] bg-[#070b16] border border-slate-800 rounded-xl overflow-hidden shadow-2xl flex flex-col">
      {/* Visualizer Top Toolbar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-[#0b1120] border-b border-slate-800/80 z-10 text-xs">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Radio className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
            <span className="font-semibold text-slate-200 tracking-wide uppercase">
              Neo4j Real-Time GraphOps Topology
            </span>
          </div>
          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
            {nodes.length} Nodes • {edges.length} Relationships
          </span>
          {isSimulating && (
            <span className="flex items-center space-x-1.5 px-2 py-0.5 rounded bg-red-950/80 border border-red-500/50 text-red-400 font-mono animate-pulse">
              <Activity className="w-3 h-3" />
              <span>Simulated Attack Active</span>
            </span>
          )}
        </div>

        {/* View Controls */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setZoom(z => Math.min(1.4, z + 0.1))}
            className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 transition"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setZoom(z => Math.max(0.4, z - 0.1))}
            className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 transition"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => { setZoom(0.85); setPan({ x: 20, y: 30 }); }}
            className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 transition"
            title="Reset Pan & Zoom"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={onRefresh}
            className="flex items-center space-x-1 px-2.5 py-1.5 bg-cyan-950/60 hover:bg-cyan-900 border border-cyan-500/40 text-cyan-300 rounded transition font-medium"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Sync Neo4j</span>
          </button>
        </div>
      </div>

      {/* SVG Canvas */}
      <div 
        className="flex-1 relative cursor-grab active:cursor-grabbing select-none overflow-hidden"
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      >
        <svg
          ref={svgRef}
          className="w-full h-full"
          onMouseDown={handleMouseDownSvg}
        >
          <defs>
            {/* Arrow Marker Definitions */}
            <marker
              id="arrow-active"
              viewBox="0 0 10 10"
              refX="22"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#00f3ff" />
            </marker>
            <marker
              id="arrow-deceptive"
              viewBox="0 0 10 10"
              refX="22"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#f59e0b" />
            </marker>
            <marker
              id="arrow-quarantined"
              viewBox="0 0 10 10"
              refX="22"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
            </marker>
            <marker
              id="arrow-compromised"
              viewBox="0 0 10 10"
              refX="22"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef4444" />
            </marker>

            {/* Glowing filter */}
            <filter id="neon-glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Grid Background Pattern */}
          <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
            <pattern id="graph-grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#131c31" strokeWidth="0.8" />
            </pattern>
            <rect x="-1000" y="-1000" width="4000" height="4000" fill="url(#graph-grid)" />

            {/* Blast Radius Zone Highlights */}
            {blastRadiusNodes.length > 0 && selectedNodeId && positions[selectedNodeId] && (
              <g>
                <circle
                  cx={positions[selectedNodeId].x}
                  cy={positions[selectedNodeId].y}
                  r="190"
                  fill="rgba(239, 68, 68, 0.05)"
                  stroke="rgba(239, 68, 68, 0.3)"
                  strokeWidth="1.5"
                  strokeDasharray="6 4"
                  className="animate-pulse"
                />
                <circle
                  cx={positions[selectedNodeId].x}
                  cy={positions[selectedNodeId].y}
                  r="340"
                  fill="rgba(239, 68, 68, 0.02)"
                  stroke="rgba(239, 68, 68, 0.15)"
                  strokeWidth="1"
                  strokeDasharray="8 6"
                />
              </g>
            )}

            {/* Edges */}
            {edges.map(edge => {
              const srcPos = positions[edge.source];
              const tgtPos = positions[edge.target];
              if (!srcPos || !tgtPos) return null;

              const isQuarantined = edge.status === "QUARANTINED";
              const isDeceptive = edge.status === "DECEPTIVE";
              const isBlastEdge = blastRadiusNodes.includes(edge.source) && blastRadiusNodes.includes(edge.target);
              
              let strokeColor = "#00f3ff80";
              let marker = "url(#arrow-active)";
              let dash = "none";

              if (isQuarantined) {
                strokeColor = "#475569";
                marker = "url(#arrow-quarantined)";
                dash = "4 4";
              } else if (isDeceptive) {
                strokeColor = "#f59e0b";
                marker = "url(#arrow-deceptive)";
                dash = "3 3";
              } else if (isBlastEdge) {
                strokeColor = "#ef4444";
                marker = "url(#arrow-compromised)";
              }

              const midX = (srcPos.x + tgtPos.x) / 2;
              const midY = (srcPos.y + tgtPos.y) / 2;

              return (
                <g key={edge.id} className="transition-all duration-300">
                  <line
                    x1={srcPos.x}
                    y1={srcPos.y}
                    x2={tgtPos.x}
                    y2={tgtPos.y}
                    stroke={strokeColor}
                    strokeWidth={isBlastEdge ? 2.5 : (isDeceptive ? 1.8 : 1.5)}
                    strokeDasharray={dash}
                    markerEnd={marker}
                  />
                  {/* Relationship Label Pill */}
                  <rect
                    x={midX - 28}
                    y={midY - 9}
                    width="56"
                    height="18"
                    rx="4"
                    fill="#080e1c"
                    stroke={strokeColor}
                    strokeWidth="0.8"
                    opacity="0.9"
                  />
                  <text
                    x={midX}
                    y={midY + 3.5}
                    textAnchor="middle"
                    fill={isQuarantined ? "#94a3b8" : (isDeceptive ? "#fbbf24" : "#a5f3fc")}
                    fontSize="9"
                    fontFamily="monospace"
                    className="select-none pointer-events-none"
                  >
                    {edge.protocol || edge.relationship}
                  </text>
                </g>
              );
            })}

            {/* Nodes */}
            {nodes.map(node => {
              const pos = positions[node.id] || { x: 200, y: 200 };
              const isSelected = node.id === selectedNodeId;
              const isInBlastRadius = blastRadiusNodes.includes(node.id);
              const nodeColor = getNodeColor(node);
              const isHoneypot = node.criticality === "Honeypot" || node.status === "DECOY";

              return (
                <g
                  key={node.id}
                  transform={`translate(${pos.x}, ${pos.y})`}
                  className="cursor-pointer transition-transform duration-150"
                  onMouseDown={(e) => handleMouseDownNode(e, node.id)}
                >
                  {/* Selected / Compromised Glow Ring */}
                  {(isSelected || node.status === "COMPROMISED" || isInBlastRadius) && (
                    <circle
                      r="32"
                      fill="none"
                      stroke={node.status === "COMPROMISED" ? "#ef4444" : (isSelected ? "#00f3ff" : "#f97316")}
                      strokeWidth={isSelected ? "3" : "2"}
                      strokeDasharray={node.status === "COMPROMISED" ? "4 3" : "none"}
                      className={node.status === "COMPROMISED" ? "animate-pulse" : ""}
                    />
                  )}

                  {/* Honeypot Golden Pulsing Aura */}
                  {isHoneypot && (
                    <circle
                      r="28"
                      fill="none"
                      stroke="#f59e0b"
                      strokeWidth="1.5"
                      strokeDasharray="2 2"
                      opacity="0.6"
                      className="animate-spin"
                      style={{ animationDuration: '8s' }}
                    />
                  )}

                  {/* Main Node Background Card / Circle */}
                  <circle
                    r="22"
                    fill="#0d1424"
                    stroke={nodeColor}
                    strokeWidth="2.5"
                    filter="url(#neon-glow)"
                  />

                  {/* Node Center Icon */}
                  <foreignObject x="-12" y="-12" width="24" height="24" className="pointer-events-none">
                    <div className="w-full h-full flex items-center justify-center">
                      {getNodeIcon(node)}
                    </div>
                  </foreignObject>

                  {/* Status Indicator Pill below node */}
                  <rect
                    x="-45"
                    y="27"
                    width="90"
                    height="18"
                    rx="4"
                    fill="#080e1c"
                    stroke={nodeColor}
                    strokeWidth="1"
                  />
                  <text
                    x="0"
                    y="40"
                    textAnchor="middle"
                    fill="#e2e8f0"
                    fontSize="9.5"
                    fontWeight="600"
                    fontFamily="monospace"
                    className="select-none pointer-events-none"
                  >
                    {node.name.length > 14 ? node.name.substring(0, 13) + '…' : node.name}
                  </text>

                  {/* Node IP Sub-tag */}
                  <text
                    x="0"
                    y="55"
                    textAnchor="middle"
                    fill="#64748b"
                    fontSize="8.5"
                    fontFamily="monospace"
                    className="select-none pointer-events-none"
                  >
                    {node.ip}
                  </text>
                </g>
              );
            })}
          </g>
        </svg>

        {/* Selected Node Inspector Drawer / Popover */}
        {selectedNode && (
          <div className="absolute bottom-4 right-4 w-84 bg-[#0d1322]/95 border border-cyan-500/40 rounded-lg p-3.5 shadow-2xl backdrop-blur-md z-20 text-xs">
            <div className="flex items-center justify-between border-b border-slate-700/80 pb-2 mb-2.5">
              <div className="flex items-center space-x-2">
                <span 
                  className="w-2.5 h-2.5 rounded-full" 
                  style={{ backgroundColor: getNodeColor(selectedNode) }}
                />
                <span className="font-bold text-slate-100">{selectedNode.name}</span>
              </div>
              <span className={`px-1.5 py-0.5 rounded font-mono text-[10px] uppercase font-semibold ${
                selectedNode.status === 'COMPROMISED' ? 'bg-red-950 text-red-400 border border-red-700' :
                selectedNode.status === 'ISOLATED' ? 'bg-slate-800 text-slate-300' :
                selectedNode.status === 'DECOY' ? 'bg-amber-950 text-amber-300 border border-amber-600' :
                'bg-emerald-950 text-emerald-300 border border-emerald-700'
              }`}>
                {selectedNode.status}
              </span>
            </div>

            <div className="space-y-1.5 font-mono text-slate-300 text-[11px]">
              <div className="flex justify-between">
                <span className="text-slate-500">ID:</span>
                <span className="text-slate-200">{selectedNode.id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Type / OS:</span>
                <span className="text-slate-200">{selectedNode.type} / {selectedNode.os}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">IP Address:</span>
                <span className="text-cyan-400">{selectedNode.ip}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Criticality:</span>
                <span className="text-purple-300 font-semibold">{selectedNode.criticality}</span>
              </div>
              {selectedNode.cve && (
                <div className="flex justify-between">
                  <span className="text-slate-500">Vulnerability:</span>
                  <span className="text-red-400">{selectedNode.cve}</span>
                </div>
              )}
            </div>

            <p className="mt-2 text-[10.5px] text-slate-400 italic border-t border-slate-800/80 pt-2">
              {selectedNode.description || "Active asset modeled in Neo4j Knowledge Graph."}
            </p>

            {/* Micro-segmentation / Containment Quick Action */}
            <div className="mt-3 flex space-x-2">
              {selectedNode.status !== "ISOLATED" ? (
                <button
                  onClick={() => onContainNode(selectedNode.id)}
                  className="flex-1 flex items-center justify-center space-x-1 px-2.5 py-1.5 bg-red-600/90 hover:bg-red-500 text-white rounded font-medium shadow-md transition"
                >
                  <Lock className="w-3.5 h-3.5" />
                  <span>Quarantine Asset</span>
                </button>
              ) : (
                <div className="flex-1 py-1 text-center font-mono text-slate-400 bg-slate-800/80 rounded border border-slate-700">
                  Asset Quarantined
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Visualizer Footer Legend */}
      <div className="px-4 py-2 bg-[#090e1c] border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 shadow-[0_0_8px_#00f3ff]" />
            <span>Perimeter / Network</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 shadow-[0_0_8px_#ef4444]" />
            <span>Compromised Ingress</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 shadow-[0_0_8px_#f59e0b]" />
            <span>AI Deception Honeypot</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-500 shadow-[0_0_8px_#a855f7]" />
            <span>Crown Jewel DB</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-slate-500" />
            <span>Isolated Asset</span>
          </div>
        </div>

        <span className="text-slate-500 font-mono">
          Interactive Drag & Zoom • Click node for GraphOps actions
        </span>
      </div>
    </div>
  );
}

