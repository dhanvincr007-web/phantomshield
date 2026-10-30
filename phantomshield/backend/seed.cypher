// ==============================================================================
// PhantomShield (GraphShield AI) — Neo4j Cypher Graph Topology Seeder
// hackFront India 2026 Hackathon | Neo4j Track - GraphOps Problem Statement
// Team: Dhanvin (Lead), Pragathish Palsamy, P.V. Krishnan, Mohamed Annas, MANO G
// ==============================================================================

MATCH (n) DETACH DELETE n;

CREATE (gw:Gateway {
    id: "Internet-Gateway",
    name: "Edge Border Gateway",
    label: "Gateway",
    type: "gateway",
    ip: "198.51.100.1",
    os: "VyOS Linux Edge",
    criticality: "Medium",
    status: "HEALTHY",
    vulnerability: "None (Hardened)",
    cve: "N/A",
    description: "Perimeter ingress router handling corporate edge traffic"
});

CREATE (dmz:Server {
    id: "DMZ-Web-Prod",
    name: "DMZ Public Web App",
    label: "Server",
    type: "server",
    ip: "10.0.1.10",
    os: "Ubuntu 22.04 LTS (NGINX)",
    criticality: "High",
    status: "COMPROMISED",
    vulnerability: "Remote Code Execution",
    cve: "CVE-2024-21413",
    description: "Initial compromised ingress vector exploited via SSRF & deserialization"
});

CREATE (api:Server {
    id: "API-Gateway-01",
    name: "Internal Microservices Gateway",
    label: "Server",
    type: "server",
    ip: "10.0.1.20",
    os: "Alpine Linux (Kong API)",
    criticality: "High",
    status: "HEALTHY",
    vulnerability: "JWT Weak Secret",
    cve: "CVE-2023-38035",
    description: "Routes inbound customer and microservice REST payloads"
});

CREATE (auth:AuthServer {
    id: "Auth-Service-OAuth",
    name: "Corporate SSO / Keycloak",
    label: "AuthServer",
    type: "server",
    ip: "10.0.2.15",
    os: "Debian 12 (Keycloak IAM)",
    criticality: "Critical",
    status: "HEALTHY",
    vulnerability: "Privilege Escalation in OIDC Plugin",
    cve: "CVE-2023-40028",
    description: "Primary identity federation provider for internal microservices"
});

CREATE (sw:Switch {
    id: "Internal-Core-Switch",
    name: "Core Layer-3 Switch (VLAN 10/20)",
    label: "Switch",
    type: "switch",
    ip: "10.0.2.1",
    os: "Cisco NX-OS",
    criticality: "Critical",
    status: "HEALTHY",
    vulnerability: "CDP Stack Overflow",
    cve: "CVE-2020-3118",
    description: "Critical bridge choke point routing traffic between DMZ and LAN"
});

CREATE (ws:Workstation {
    id: "DevOps-Workstation-04",
    name: "Lead Architect Workstation",
    label: "Workstation",
    type: "workstation",
    ip: "10.0.3.45",
    os: "Windows 11 Enterprise",
    criticality: "High",
    status: "HEALTHY",
    vulnerability: "Unquoted Service Path",
    cve: "CVE-2023-36884",
    description: "Contains cached AWS credentials and SSH jump keys"
});

CREATE (k8s:Cluster {
    id: "Production-K8s-Cluster",
    name: "Prod Kubernetes Control Plane",
    label: "Cluster",
    type: "server",
    ip: "10.0.4.10",
    os: "Ubuntu 22.04 (k8s v1.28)",
    criticality: "Critical",
    status: "HEALTHY",
    vulnerability: "API Ingress Path Traversal",
    cve: "CVE-2023-5044",
    description: "Hosts core revenue transaction processing pods"
});

CREATE (dc:DomainController {
    id: "AD-Domain-Controller",
    name: "AD Primary DC (CORP.LOCAL)",
    label: "DomainController",
    type: "domain_controller",
    ip: "10.0.0.5",
    os: "Windows Server 2022",
    criticality: "Critical",
    status: "HEALTHY",
    vulnerability: "Zerologon RPC Relay",
    cve: "CVE-2020-1472",
    description: "Kerberos Key Distribution Center and Active Directory forest root"
});

