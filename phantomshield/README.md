# 🛡️ PhantomShield (GraphShield AI)

> **GraphOps Engine for Autonomous Threat Hunting, AI Deception, J.A.R.V.I.S. Sentinel Safeguards, and Real-Time Blast Radius Containment**  
> *Developed for **hackFront India 2026 (Edition 01)** — an initiative of Where U Elevate*  
> *Track: **Cybersecurity Track → Neo4j Track (GraphOps)***  
> *Problem Statement: **GraphOps: Graph analytics for proactive threat hunting and blast radius containment in security operations centers***  
> *GitHub Repository: **[https://github.com/dhanvincr007-web/PhantomShield.git](https://github.com/dhanvincr007-web/PhantomShield.git)***

---

## 👥 Team Metadata & Roster

| Name | Role | Email |
| :--- | :--- | :--- |
| **Dhanvin** | **Team Lead & Full-Stack Architect** | `dhanvincr007@gmail.com` |
| **Pragathish Palsamy** | **Core Engineer** | `pragathishpalsamy@gmail.com` |
| **P.V. Krishnan** | **Core Engineer** | `pvkrishnan38@gmail.com` |
| **Mohamed Annas** | **Core Engineer** | `mohamedannas023@gmail.com` |
| **MANO G** | **Core Engineer** | `rr0839880@gmail.com` |

---

## 🤖 J.A.R.V.I.S. Autonomous AI Sentinel

PhantomShield features an embedded autonomous GraphOps Sentinel: **J.A.R.V.I.S.** (**J**ust **A** **R**ather **V**ery **I**ntelligent **S**ystem).

```
   [ Attacker Action / Telemetry ]
                 │
                 ▼
   [ J.A.R.V.I.S. Telemetry Inspector ]
                 │
   ┌─────────────┴─────────────┐
   ▼                           ▼
[ Canary Tripwire? ]   [ BRVI > 85.0%? ]
(AKIA_CANARY_PHANTOM_99) (Crown Jewel Threatened)
   │                           │
   └─────────────┬─────────────┘
                 │ (Breach Detected)
                 ▼
   [ Mode == AUTONOMOUS_PROTECTION? ]
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
    [ YES ]             [ NO (MANUAL_OVERRIDE) ]
       │                   │
       ▼                   ▼
[ Sever Egress Paths ]  [ Log Critical Alert ]
[ Collapse BRVI: 0%  ]  [ Await Operator Action ]
[ Broadcast Telepathy]  [ Broadcast Telepathy ]
```

### Key Capabilities:
- **Continuous Telemetry Inspector:** Intercepts real-time command execution, canary token touches, and graph mutations.
- **Dynamic Safeguard Triggers:**
  - **Blast Radius Vulnerability Index (BRVI) > 85.0%**: Immediately initiates topological micro-segmentation before Crown Jewel compromise.
  - **Canary Breach Detection**: Trips immediately when decoy files (`/var/backup/shadow.kdbx`) or canary keys (`AKIA_CANARY_PHANTOM_99`) are touched.
- **Operational Modes:**
  - `AUTONOMOUS_PROTECTION` *(Default)*: Automatically severs egress network edges and quarantines compromised assets, collapsing blast radius from 92% to **0.0% (SECURE)**.
  - `MANUAL_OVERRIDE`: Switches to passive logging and telemetry streaming, requiring operator confirmation before edge modification.
- **Full-Duplex WebSocket Telepathy:** Emits structured decision payloads (`SENTINEL_SAFEGUARD_TRIGGERED`, `SENTINEL_MODE_CHANGED`, `NODE_STATUS_CHANGED`, `EDGE_SEVERED`) for instant SOC visual updates.

---

## 💡 The Problem & The GraphOps Vision

Modern Security Operations Centers (SOCs) are overwhelmed with 10,000+ alerts daily from disparate sensors. Traditional relational and document databases store these events as flat logs, rendering analysts **blind to multi-hop lateral movement** and unable to calculate an incident's true blast radius.

**PhantomShield** introduces **GraphOps** to cybersecurity:
1. **Neo4j Connected Knowledge Graph**: Telemetry, identity permissions, network routes, and vulnerabilities are unified into a high-speed, queryable graph.
2. **AI Deception Tripwires**: Dynamic honeypots, canary files, and breadcrumb honeytokens are strategically planted across network paths.
3. **GraphOps Blast Radius Engine**: When an asset is breached or probed, Neo4j calculates 1–3 hop blast radius exposure, pinpointing threatened Crown Jewels in milliseconds.
4. **Betweenness Centrality Choke Point Detection**: Automatically discovers graph pivots ($C_B(v)$) and bottlenecks, enabling targeted honeypot placement to catch 80%+ of lateral movement attempts.
5. **Zero-Downtime In-Memory Fallback Engine**: If Neo4j is offline or inaccessible, the system automatically activates a high-fidelity In-Memory Graph (15 nodes, 18 relationships), ensuring zero downtime during judging or live demos.
6. **Autonomous Micro-Segmentation**: With one click (or autonomous J.A.R.V.I.S. trigger), severs active attack paths in the graph to collapse the blast radius down to 0%.

---

## 🚀 Live Judge Attack Simulation Engine (1-Click Automated Demo)

PhantomShield includes a built-in automated attack scenario runner executing the complete end-to-end cyber chain over real-time WebSockets:

| Step | Time | Phase | Command / Action | MITRE Tag / Canary | GraphOps & Sentinel Outcome |
|:---:|:---:|:---|:---|:---|:---|
| **1** | **0s** | **Reconnaissance** | `whoami && uname -a` | `TA0007: System Information Discovery` | Decoy host probed; baseline telemetry broadcast |
| **2** | **2s** | **Credential Dumping** | `cat /var/backup/shadow.kdbx` | Canary: `AKIA_CANARY_PHANTOM_99` | Decoy node `decoy-ssh-01` marked `COMPROMISED` |
| **3** | **4s** | **Blast Radius Calculation** | `get_blast_radius("decoy-ssh-01", 3)` | Multi-hop Graph Traversal | **BRVI: 92% (CRITICAL)**; `CrownJewel-Vault-DB` exposed |
| **4** | **6s** | **Choke Point Identification** | `get_choke_points()` | Betweenness Centrality $C_B(v)$ | Flags `Internal-Core-Switch` as critical bridge node |
| **5** | **8s** | **J.A.R.V.I.S. Intervention** | `contain_threat("decoy-ssh-01")` | Dynamic Micro-Segmentation | Egress severed; **BRVI collapses to 0% (SECURE)** |

### Demo Controls on Frontend
- **"⚡ Run Live Judge Attack Simulation"**: Triggers `POST /api/simulation/run-scenario` and streams live stage countdown, graph highlights, and MITRE logs.
- **"🔄 Reset Infrastructure Graph"**: Calls `POST /api/graph/reset` to restore all nodes to pristine `HEALTHY` status.
- **"J.A.R.V.I.S. AUTO GUARD / MANUAL"**: Toggles between Autonomous Protection and Manual Override with glowing visual telemetry.

---

## 📐 Architecture Overview

```
+-----------------------------------------------------------------------------------+
|                            PhantomShield SOC Command Center                       |
|                          (Next.js 14 + Tailwind CSS + Cytoscape + Lucide)         |
+-----------------------------------------+-----------------------------------------+
                                          |
                      REST API & WebSocket /ws/telemetry
                                          |
+-----------------------------------------v-----------------------------------------+
|                               FastAPI GraphOps Engine                             |
+-------------------+---------------------+--------------------+--------------------+
|   main.py         |   database.py       |   ai_sentinel.py   |   graph_ops.py     |
| - REST Endpoints  | - Neo4j AuraDB / Bolt| - J.A.R.V.I.S. Guard| - Blast Radius     |
| - WebSocket Hub   | - Cypher Seeder     | - Policy Engine    | - Betweenness      |
| - Judge Scenario  | - In-Memory Fallback| - Threshold Trigger| - Micro-segment    |
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
PhantomShield/
├── .gitignore                # Root Git ignore policy (Node, Next, Python, envs)
├── README.md                 # Complete project documentation & setup
├── docker-compose.yml        # Turnkey orchestration for Neo4j, Backend, Frontend
├── start_all.bat             # Turnkey Windows 1-click execution launcher
├── DEPLOYMENT.md             # Free-tier cloud deployment guide (AuraDB, Render, Vercel)
├── phantomshield_pitch_deck.md # 10-slide presentation pitch deck
├── backend/                  # FastAPI + Neo4j Graph Engine + AI Sentinel
│   ├── main.py               # API Endpoints, WebSockets & Scenario Runner
│   ├── database.py           # Neo4j Driver Connection + In-Memory Fallback Graph
│   ├── ai_sentinel.py        # J.A.R.V.I.S. Autonomous AI Sentinel Engine
│   ├── graph_ops.py          # Blast Radius, Betweenness Centrality & Containment
│   ├── llm_sandbox.py        # AI Deception Proxy & Honeypot Shell Simulator
│   ├── verify_submission.py  # Local Test & Automated Submission Readiness Suite
│   ├── test_engine.py        # Comprehensive test suite
│   ├── requirements.txt      # Python dependencies
│   ├── Procfile              # PaaS process file (Render / Railway)
│   ├── runtime.txt           # Python 3.11 runtime specification
│   ├── render.yaml           # Render 1-click blueprint specification
│   ├── railway.json          # Railway deployment configuration
│   ├── Dockerfile            # Container build for backend
│   └── .env.example          # Environment variable template
├── frontend/                 # Next.js 14 SOC Operator Command Center
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx      # Main SOC Dashboard with Judge Controls & Timeline
│   │   │   ├── layout.tsx    # Cyber theme root layout
│   │   │   └── globals.css   # Dark cyber theme & CRT terminal styling
│   │   └── components/
│   │       ├── GraphView.tsx # Cytoscape.js & SVG Force Topology Visualizer
│   │       ├── ShellView.tsx # Monospace Attacker Terminal Simulator
│   │       └── CTIView.tsx   # MITRE ATT&CK, BRVI Radar & J.A.R.V.I.S. Controls
│   ├── package.json          # Dependencies & scripts
│   ├── tailwind.config.js    # Cyber palette config
│   ├── tsconfig.json         # TypeScript configuration
│   ├── vercel.json           # Vercel deployment configuration
│   ├── Dockerfile            # Container build for frontend
│   └── .env.example          # Frontend environment variable template
└── phantomshield/            # Synced production mirror
```

---

## ⚡ Quick Start & Deployment

### Option 1: Turnkey Windows Launcher (`start_all.bat`)
Double-click `start_all.bat` or run from PowerShell:
```cmd
start_all.bat
```
- Automatically detects Docker and runs `docker-compose up -d`.
- If Docker is not installed, automatically starts FastAPI backend and Next.js frontend natively in separate console windows!

---

### Option 2: Docker Compose (All-in-One Turnkey)
Run the full stack with Neo4j Community (APOC enabled), FastAPI backend, and Next.js frontend:
```bash
docker-compose up --build
```
- **SOC Command Dashboard:** [http://localhost:3000](http://localhost:3000)
- **FastAPI Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Neo4j Browser:** [http://localhost:7474](http://localhost:7474)  
  *Default Credentials:* User: `neo4j` | Password: `phantomshield2026`

---

### Option 3: Running Locally Without Docker (Zero-Downtime In-Memory Fallback)

#### 1. Backend (FastAPI + Graph Engine + J.A.R.V.I.S.)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
> **Zero-Downtime Guarantee:** If a local Neo4j instance is not running on port 7687, the backend automatically activates its built-in **High-Fidelity In-Memory Graph Engine** (15 nodes, 18 relationships), so all GraphOps features, blast radius calculations, J.A.R.V.I.S. safeguards, and AI deception sandboxes run flawlessly out of the box!

#### 2. Frontend (Next.js SOC Command Center)
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🧪 Submission Verification Suite

PhantomShield includes an automated pre-submission testing suite validating all 8 core deliverables, graph algorithms, and J.A.R.V.I.S. safeguards:

```bash
# Run local verification suite
python backend/verify_submission.py

# Optional: Run live integration tests against a running server
python backend/verify_submission.py --live --url http://localhost:8000
```

### Verification Checks:
```text
------------------------------------------------------------------------
TEST / DELIVERABLE               | STATUS   | DETAILS
------------------------------------------------------------------------
Graph Topology Seeding           | [PASS]   | 15 nodes, 18 edges (In-Memory Graph Engine)
Blast Radius (decoy-ssh-01)      | [PASS]   | BRVI 92% (CRITICAL), Exposed Crown Jewels
Centrality & Choke Points        | [PASS]   | Top node identified. Choke points: Internal-Core-Switch
AI Deception & Canary Trap       | [PASS]   | AKIA_CANARY_PHANTOM_99 tripped — MITRE T1552.004
Autonomous Containment           | [PASS]   | Risk: 92% -> 0% (SECURE). Severed edges: 2
J.A.R.V.I.S. AI Sentinel         | [PASS]   | Autonomous Guard (85% BRVI threshold) & Manual Override
Pitch Deck (10 Slides)           | [PASS]   | 10 slides found with all required hackathon metadata
Submission ZIP Archive           | [PASS]   | Clean archive without node_modules / .venv
------------------------------------------------------------------------
>>> SUBMISSION PACKAGE VERIFIED & READY FOR HACKFRONT INDIA 2026! <<<
```

---

## 🚀 Pushing to GitHub

To push the clean repository to GitHub:

```bash
# 1. Verify git status (clean build, no node_modules or .venv)
git status

# 2. Add all tracked files
git add .

# 3. Commit with hackathon submission message
git commit -m "feat: complete PhantomShield GraphOps AI deception engine with J.A.R.V.I.S. safeguards"

# 4. Set remote origin (if not already configured)
git remote set-url origin https://github.com/dhanvincr007-web/PhantomShield.git

# 5. Push to main branch
git branch -M main
git push -u origin main
```

---

## 🏆 Innovation & Hackathon Impact
- **Zero-Trust Graph Automation:** Replaces slow manual SIEM correlation with sub-second graph traversal algorithms.
- **Proactive AI Deception:** Uses honeypots and tripwires to trick attackers into revealing their TTPs before reaching Crown Jewels.
- **Deterministic Containment:** J.A.R.V.I.S. micro-segments infected nodes at topological choke points without disrupting benign network traffic.
