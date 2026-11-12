# 🛡️ PhantomShield (GraphShield AI)
## Hackathon Pitch Deck & Technical Briefing
### hackFront India 2026 (Edition 01) — Neo4j Track / GraphOps Problem Statement

---

## 📑 Slide 1: Title & Team Metadata

### **PhantomShield (GraphShield AI)**
> **Autonomous GraphOps Engine for Real-Time Threat Hunting, AI Deception, J.A.R.V.I.S. Safeguards & Blast Radius Containment**

- **Hackathon:** hackFront India 2026 (Edition 01)
- **Category & Track:** Cybersecurity Track $\rightarrow$ **Neo4j Track**
- **Problem Statement:** *GraphOps: Graph analytics for proactive threat hunting and blast radius containment in security operations centers*
- **AI Sentinel:** **J.A.R.V.I.S.** (*Just a Rather Very Intelligent System*)
- **Live Code Repository:** `https://github.com/dhanvincr007-web/PhantomShield.git`

### 👥 Engineering Team
| Role | Name | Email |
|:---|:---|:---|
| **Team Lead & Full-Stack Architect** | **Dhanvin** | `dhanvincr007@gmail.com` |
| **Graph Algorithm Engineer** | **Pragathish Palsamy** | `pragathishpalsamy@gmail.com` |
| **Cybersecurity & Deception Lead** | **P.V. Krishnan** | `pvkrishnan38@gmail.com` |
| **Backend & Distributed Systems** | **Mohamed Annas** | `mohamedannas023@gmail.com` |
| **UI/UX & Frontend Engineer** | **MANO G** | `rr0839880@gmail.com` |

---

## 📑 Slide 2: The Core SOC Problem

### The Crisis in Modern Security Operations
- **Alert Fatigue & Data Silos:** Enterprise SOCs process **10,000+ alerts daily** across disjointed log tables, firewalls, and EDR solutions.
- **Relational DB Bottlenecks:** Traditional relational and document databases fail at recursive graph traversals. Tracing a 3-hop lateral movement path requires complex multi-table self-joins that degrade query response times from milliseconds to minutes.
- **Blast Radius Blindness:** SOC analysts lack real-time visibility into an incident's true blast radius. When an edge machine is breached, identifying reachable Crown Jewels takes hours of manual correlation.
- **Delayed Containment (Mean Time To Contain > 200 Days):** Perimeter-focused defense fails once an adversary achieves initial execution, leaving multi-hop lateral movement undetected.

---

## 📑 Slide 3: PhantomShield Solution & Architecture

### The GraphOps Paradigm Shift
PhantomShield converts passive security telemetry into an active, interconnected cyber knowledge graph using **Neo4j**, coupled with dynamic **AI Deception** and automated **GraphOps containment**:

```text
+-----------------------------------------------------------------------------------+
|                        PhantomShield SOC Command Center                           |
|                      (Next.js 14 + Tailwind CSS + Cytoscape.js)                   |
+-----------------------------------------+-----------------------------------------+
                                          |
                      REST API & WebSocket /ws/telemetry
                                          |
+-----------------------------------------v-----------------------------------------+
|                               FastAPI GraphOps Engine                             |
+-------------------+---------------------+--------------------+--------------------+
|   main.py         |   database.py       |   ai_sentinel.py   |   graph_ops.py     |
| - REST Endpoints  | - Neo4j AuraDB Bolt | - J.A.R.V.I.S. Guard| - Blast Radius     |
| - WebSocket Hub   | - Cypher Seeder     | - Auto-Containment | - Betweenness      |
| - Judge Scenario  | - In-Memory Fallback| - Mode Toggling    | - Micro-segment    |
+-------------------+---------------------+--------------------+--------------------+
                                          |
                                 Bolt Protocol / Port 7687
                                          |
+-----------------------------------------v-----------------------------------------+
|                        Neo4j Enterprise / AuraDB Graph Database                   |
|   (Network Topology, Lateral Movement Edges, HoneyTokens, Crown Jewel Targets)     |
+-----------------------------------------------------------------------------------+
```

1. **Connected Knowledge Graph:** Maps network hosts, authentication sessions, and cloud permissions into graph nodes and edges.
2. **AI Deception Tripwires:** Intercepts reconnaissance with low-friction, high-interaction honeypots and synthetic canary files.
3. **GraphOps Engine:** Calculates 1–3 hop blast radius exposure, pinpoints choke points, and micro-segments compromised paths in under 10 seconds.