CREATE (vault:CrownJewel {
    id: "CrownJewel-Vault-DB",
    name: "Crown Jewel: Secrets & PII Vault",
    label: "CrownJewel",
    type: "database",
    ip: "10.0.0.50",
    os: "RHEL 9 (HashiCorp Vault & PG-Crypto)",
    criticality: "CrownJewel",
    status: "HEALTHY",
    vulnerability: "None (MFA Enforced)",
    cve: "N/A",
    description: "Ultimate target containing customer PII, encryption root keys, and financial ledger"
});

CREATE (backup:Storage {
    id: "Backup-DR-Storage",
    name: "Immutable Cold Backup Array",
    label: "Storage",
    type: "storage",
    ip: "10.0.5.100",
    os: "TrueNAS Enterprise ZFS",
    criticality: "High",
    status: "HEALTHY",
    vulnerability: "Outdated SSH Cipher Suite",
    cve: "N/A",
    description: "Air-gapped replica storage target"
});

CREATE (hbastion:Honeypot {
    id: "Honey-Bastion-SSH",
    name: "Decoy Jumpbox (Honey-Bastion)",
    label: "Honeypot",
    type: "honeypot",
    ip: "10.0.1.99",
    os: "Alpine Linux (AI Emulated Shell)",
    criticality: "Honeypot",
    status: "DECOY",
    vulnerability: "Default Root Credential Trap",
    cve: "T1078.001",
    description: "High-interaction deceptive SSH proxy equipped with AI prompt deception"
});

CREATE (htoken:HoneyToken {
    id: "HoneyToken-AdminKey",
    name: "HoneyToken: AWS_ROOT_ACCESS_KEY",
    label: "HoneyToken",
    type: "honeytoken",
    ip: "Virtual Decoy",
    os: "Decoy Credential",
    criticality: "Honeypot",
    status: "DECOY",
    vulnerability: "Simulated Leaked Cloud IAM Token",
    cve: "T1552.001",
    description: "Planted credential in /tmp and environment variables alerting when referenced"
});

CREATE (hcrm:Honeypot {
    id: "Honey-CRM-Database",
    name: "Decoy CRM Database (Fake Leads)",
    label: "Honeypot",
    type: "honeypot",
    ip: "10.0.2.99",
    os: "MySQL 8.0 Decoy Container",
    criticality: "Honeypot",
    status: "DECOY",
    vulnerability: "SQL Injection Trap",
    cve: "T1190",
    description: "Simulated synthetic database serving watermarked honeypot rows"
});

CREATE (canary:Canary {
    id: "Canary-File-Passwd",
    name: "Canary: /var/backup/shadow.kdbx",
    label: "Canary",
    type: "canary",
    ip: "File Artifact",
    os: "Canary Breadcrumb",
    criticality: "Honeypot",
    status: "DECOY",
    vulnerability: "Breadcrumb Trailing to Honey-CRM",
    cve: "T1083",
    description: "Planted KeePass database file alerting on read or file extraction attempts"
});

MATCH (gw:Gateway {id: "Internet-Gateway"}), (dmz:Server {id: "DMZ-Web-Prod"})
CREATE (gw)-[:ROUTES_TRAFFIC_TO {id: "e1", protocol: "HTTPS", port: 443, weight: 1.0, status: "ACTIVE"}]->(dmz);

MATCH (gw:Gateway {id: "Internet-Gateway"}), (hb:Honeypot {id: "Honey-Bastion-SSH"})
CREATE (gw)-[:ROUTES_TRAFFIC_TO {id: "e2", protocol: "SSH", port: 2222, weight: 0.5, status: "DECEPTIVE"}]->(hb);

MATCH (dmz:Server {id: "DMZ-Web-Prod"}), (api:Server {id: "API-Gateway-01"})
CREATE (dmz)-[:CONNECTS_TO {id: "e3", protocol: "mTLS", port: 8443, weight: 1.5, status: "ACTIVE"}]->(api);

