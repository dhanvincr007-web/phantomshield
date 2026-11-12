# ☁️ PhantomShield (GraphShield AI) — Free-Tier Cloud Deployment Guide

> **hackFront India 2026 Hackathon | Track: Cybersecurity -> Neo4j Track**  
> **Problem Statement: GraphOps: Graph analytics for proactive threat hunting and blast radius containment in SOCs**  
> **Team:** Dhanvin (Lead), Pragathish Palsamy, P.V. Krishnan, Mohamed Annas, MANO G

---

This guide details how to deploy **PhantomShield** across 100% free-tier cloud infrastructure:
- **Graph Database:** [Neo4j AuraDB Free](https://neo4j.com/cloud/platform/aura-graph-database/)
- **GraphOps Engine (FastAPI):** [Render](https://render.com) or [Railway](https://railway.app)
- **SOC Operator Console (Next.js):** [Vercel](https://vercel.com)

```text
+------------------------+          HTTPS & WSS          +----------------------------+
|   Vercel (Frontend)    | <---------------------------> |  Render/Railway (Backend)  |
|  Next.js 14 SOC Portal |                               |  FastAPI GraphOps Engine   |
+------------------------+                               +--------------+-------------+
                                                                        |
                                                          Bolt TLS (neo4j+s://)
                                                                        |
                                                         +--------------v-------------+
                                                         |     Neo4j AuraDB Free      |
                                                         |  Cloud Cyber Graph Engine  |
                                                         +----------------------------+
```

---

## 🟢 Part 1: Provision Free-Tier Neo4j AuraDB

1. Navigate to the **[Neo4j Aura Console](https://console.neo4j.io/)** and sign in (or create a free account).
2. Click **"New Instance"** and select **"AuraDB Free"** (Free forever, 1 instance, 200k nodes & 400k relationships).
3. Name your instance (e.g., `phantomshield-graph`).
4. **Important:** Download or copy your auto-generated credentials:
   - **URI:** `neo4j+s://<instance-id>.databases.neo4j.io`
   - **Username:** `neo4j`
   - **Password:** `<your-saved-password>`
5. Wait ~60 seconds for the instance status to transition to **Running**.
6. *(Optional)* Click **"Query"** or **"Open"** to verify connection, or let PhantomShield auto-seed the database upon initial boot!

---

## 🟣 Part 2: Deploy Backend to Render (or Railway)

### Option A: Render (Recommended)
1. Fork or push this repository to your GitHub account.
2. Sign in to **[Render Dashboard](https://dashboard.render.com/)**.
3. Click **"New +"** → **"Web Service"** and connect your GitHub repository.
4. Configure the service settings:
   - **Name:** `phantomshield-backend`
   - **Root Directory:** `backend` (or leave empty if deploying standalone)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free`
5. Under **Environment Variables**, add:
   | Key | Value | Description |
   |:---|:---|:---|
   | `NEO4J_URI` | `neo4j+s://<instance-id>.databases.neo4j.io` | Your AuraDB connection URI |
   | `NEO4J_USER` | `neo4j` | Default AuraDB username |
   | `NEO4J_PASSWORD` | `<your-auradb-password>` | Your AuraDB password |
   | `NEO4J_DATABASE` | `neo4j` | Default AuraDB database |
   | `PYTHON_VERSION` | `3.11.8` | Python runtime version |
   | `GEMINI_API_KEY` | *(Optional)* | Google Gemini key for shell deception |
6. Click **"Create Web Service"**.
7. Once deployed, test the health check endpoint:  
   `https://<your-render-app>.onrender.com/api/health`

---

### Option B: Railway
1. Sign in to **[Railway Dashboard](https://railway.app/)**.
2. Click **"New Project"** → **"Deploy from GitHub repo"**.
3. Select your repository.
4. In **Settings**:
   - Set **Root Directory** to `/backend`.
   - The included [`backend/railway.json`](file:///c:/Users/user/Downloads/Phantomsheild/backend/railway.json) and [`backend/Procfile`](file:///c:/Users/user/Downloads/Phantomsheild/backend/Procfile) configure the Nixpacks builder and port binding automatically.
5. In **Variables**, add:
   - `NEO4J_URI`
   - `NEO4J_USER`
   - `NEO4J_PASSWORD`
6. Click **"Generate Domain"** under Networking to get your public backend URL.

---

## ⚡ Part 3: Deploy Frontend to Vercel

1. Sign in to **[Vercel](https://vercel.com/)**.
2. Click **"Add New..."** → **"Project"** and import your repository.
3. Configure the Project:
   - **Framework Preset:** `Next.js`
   - **Root Directory:** Click edit and select `frontend`.
4. In **Environment Variables**, add:
   | Key | Value |
   |:---|:---|
   | `NEXT_PUBLIC_API_URL` | `https://<your-backend-app>.onrender.com` |
5. Click **"Deploy"**.
6. Vercel will build the Next.js application in under 60 seconds.

---

## 🛡️ Zero-Downtime Resilience Guarantee

If Neo4j AuraDB credentials are not supplied or if AuraDB is paused:
- The FastAPI backend **automatically detects** unreachable remote connections.
- It immediately engages the built-in **High-Fidelity In-Memory Graph Engine**.
- All blast radius calculations ($1–3\text{ hops}$), Betweenness Centrality choke point detections ($C_B(v)$), interactive bash honeypots, and autonomous micro-segmentations continue running smoothly with **zero crashes or 500 errors**.

---

## 🧪 Post-Deployment Judge Verification Protocol

1. **Verify Backend Health:**
   ```bash
   curl -s https://<your-backend-url>/api/health
   ```
   *Expected Response:*
   ```json
   {
     "status": "healthy",
     "neo4j": {
       "status": "connected",
       "mode": "neo4j_auradb",
       "tls_encrypted": true
     }
   }
   ```

2. **Trigger the 1-Click Judge Scenario:**
   - Open your Vercel deployment URL (`https://<your-app>.vercel.app`).
   - Click **"🚀 Run Live Judge Attack Simulation"**.
   - Observe real-time WebSocket stage progression (Reconnaissance → Canary Credential Dumping → BRVI 92% Spike → Internal-Core-Switch Choke Point → Micro-Segmentation 0% SECURE).