---

## 📑 Slide 4: Graph Model Specification $G = (V, E)$

PhantomShield models the enterprise security posture as an attributed, directed property graph $G = (V, E)$:

### 1. Vertices / Nodes ($V$)
| Node Category | Primary Labels | Example Identifiers | Properties |
|:---|:---|:---|:---|
| **Perimeter** | `Gateway`, `Server` | `Internet-Gateway`, `DMZ-Web-Prod` | `ip`, `os`, `cve`, `criticality: High` |
| **Core Infrastructure** | `Switch`, `Workstation` | `Internal-Core-Switch`, `DevOps-Workstation-04` | `betweenness_score`, `status: HEALTHY` |
| **Crown Jewels** | `Database`, `Vault` | `CrownJewel-Vault-DB`, `AD-Domain-Controller` | `criticality: MissionCritical`, `tier: 0` |
| **AI Deception Traps** | `Honeypot`, `Canary`, `HoneyToken` | `decoy-ssh-01`, `Canary-File-Passwd`, `HoneyToken-AdminKey` | `is_decoy: true`, `canary_id` |

### 2. Edges / Relationships ($E$)
- `ROUTES_TRAFFIC_TO`: Ingress/egress routing with protocol and port attributes.
- `CONNECTS_TO`: Direct network adjacency and firewall allow rules.
- `PIVOT_EXPLOIT`: Identified multi-hop lateral movement trajectory.
- `AUTHENTICATES_VIA` / `ADMIN_ACCESS`: Identity privilege delegation and Kerberos/WinRM paths.
- `CONTAINS_CANARY` / `LEADS_TO_TRAP`: Deceptive breadcrumb edges designed to lure attackers away from production databases.

---

## 📑 Slide 5: Graph Analytics & Algorithmic Innovation

### 1. Multi-Hop Blast Radius & Vulnerability Index (BRVI)
When node $v_0$ is breached, the engine computes reachable asset sets $R_k(v_0)$ for hops $k \in \{1, 2, 3\}$ via Breadth-First Search (BFS) graph traversal:
$$R_k(v_0) = \{ u \in V \mid d(v_0, u) \le k \}$$

The **Blast Radius Vulnerability Index (BRVI)** combines hop distance, asset criticality weights ($w_u$), and Crown Jewel exposure:
$$\text{BRVI}(v_0) = \min\left(100, \; \sum_{u \in R_3(v_0)} \frac{w_u \cdot \text{CriticalityMultiplier}(u)}{\text{distance}(v_0, u)}\right)$$

### 2. Betweenness Centrality Choke Point Detection
Identifies structural choke points using Brandes' Betweenness Centrality algorithm:
$$C_B(v) = \sum_{s \neq v \neq t \in V} \frac{\sigma_{st}(v)}{\sigma_{st}}$$
Where $\sigma_{st}$ is the total number of shortest attack paths from node $s$ to Crown Jewel $t$, and $\sigma_{st}(v)$ is the number of paths passing through $v$.
- **Outcome:** Nodes with $C_B(v) > 0.15$ (e.g., `Internal-Core-Switch`) are automatically classified as **Strategic Choke Points**, allowing operators to position decoys or pre-stage firewall rules.

---

## 📑 Slide 6: AI Deception & MITRE ATT&CK Mapping

### High-Interaction Emulated Shell & Honeypots
- **Interactive Bash Shell:** Adversaries interact with a simulated environment (`whoami`, `uname -a`, `ls -la /var/backup`, `cat shadow.kdbx`).
- **Canary Breadcrumbs:** Returns synthetic AWS keys (`AKIA_CANARY_PHANTOM_99`) and seeded KeePass databases.
- **Automated MITRE ATT&CK Classification:**
  - `TA0007: Discovery` $\rightarrow$ `whoami`, `uname -a` (System Information Discovery)
  - `TA0006: Credential Access` $\rightarrow$ `T1552.004` (Unsecured Credentials in Private Keys/Vaults)
  - `TA0008: Lateral Movement` $\rightarrow$ `T1021.004` (Remote Services: SSH / WinRM)
- **Zero False-Positive Guarantee:** Production users never access canary tokens or honeypot ports. Any interaction with decoy assets represents 100% true-positive malicious intent.

---