MATCH (api:Server {id: "API-Gateway-01"}), (auth:AuthServer {id: "Auth-Service-OAuth"})
CREATE (api)-[:AUTHENTICATES_VIA {id: "e4", protocol: "OIDC", port: 8080, weight: 2.0, status: "ACTIVE"}]->(auth);

MATCH (dmz:Server {id: "DMZ-Web-Prod"}), (sw:Switch {id: "Internal-Core-Switch"})
CREATE (dmz)-[:CROSSES_SUBNET {id: "e5", protocol: "TCP", port: 0, weight: 3.0, status: "ACTIVE"}]->(sw);

MATCH (sw:Switch {id: "Internal-Core-Switch"}), (ws:Workstation {id: "DevOps-Workstation-04"})
CREATE (sw)-[:CONNECTS_TO {id: "e6", protocol: "RDP", port: 3389, weight: 2.5, status: "ACTIVE"}]->(ws);

MATCH (ws:Workstation {id: "DevOps-Workstation-04"}), (k8s:Cluster {id: "Production-K8s-Cluster"})
CREATE (ws)-[:ADMIN_ACCESS {id: "e7", protocol: "KUBECTL", port: 6443, weight: 3.5, status: "ACTIVE"}]->(k8s);

MATCH (dmz:Server {id: "DMZ-Web-Prod"}), (canary:Canary {id: "Canary-File-Passwd"})
CREATE (dmz)-[:CONTAINS_CANARY {id: "e8", protocol: "LOCAL_FS", port: 0, weight: 0.2, status: "DECEPTIVE"}]->(canary);

MATCH (hb:Honeypot {id: "Honey-Bastion-SSH"}), (ht:HoneyToken {id: "HoneyToken-AdminKey"})
CREATE (hb)-[:LEADS_TO_TRAP {id: "e9", protocol: "TOKEN_READ", port: 0, weight: 0.1, status: "DECEPTIVE"}]->(ht);

MATCH (canary:Canary {id: "Canary-File-Passwd"}), (crm:Honeypot {id: "Honey-CRM-Database"})
CREATE (canary)-[:REFERENCES_DECOY {id: "e10", protocol: "DB_CONN", port: 3306, weight: 0.4, status: "DECEPTIVE"}]->(crm);

MATCH (sw:Switch {id: "Internal-Core-Switch"}), (dc:DomainController {id: "AD-Domain-Controller"})
CREATE (sw)-[:LATERAL_MOVEMENT_PATH {id: "e11", protocol: "SMB/RPC", port: 445, weight: 4.0, status: "ACTIVE"}]->(dc);

MATCH (ws:Workstation {id: "DevOps-Workstation-04"}), (dc:DomainController {id: "AD-Domain-Controller"})
CREATE (ws)-[:PIVOT_EXPLOIT {id: "e12", protocol: "WINRM", port: 5985, weight: 3.8, status: "ACTIVE"}]->(dc);

MATCH (dc:DomainController {id: "AD-Domain-Controller"}), (vault:CrownJewel {id: "CrownJewel-Vault-DB"})
CREATE (dc)-[:CONTROLS_DATA {id: "e13", protocol: "LDAP_SYNC", port: 636, weight: 5.0, status: "ACTIVE"}]->(vault);

MATCH (k8s:Cluster {id: "Production-K8s-Cluster"}), (vault:CrownJewel {id: "CrownJewel-Vault-DB"})
CREATE (k8s)-[:QUERIES_SECRETS {id: "e14", protocol: "VAULT_REST", port: 8200, weight: 4.5, status: "ACTIVE"}]->(vault);

MATCH (vault:CrownJewel {id: "CrownJewel-Vault-DB"}), (backup:Storage {id: "Backup-DR-Storage"})
CREATE (vault)-[:REPLICATES_TO {id: "e15", protocol: "ZFS_SEND", port: 9000, weight: 1.2, status: "ACTIVE"}]->(backup);

