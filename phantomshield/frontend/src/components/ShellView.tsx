"use client";

import React, { useState, useRef, useEffect } from "react";
import { Terminal, Send, ShieldAlert, Sparkles, Play, Trash2 } from "lucide-react";

interface MitreInfo {
  technique_id: string;
  technique_name: string;
  tactic: string;
  severity: string;
}

interface ShellLog {
  id: string;
  command: string;
  output: string;
  mitre?: MitreInfo;
  alert?: string;
  timestamp: string;
}

interface ShellViewProps {
  onExecuteCommand: (command: string) => Promise<{
    output: string;
    mitre_technique?: MitreInfo;
    alert_details?: string;
  }>;
}

export default function ShellView({ onExecuteCommand }: ShellViewProps) {
  const [inputCmd, setInputCmd] = useState("");
  const [logs, setLogs] = useState<ShellLog[]>([
    {
      id: "init-1",
      command: "uname -a",
      output: "Linux dmz-web-prod-01 5.15.0-105-generic #115-Ubuntu SMP Mon Feb 12 18:20:41 UTC 2024 x86_64 GNU/Linux",
      mitre: {
        technique_id: "T1082",
        technique_name: "System Information Discovery",
        tactic: "Discovery",
        severity: "HIGH"
      },
      timestamp: "19:39:12"
    },
    {
      id: "init-2",
      command: "whoami",
      output: "www-data",
      mitre: {
        technique_id: "T1033",
        technique_name: "System Owner/User Discovery",
        tactic: "Reconnaissance",
        severity: "HIGH"
      },
      timestamp: "19:39:20"
    }
  ]);
  const [isExecuting, setIsExecuting] = useState(false);
  const terminalEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputCmd.trim() || isExecuting) return;

    const cmd = inputCmd.trim();
    setInputCmd("");
    setIsExecuting(true);

    const now = new Date().toLocaleTimeString();

    try {
      const res = await onExecuteCommand(cmd);
      setLogs(prev => [
        ...prev,
        {
          id: Math.random().toString(),
          command: cmd,
          output: res.output,
          mitre: res.mitre_technique,
          alert: res.alert_details,
          timestamp: now
        }
      ]);
    } catch {
      setLogs(prev => [
        ...prev,
        {
          id: Math.random().toString(),
          command: cmd,
          output: "Command execution failed. Check backend connection.",
          timestamp: now
        }
      ]);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleRunPreset = (cmd: string) => {
    setInputCmd(cmd);
  };

  const clearTerminal = () => {
    setLogs([]);
  };

  return (
    <div className="w-full h-[620px] bg-[#060a14] border border-slate-800 rounded-xl overflow-hidden shadow-2xl flex flex-col font-mono">
      <div className="flex items-center justify-between px-4 py-2.5 bg-[#0b1222] border-b border-slate-800 text-xs">
        <div className="flex items-center space-x-2">
          <div className="flex space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500/80 inline-block" />
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80 inline-block" />
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80 inline-block" />
          </div>
          <span className="ml-2 font-semibold text-slate-300 flex items-center space-x-1.5">
            <Terminal className="w-3.5 h-3.5 text-emerald-400" />
            <span>Attacker Terminal Simulator (Honeypot Deception Sandbox)</span>
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <span className="px-2 py-0.5 rounded bg-slate-800 text-cyan-400 text-[11px]">
            Target: DMZ-Web-Prod (10.0.1.10)
          </span>
          <button
            onClick={clearTerminal}
            className="p-1 hover:bg-slate-800 text-slate-400 hover:text-slate-200 rounded transition"
            title="Clear Console"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <div className="px-3 py-2 bg-[#090e1c] border-b border-slate-800/80 flex flex-wrap items-center gap-1.5 text-[11px]">
        <span className="text-slate-500 font-sans font-medium flex items-center space-x-1 mr-1">
          <Play className="w-3 h-3 text-cyan-400" />
          <span>Demo Scripts:</span>
        </span>
        <button
          onClick={() => handleRunPreset("whoami")}
          className="px-2 py-0.5 bg-slate-800/80 hover:bg-slate-700 text-cyan-300 rounded border border-slate-700/60 transition"
        >
          whoami
        </button>
        <button
          onClick={() => handleRunPreset("cat /etc/passwd")}
          className="px-2 py-0.5 bg-slate-800/80 hover:bg-slate-700 text-cyan-300 rounded border border-slate-700/60 transition"
        >
          cat /etc/passwd
        </button>
        <button
          onClick={() => handleRunPreset("cat /var/backup/shadow.kdbx")}
          className="px-2 py-0.5 bg-amber-950/60 hover:bg-amber-900 border border-amber-500/40 text-amber-300 rounded transition flex items-center space-x-1"
        >
          <Sparkles className="w-2.5 h-2.5" />
          <span>Trip Canary (shadow.kdbx)</span>
        </button>
        <button
          onClick={() => handleRunPreset("ssh root@10.0.1.99")}
          className="px-2 py-0.5 bg-amber-950/60 hover:bg-amber-900 border border-amber-500/40 text-amber-300 rounded transition"
        >
          ssh Honey-Bastion
        </button>
        <button
          onClick={() => handleRunPreset("curl -s http://10.0.0.50:8200")}
          className="px-2 py-0.5 bg-red-950/60 hover:bg-red-900 border border-red-500/40 text-red-300 rounded transition"
        >
          Probe Vault DB
        </button>
      </div>

      <div className="flex-1 p-4 overflow-y-auto space-y-4 text-xs leading-relaxed terminal-scanlines">
        {logs.map((log) => (
          <div key={log.id} className="space-y-1.5">
            <div className="flex flex-wrap items-center justify-between text-slate-400 border-b border-slate-800/40 pb-1">
              <div className="flex items-center space-x-2">
                <span className="text-emerald-400 font-bold">www-data@dmz-web-prod:~$</span>
                <span className="text-slate-100 font-semibold">{log.command}</span>
              </div>
              <div className="flex items-center space-x-2 text-[10px]">
                {log.mitre && (
                  <span className={`px-1.5 py-0.5 rounded font-mono font-semibold ${
                    log.mitre.severity === 'CRITICAL' ? 'bg-red-950 text-red-400 border border-red-600' :
                    log.mitre.severity === 'HIGH' ? 'bg-amber-950 text-amber-300 border border-amber-600' :
                    'bg-cyan-950 text-cyan-300 border border-cyan-700'
                  }`}>
                    {log.mitre.technique_id} • {log.mitre.technique_name}
                  </span>
                )}
                <span className="text-slate-500">{log.timestamp}</span>
              </div>
            </div>

            {log.alert && (
              <div className="p-2 bg-red-950/80 border border-red-600/60 rounded text-red-300 text-[11px] flex items-start space-x-2 animate-pulse">
                <ShieldAlert className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
                <div>
                  <span className="font-bold text-red-200">DECEPTION TRIPWIRE ALERT:</span> {log.alert}
                </div>
              </div>
            )}

            <pre className="text-slate-300 whitespace-pre-wrap font-mono pl-2 text-[11.5px] border-l-2 border-slate-700/60">
              {log.output}
            </pre>
          </div>
        ))}
        <div ref={terminalEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-3 bg-[#0a0f1d] border-t border-slate-800 flex items-center space-x-2">
        <span className="text-emerald-400 font-bold text-xs select-none">www-data@dmz-web-prod:~$</span>
        <input
          type="text"
          value={inputCmd}
          onChange={(e) => setInputCmd(e.target.value)}
          placeholder="Type bash command (e.g. whoami, cat /etc/passwd, nmap 10.0.2.1)..."
          className="flex-1 bg-transparent text-slate-100 placeholder-slate-600 focus:outline-none text-xs font-mono"
          disabled={isExecuting}
          autoFocus
        />
        <button
          type="submit"
          disabled={isExecuting || !inputCmd.trim()}
          className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-black font-semibold rounded text-xs flex items-center space-x-1 transition shadow"
        >
          <span>Send</span>
          <Send className="w-3 h-3" />
        </button>
      </form>
    </div>
  );
}