## 📑 Slide 7: Next.js Command Center Features

### SOC Operator Experience (Next.js 14 + Tailwind + Lucide + Cytoscape.js)
1. **Dual GraphOps Visualizer:**
   - **Force-Directed Physics View:** Interactive SVG physics with draggable nodes, zoom/pan, pulsing blast rings, and glowing attack vectors.
   - **Cytoscape.js Engine:** CoSE (Compound Spring Embedder) graph layout for high-density enterprise networks.
2. **Live Attacker Terminal:** Emulates a CRT monitor connected to the decoy bastion via WebSockets.
3. **Cyber Threat Intelligence (CTI) Feed:**
   - Real-time BRVI gauge ($0\text{--}100\%$).
   - Multi-hop breakdown ($k=1, 2, 3$).
   - Ranked Strategic Choke Points leaderboard.
   - Live MITRE ATT&CK telemetry feed.
4. **1-Click Judge Scenario Bar:** Visual countdown and stage highlighter for live evaluations.

---

## 📑 Slide 8: 5-Step Demo Walkthrough

The platform includes a 1-click automated simulation (`POST /api/simulation/run-scenario`) demonstrating autonomous containment in 8 seconds:

| Step | Time | Phase | Command / Action | MITRE Tag / Canary | GraphOps Outcome |
|:---:|:---:|:---|:---|:---|:---|
| **1** | **0s** | **Reconnaissance** | `whoami && uname -a` | `TA0007: System Info Discovery` | Baseline telemetry captured; decoy shell active |
| **2** | **2s** | **Credential Dumping** | `cat /var/backup/shadow.kdbx` | Canary: `AKIA_CANARY_PHANTOM_99` | Decoy `decoy-ssh-01` marked **COMPROMISED** |
| **3** | **4s** | **Blast Radius Calculation** | `get_blast_radius("decoy-ssh-01", 3)` | Multi-hop Graph Traversal | **BRVI: 92% (CRITICAL)**; `CrownJewel-Vault-DB` exposed |
| **4** | **6s** | **Choke Point Analysis** | `get_choke_points()` | Betweenness Centrality $C_B(v)$ | Flags `Internal-Core-Switch` ($C_B = 0.4286$) as bridge |
| **5** | **8s** | **J.A.R.V.I.S. Intervention** | `contain_threat("decoy-ssh-01")` | Dynamic Edge Quarantine | J.A.R.V.I.S. auto-severs egress; **BRVI collapses to 0% (SECURE)** |

---

## 📑 Slide 9: Impact & Commercial Feasibility

### Enterprise Value Proposition
- **99.9% Reduction in MTTC:** Slashes Mean Time To Contain from industry average of **200+ hours to under 10 seconds** via autonomous topological micro-segmentation.
- **Zero False-Positive Alerting:** Canary tokens and deception tripwires provide deterministic alerts, freeing SOC analysts from chasing alert noise.
- **Cost Efficiency:** Deployed on standard commodity infrastructure or free-tier cloud (Neo4j AuraDB Free + Render + Vercel).
- **Extensible Integration:** REST API & WebSockets integrate seamlessly with enterprise SIEM/SOAR platforms (Splunk, Microsoft Sentinel, Cortex XSOAR).

---

## 📑 Slide 10: Conclusion & Submission Links

### **PhantomShield (GraphShield AI)**
*Defending Enterprise Networks with Graph Intelligence and Autonomous AI Deception*

- **Hackathon:** hackFront India 2026 (Edition 01)
- **Track:** Cybersecurity Track $\rightarrow$ Neo4j Track
- **Problem Statement:** GraphOps: Graph analytics for proactive threat hunting and blast radius containment in SOCs
- **GitHub Repository:** [github.com/dhanvincr007-web/phantomshield](https://github.com/dhanvincr007-web/phantomshield)
- **Submission Package:** `phantomshield_source_code.zip` (Ready & Validated)
- **Core Technology Stack:**
  - Graph Engine: Neo4j 5.x & Neo4j AuraDB (Cypher & APOC)
  - Backend: FastAPI, NetworkX, Uvicorn, Python 3.11
  - Frontend: Next.js 14, React 18, Tailwind CSS, Cytoscape.js, Lucide-React
  - Deployment: Docker Compose, Render PaaS, Vercel Edge

**Thank You to the hackFront India 2026 Organizing Committee and Neo4j Track Judges!**

