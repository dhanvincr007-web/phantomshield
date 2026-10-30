# 🛡️ PhantomShield (GraphShield AI)
> **GraphOps Engine for Autonomous Threat Hunting, AI Deception, and Real-Time Blast Radius Containment**  
> *Developed for **hackFront India 2026 (Edition 01)** | Track: **Cybersecurity Track -> Neo4j Track***  
> *Problem Statement: **GraphOps: Graph analytics for proactive threat hunting and blast radius containment in security operations centers***

---

## 👥 Team Metadata
- **Team Lead:** Dhanvin (`dhanvincr007@gmail.com`)
- **Team Member:** Pragathish Palsamy (`pragathishpalsamy@gmail.com`)
- **Team Member:** P.V. Krishnan (`pvkrishnan38@gmail.com`)
- **Team Member:** Mohamed Annas (`mohamedannas023@gmail.com`)
- **Team Member:** MANO G (`rr0839880@gmail.com`)

---

## 💡 The Problem & The GraphOps Vision
Modern Security Operations Centers (SOCs) are inundated with over 10,000+ alerts daily from disparate sensors. Traditional relational and document databases store these events as flat logs, rendering analysts **blind to multi-hop lateral movement** and unable to calculate an incident's true blast radius.

**PhantomShield** introduces **GraphOps** to cybersecurity:
1. **Neo4j Connected Knowledge Graph**: Telemetry, identity permissions, network routes, and vulnerabilities are unified into a high-speed, queryable graph.
2. **AI Deception Tripwires**: Dynamic honeypots, canary files, and breadcrumb honeytokens are strategically planted across network paths.
3. **GraphOps Blast Radius Engine**: When an asset is breached or probed, Neo4j calculates 1–3 hop blast radius exposure, pinpointing threatened Crown Jewels in milliseconds.
4. **Betweenness Centrality Choke Point Detection**: Automatically discovers graph pivots ($C_B(v)$) and bottlenecks, enabling targeted honeypot placement to catch 80%+ of lateral movement attempts.
5. **Autonomous Micro-Segmentation**: With one click (or autonomous trigger), severs active attack paths in the graph to collapse the blast radius down to 0%.

---

## 📐 Architecture Overview

```
+-----------------------------------------------------------------------------------+
|                            PhantomShield SOC Command Center                       |
|                          (Next.js 14 + Tailwind CSS + Lucide)                     |
+-----------------------------------------+-----------------------------------------+
                                          |
                      REST API & WebSocket /ws/telemetry
                                          |
+-----------------------------------------v-----------------------------------------+
|                               FastAPI GraphOps Engine                             |
+-------------------+---------------------+--------------------+--------------------+
|   main.py         |   database.py       |   graph_ops.py     |   llm_sandbox.py   |
| - REST Endpoints  | - Neo4j Driver      | - Blast Radius     | - Deception Proxy  |
| - WebSocket Hub   | - Cypher Seeder     | - Betweenness      | - Honeypot Shell   |
| - Attack Pipeline | - In-Memory Fallback| - Micro-segment    | - MITRE ATT&CK     |
+-------------------+---------------------+--------------------+--------------------+
                                          |
                                Bolt Protocol / Port 7687
                                          |
+-----------------------------------------v-----------------------------------------+
|                             Neo4j Graph Database 5.x                              |
|   (Network Topology, Lateral Movement Edges, HoneyTokens, Crown Jewel Targets)     |
+-----------------------------------------------------------------------------------+
```

---

## 📂 Project Structure

```text
phantomshield/
├── backend/                  # FastAPI + Neo4j Graph Engine + Deception Proxy
│   ├── main.py               # API Endpoints & WebSocket Telemetry Server
│   ├── database.py           # Neo4j Driver Connection & Cypher Seed Scripts
│   ├── llm_sandbox.py        # AI Deception Proxy & Shell Emulation
│   ├── graph_ops.py          # Blast Radius & Betweenness Centrality Algorithms
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile            # Container build for backend
├── frontend/                 # Next.js Operator Command Center
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx      # Main SOC Operator Dashboard
│   │   │   ├── layout.tsx    # Cyber theme root layout
│   │   │   └── globals.css   # Dark cyber theme & terminal scanlines
│   │   └── components/
│   │       ├── GraphView.tsx # Interactive GraphOps Visualizer
│   │       ├── ShellView.tsx # Live Attacker Terminal Simulator
│   │       └── CTIView.tsx   # MITRE ATT&CK & Blast Radius Metrics
│   ├── package.json          # Dependencies & scripts
│   ├── tailwind.config.js    # Cyber palette config
│   ├── tsconfig.json         # TypeScript configuration
│   └── Dockerfile            # Container build for frontend
└── docker-compose.yml        # Orchestrates Neo4j, Backend, and Frontend
```

---

## ⚡ Quick Start & Deployment

### Option 1: Docker Compose (All-in-One Turnkey)
Run the full stack (Neo4j Community with APOC, FastAPI backend, Next.js frontend):
```bash
docker-compose up --build
```
- **SOC Dashboard:** [http://localhost:3000](http://localhost:3000)
- **FastAPI Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Neo4j Browser:** [http://localhost:7474](http://localhost:7474) (User: `neo4j`, Password: `phantomshield2026`)

---

### Option 2: Running Locally Without Docker

#### 1. Backend (FastAPI + Graph Engine)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
*(Note: If Neo4j is not running locally, the backend seamlessly switches to its built-in **High-Fidelity In-Memory Graph Engine**, so all GraphOps features, blast radius calculations, and AI deception sandboxes run out of the box!)*

#### 2. Frontend (Next.js Command Center)
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🧪 Interactive Hackathon Demo Script (Judge Walkthrough)

1. **Inspect GraphOps Topology**:
   - Navigate to the **Full Graph Visualizer** tab.
   - Click on `DMZ-Web-Prod` (compromised web server) to inspect its CVEs and see the multi-hop perimeter.
   - Notice the golden decoys: `Honey-Bastion-SSH`, `Canary-File-Passwd`, and `HoneyToken-AdminKey`.

2. **Trigger the Attacker Deception Terminal**:
   - In the **Attacker Terminal**, execute:
     ```bash
     cat /var/backup/shadow.kdbx
     ```
   - Watch the AI deception proxy return simulated decoy credentials while the MITRE technique tag `T1552.004` appears.
   - Look at the top alert: the Canary file trips, instantly alerting the SOC over WebSockets!

3. **Check Blast Radius & Crown Jewel Risk**:
   - On the right panel, observe the **Blast Radius Vulnerability Index (BRVI)** rise to **85–92 (CRITICAL)**.
   - The engine flags reachable assets across 1, 2, and 3 hops and alerts: *Imminent attack path to Crown Jewel Vault DB*.

4. **Surface Choke Points via Betweenness Centrality**:
   - View the **Strategic Choke Points** leaderboard.
   - `Internal-Core-Switch` and `DevOps-Workstation-04` are detected as the highest betweenness bottlenecks ($C_B(v) > 0.12$).

5. **Execute Autonomous Containment**:
   - Click **"Trigger Autonomous Micro-Segmentation"**.
   - Watch the active edges sever in real time on the graph visualizer, and the Blast Radius risk score collapses from **92 -> 0**!

---

## 🏆 Innovation & Hackathon Impact
- **Zero-Trust Graph Automation:** Replaces slow manual SIEM correlation with graph algorithms.
- **Proactive AI Deception:** Uses honeypots and tripwires to trick attackers into revealing their TTPs before reaching Crown Jewels.
- **Deterministic Containment:** Micro-segments infected nodes at topological choke points without disrupting benign network traffic.
