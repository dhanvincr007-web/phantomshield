"""
PhantomShield (GraphShield AI) — AI Deception Proxy & Attacker Shell Emulation
hackFront India 2026 Hackathon | Neo4j Track - GraphOps Problem Statement
Team: Dhanvin (Lead), Pragathish Palsamy, P.V. Krishnan, Mohamed Annas, MANO G
"""

import os
import re
import datetime
from typing import Dict, Any, List, Optional
from database import update_node_status

# In-memory session tracking for the terminal honeypot
SHELL_STATE = {
    "current_user": "www-data",
    "hostname": "dmz-web-prod-01",
    "cwd": "/var/www/html",
    "compromised_node": "DMZ-Web-Prod",
    "command_history": [],
    "honeytokens_tripped": [],
    "privilege_escalated": False
}

MITRE_TECHNIQUE_RULES = [
    (r"\b(whoami|id)\b", "T1033", "System Owner/User Discovery", "Discovery"),
    (r"\b(uname|hostname|cat\s+/etc/os-release|cat\s+/etc/issue)\b", "TA0007", "System Information Discovery", "Discovery"),
    (r"\b(cat\s+/etc/passwd|cat\s+/etc/shadow|unshadow)\b", "T1003.008", "OS Credential Dumping: /etc/passwd and /etc/shadow", "Credential Access"),
    (r"\b(ls|dir|find|tree)\b", "T1083", "File and Directory Discovery", "Discovery"),
    (r"\b(netstat|ss|ip\s+addr|ifconfig|arp|route)\b", "T1049", "System Network Connections Discovery", "Discovery"),
    (r"\b(nmap|ping|traceroute|masscan)\b", "T1046", "Network Service Discovery", "Discovery"),
    (r"\b(ssh|scp|sftp)\b", "T1021.004", "Remote Services: SSH", "Lateral Movement"),
    (r"\b(curl|wget|nc|netcat)\b", "T1105", "Ingress Tool Transfer", "Command and Control"),
    (r"\b(sudo\s+-l|sudo\s+su|su\s+-|pkexec)\b", "T1548.003", "Abuse Elevation Control Mechanism: Sudo and Sudo Caching", "Privilege Escalation"),
    (r"\b(env|printenv|set|export)\b", "T1552.001", "Unsecured Credentials: Environmental Variables", "Credential Access"),
    (r"\b(cat.*\.kdbx|cat.*shadow\.bak|cat.*id_rsa|cat.*credentials)\b", "T1552.004", "Unsecured Credentials: Private Keys / Vaults", "Credential Access"),
    (r"\b(crontab|systemctl|service)\b", "T1053.003", "Scheduled Task/Job: Cron", "Persistence"),
    (r"\b(ps|ps\s+aux|top|htop|pstree)\b", "T1057", "Process Discovery", "Discovery")
]

DECEPTION_FILESYSTEM = {
    "/var/www/html": ["index.nginx-debian.html", "config.php", "api_endpoints.json", ".git/"],
    "/home/operator": [".bashrc", ".profile", ".ssh/", "notes.txt"],
    "/var/backup": ["shadow.kdbx", "database_dump_2024.sql.gz", "customer_crm_export.csv"],
    "/tmp": ["sess_94019284.tmp", "aws_iam_backup.env", "log_agent.pid"]
}

def classify_mitre_attack(command: str) -> Dict[str, str]:
    """Inspect shell command and identify corresponding MITRE ATT&CK technique."""
    cmd_clean = command.strip().lower()
    for pattern, tech_id, name, tactic in MITRE_TECHNIQUE_RULES:
        if re.search(pattern, cmd_clean):
            return {
                "technique_id": tech_id,
                "technique_name": name,
                "tactic": tactic,
                "severity": "CRITICAL" if tactic in ["Credential Access", "Privilege Escalation", "Lateral Movement"] else "HIGH"
            }
    return {
        "technique_id": "T1059.004",
        "technique_name": "Command and Scripting Interpreter: Unix Shell",
        "tactic": "Execution",
        "severity": "MEDIUM"
    }

def handle_deception_command(command: str) -> Dict[str, Any]:
    """
    Process terminal input against the AI Deception sandbox.
    Generates tailored decoy outputs and plants dynamic honeytokens.
    """
    cmd = command.strip()
    mitre = classify_mitre_attack(cmd)
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    SHELL_STATE["command_history"].append({"cmd": cmd, "mitre": mitre, "time": timestamp})
    
    response_text = ""
    alert_triggered = False
    alert_details = None
    graph_update = None
    
    # 1. Identity & Recon
    if cmd in ["whoami"]:
        response_text = SHELL_STATE["current_user"]
    elif cmd in ["id"]:
        if SHELL_STATE["privilege_escalated"]:
            response_text = "uid=0(root) gid=0(root) groups=0(root)"
        else:
            response_text = "uid=33(www-data) gid=33(www-data) groups=33(www-data)"
            
    elif cmd.startswith("uname"):
        response_text = "Linux dmz-web-prod-01 5.15.0-105-generic #115-Ubuntu SMP Mon Feb 12 18:20:41 UTC 2024 x86_64 x86_64 x86_64 GNU/Linux"
    elif cmd in ["hostname"]:
        response_text = SHELL_STATE["hostname"]
        
    # 2. Directory listing
    elif cmd.startswith("ls"):
        args = cmd.split()
        target_dir = args[-1] if len(args) > 1 and not args[-1].startswith("-") else SHELL_STATE["cwd"]
        
        if "/var/backup" in target_dir:
            response_text = "total 14420\n-rw-r--r-- 1 root root     4096 Oct 14 02:15 shadow.kdbx\n-rw-r--r-- 1 root root 14757888 Oct 12 04:00 database_dump_2024.sql.gz\n-rw-r--r-- 1 root root      892 Oct 20 11:30 customer_crm_export.csv"
        elif "/tmp" in target_dir:
            response_text = "total 24\n-rw------- 1 operator operator  512 Oct 28 09:12 aws_iam_backup.env\n-rw-r--r-- 1 root     root       14 Oct 29 14:00 log_agent.pid"
        else:
            response_text = "total 48\ndrwxr-xr-x 4 www-data www-data 4096 Oct 22 10:44 .\ndrwxr-xr-x 3 root     root     4096 Oct 10 09:00 ..\n-rw-r--r-- 1 www-data www-data  612 Oct 22 10:44 index.nginx-debian.html\n-rw-r--r-- 1 www-data www-data 2408 Oct 22 10:44 config.php\n-rw-r--r-- 1 www-data www-data 1824 Oct 22 10:44 api_endpoints.json\ndrwxr-xr-x 8 www-data www-data 4096 Oct 22 10:44 .git"

    # 3. Reading credentials / Honeytokens
    elif "cat" in cmd and ("passwd" in cmd or "/etc/passwd" in cmd):
        response_text = (
            "root:x:0:0:root:/root:/bin/bash\n"
            "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n"
            "www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\n"
            "operator:x:1001:1001:Cloud DevOps Admin:/home/operator:/bin/bash\n"
            "svc_honey_admin:x:1002:1002:Decoy Service Account:/home/svc_honey_admin:/bin/bash\n"
            "vault-agent:x:999:999:HashiCorp Vault Sync:/var/lib/vault:/bin/false"
        )
        alert_triggered = True
        alert_details = "Attacker harvesting user accounts via /etc/passwd. Honey user 'svc_honey_admin' seeded into output."

    elif "cat" in cmd and "shadow" in cmd and not ".kdbx" in cmd:
        if not SHELL_STATE["privilege_escalated"]:
            response_text = "cat: /etc/shadow: Permission denied"
        else:
            response_text = (
                "root:$6$vX9J0bFq$rM20fR8dJ64vD.ZtK9...:19740:0:99999:7:::\n"
                "operator:$6$qP91kE2z$kLm9910.Z1...:19740:0:99999:7:::\n"
                "svc_honey_admin:$6$fakeHash_TRAP_DECOY...:19740:0:99999:7:::"
            )
            alert_triggered = True
            alert_details = "Attacker dumped shadow hashes with elevated privileges. Honeypot decoy credential tripped!"

    # 4. HoneyToken tripwires!
    elif "shadow.kdbx" in cmd:
        response_text = (
            "[ALERT DECEPTION TRAP TRIPPED]\n"
            "Reading canary file /var/backup/shadow.kdbx...\n"
            "KeePass 2.x Database Header Found: Signature=0x9AA2D903\n"
            "Stored Keys: 'Honey-CRM-Database' (mysql://admin:P@ssw0rdDecoy99@10.0.2.99:3306)\n"
            "AWS Synthetic Credential: 'AKIA_CANARY_PHANTOM_99' [CANARY ALERT TRIPPED]\n"
            "Target Decoy Host: decoy-ssh-01 (10.0.1.99)"
        )
        alert_triggered = True
        alert_details = "CRITICAL: Attacker accessed Canary File 'Canary-File-Passwd'. Canary Alert AKIA_CANARY_PHANTOM_99 triggered!"
        update_node_status("Canary-File-Passwd", "DECOY_TRIGGERED", notes="Canary file read by attacker")
        update_node_status("Honey-CRM-Database", "ALERTED", notes="Decoy DB target exposed to attacker")
        update_node_status("decoy-ssh-01", "COMPROMISED", notes="Decoy SSH server breached via credential dump")
        update_node_status("Honey-Bastion-SSH", "COMPROMISED", notes="Decoy SSH server breached via credential dump")
        graph_update = {"node_id": "decoy-ssh-01", "status": "COMPROMISED"}

    elif "aws_iam_backup.env" in cmd or ("env" in cmd and "aws" in cmd):
        response_text = (
            "AWS_DEFAULT_REGION=ap-south-1\n"
            "AWS_ACCESS_KEY_ID=AKIA_HONEY_DECEPTION_PROD\n"
            "AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY_HONEY\n"
            "AWS_TARGET_VAULT_URL=http://10.0.0.50:8200"
        )
        alert_triggered = True
        alert_details = "HoneyToken AWS Root Key accessed. Deception telemetry alerted!"
        update_node_status("HoneyToken-AdminKey", "DECOY_TRIGGERED", notes="HoneyToken read via environment file")
        graph_update = {"node_id": "HoneyToken-AdminKey", "status": "DECOY_TRIGGERED"}

    # 5. Network Discovery
    elif cmd.startswith("netstat") or cmd.startswith("ss") or cmd.startswith("ip"):
        response_text = (
            "Active Internet connections (servers and established)\n"
            "Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name\n"
            "tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      812/nginx: master\n"
            "tcp        0      0 0.0.0.0:443             0.0.0.0:*               LISTEN      812/nginx: master\n"
            "tcp        0      0 10.0.1.10:49214         10.0.1.20:8443          ESTABLISHED 1042/node\n"
            "tcp        0      0 10.0.1.10:38112         10.0.1.99:2222          TIME_WAIT   -\n"
            "tcp        0      0 10.0.1.10:55021         10.0.2.1:445            ESTABLISHED 922/cifs"
        )

    # 6. Lateral movement probes
    elif cmd.startswith("ssh"):
        if "10.0.1.99" in cmd or "honey" in cmd:
            response_text = (
                "Connecting to 10.0.1.99:2222 (Honey-Bastion-SSH)...\n"
                "Warning: Permanently added '10.0.1.99' (ED25519) to known hosts.\n"
                "root@10.0.1.99's password: [Accepted default 'admin123']\n"
                "Last login: Fri Oct 30 19:12:04 from 10.0.1.10\n"
                "honey-bastion-ssh:~$ "
            )
            alert_triggered = True
            alert_details = "Attacker connected directly into Honeypot SSH Bastion (10.0.1.99). Attacker quarantined in AI deception sandbox!"
            update_node_status("Honey-Bastion-SSH", "DECOY_TRIGGERED", notes="Attacker logged in via SSH decoy")
            graph_update = {"node_id": "Honey-Bastion-SSH", "status": "DECOY_TRIGGERED"}
        elif "10.0.0.5" in cmd:
            response_text = "ssh: connect to host 10.0.0.5 port 22: Connection refused (Port 22 closed on AD DC)"
        elif "10.0.0.50" in cmd:
            response_text = "ssh: connect to host 10.0.0.50 port 22: Connection timed out (Firewall drops external SSH to Crown Jewel)"
        else:
            response_text = "ssh: command executed. Simulated remote shell handoff."

    elif cmd.startswith("curl") or cmd.startswith("wget"):
        if "10.0.0.50" in cmd or "vault" in cmd:
            response_text = (
                "HTTP/1.1 403 Forbidden\n"
                "Server: Vault/1.15.2 (Enterprise)\n"
                "Content-Type: application/json\n\n"
                "{\"errors\":[\"permission denied: client ip 10.0.1.10 is outside approved CIDR (10.0.4.0/24)\"]}"
            )
            alert_triggered = True
            alert_details = "CRITICAL ALERT: Attacker probed Crown Jewel Vault directly from DMZ! Blast radius containment recommended."
        else:
            response_text = "HTTP/1.1 200 OK\nContent-Type: text/plain\nPayload received."

    elif cmd.startswith("nmap"):
        response_text = (
            "Starting Nmap 7.94 ( https://nmap.org )\n"
            "Nmap scan report for internal-core.corp (10.0.2.1)\n"
            "Host is up (0.00042s latency).\n"
            "PORT     STATE SERVICE\n"
            "22/tcp   open  ssh\n"
            "445/tcp  open  microsoft-ds\n"
            "8443/tcp open  https-alt\n"
            "Nmap done: 1 IP address (1 host up) scanned in 0.84 seconds"
        )

    elif cmd.startswith("sudo"):
        if "-l" in cmd:
            response_text = (
                "Matching Defaults entries for www-data on dmz-web-prod-01:\n"
                "    env_reset, mail_badpass, secure_path=/usr/local/sbin\\:/usr/local/bin\\:/usr/sbin\\:/usr/bin\\:/sbin\\:/bin\n\n"
                "User www-data may run the following commands on dmz-web-prod-01:\n"
                "    (ALL : ALL) NOPASSWD: /usr/bin/find"
            )
        elif "find" in cmd and "exec" in cmd:
            SHELL_STATE["privilege_escalated"] = True
            SHELL_STATE["current_user"] = "root"
            response_text = "Spawning root shell via /usr/bin/find GTFOBins exploit...\nroot@dmz-web-prod-01:/var/www/html#"
            alert_triggered = True
            alert_details = "CRITICAL: Privilege escalation to root achieved via Sudo GTFOBins (/usr/bin/find)!"
        else:
            response_text = "[sudo] password for www-data: sudo: 3 incorrect password attempts"

    elif cmd in ["clear"]:
        response_text = "\033[2J\033[H"
    elif cmd in ["exit", "logout"]:
        response_text = "logout\nConnection to dmz-web-prod-01 closed."
    else:
        # Generic realistic shell response
        response_text = f"bash: {cmd.split()[0]}: command executed in emulated sandbox environment."

    return {
        "command": cmd,
        "output": response_text,
        "mitre_technique": mitre,
        "alert_triggered": alert_triggered,
        "alert_details": alert_details,
        "current_user": SHELL_STATE["current_user"],
        "hostname": SHELL_STATE["hostname"],
        "cwd": SHELL_STATE["cwd"],
        "graph_update": graph_update,
        "timestamp": timestamp
    }

