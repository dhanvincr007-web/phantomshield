"""
PhantomShield (GraphShield AI) — J.A.R.V.I.S. Real-Time Alert Dispatcher
Multi-Channel Outbound Incident Dispatcher (Email, SMS & Instant Mobile Push)
hackFront India 2026 Hackathon | Neo4j Track - GraphOps Problem Statement

Primary Pre-Configured Alert Recipients:
- Primary Alert Email:        dhanvincr007@gmail.com
- Primary Alert Mobile Phone: +917708720395
- Zero-Config Push Topic:     phantomshield-jarvis-7708720395
"""

import os
import smtplib
import asyncio
import logging
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
import httpx

logger = logging.getLogger("phantomshield.notifier")

class JARVISNotifier:
    """
    J.A.R.V.I.S. Multi-Channel Alert Dispatcher
    Dispatches critical security alerts across:
    1. Gmail SMTP Email (HTML + Plain text)
    2. Mobile SMS via Twilio REST API
    3. Zero-Config Instant Mobile Push via ntfy.sh
    """

    def __init__(self):
        # Default Team Lead primary contact details
        self.default_email: str = "dhanvincr007@gmail.com"
        self.default_phone: str = "+917708720395"
        self.default_ntfy_topic: str = "phantomshield-jarvis-7708720395"

        # Read environment variables (with fallback to defaults)
        self.email_sender = os.getenv("JARVIS_EMAIL_SENDER", self.default_email).strip()
        self.email_password = os.getenv("JARVIS_EMAIL_APP_PASSWORD", "").strip()
        self.email_recipient = os.getenv("JARVIS_EMAIL_RECIPIENT", self.default_email).strip()
        self.alert_phone = os.getenv("JARVIS_ALERT_PHONE_NUMBER", self.default_phone).strip()
        self.ntfy_topic = os.getenv("JARVIS_NTFY_TOPIC", self.default_ntfy_topic).strip()

        # Twilio SMS configuration
        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
        self.twilio_from = os.getenv("TWILIO_FROM_NUMBER", "").strip()

        # Dispatch history tracking
        self.dispatch_history: List[Dict[str, Any]] = []
        self.total_dispatches: int = 0

    def get_status(self) -> Dict[str, Any]:
        """Return configuration status of all outbound alert channels."""
        has_smtp = bool(self.email_password and self.email_sender)
        has_twilio = bool(self.twilio_sid and self.twilio_token and self.twilio_from)
        
        return {
            "dispatcher_name": "J.A.R.V.I.S. Real-Time Alert Dispatcher",
            "version": "2.4.0-AlertHub",
            "primary_recipients": {
                "email": self.email_recipient,
                "phone": self.alert_phone,
                "ntfy_topic": self.ntfy_topic,
                "ntfy_web_url": f"https://ntfy.sh/{self.ntfy_topic}"
            },
            "channels": {
                "email_smtp": {
                    "enabled": True,
                    "mode": "LIVE_SMTP" if has_smtp else "SIMULATED_LOGGED",
                    "sender": self.email_sender,
                    "host": "smtp.gmail.com:587 (TLS)"
                },
                "mobile_sms": {
                    "enabled": True,
                    "mode": "LIVE_TWILIO" if has_twilio else "SIMULATED_LOGGED",
                    "recipient": self.alert_phone,
                    "provider": "Twilio REST API"
                },
                "mobile_push": {
                    "enabled": True,
                    "mode": "LIVE_INSTANT_PUSH",
                    "topic": self.ntfy_topic,
                    "provider": "ntfy.sh (Zero-Config Mobile Push)"
                }
            },
            "total_dispatches": self.total_dispatches,
            "recent_dispatches_count": len(self.dispatch_history)
        }

    # ------------------------------------------------------------------
    # Channel 1: Gmail SMTP Email Alert Dispatch
    # ------------------------------------------------------------------
    def _send_email_sync(self, subject: str, html_content: str, text_content: str, recipient: str) -> Dict[str, Any]:
        """Synchronous SMTP worker executed in thread pool."""
        if not self.email_password:
            logger.info(f"[J.A.R.V.I.S. NOTIFIER] Gmail app password not configured. Simulated dispatch to {recipient} logged.")
            return {
                "channel": "EMAIL",
                "status": "SIMULATED_DISPATCH_LOGGED",
                "recipient": recipient,
                "subject": subject,
                "detail": "Simulated dispatch logged. Set JARVIS_EMAIL_APP_PASSWORD in .env for live TLS delivery."
            }

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"J.A.R.V.I.S. Sentinel <{self.email_sender}>"
            msg["To"] = recipient

            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            msg.attach(part1)
            msg.attach(part2)

            with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
                server.starttls()
                server.login(self.email_sender, self.email_password)
                server.sendmail(self.email_sender, recipient, msg.as_string())

            logger.info(f"[J.A.R.V.I.S. NOTIFIER] Live email alert dispatched successfully to {recipient}")
            return {
                "channel": "EMAIL",
                "status": "DELIVERED",
                "recipient": recipient,
                "subject": subject
            }
        except Exception as e:
            logger.warning(f"[J.A.R.V.I.S. NOTIFIER] Email delivery error ({e}). Fallback to simulated log.")
            return {
                "channel": "EMAIL",
                "status": "FALLBACK_LOGGED",
                "recipient": recipient,
                "subject": subject,
                "error": str(e)
            }

    async def send_email_alert(self, subject: str, html_content: str, text_content: str, recipient: Optional[str] = None) -> Dict[str, Any]:
        """Asynchronously dispatch email alert via Gmail SMTP."""
        target_email = recipient or self.email_recipient
        return await asyncio.to_thread(self._send_email_sync, subject, html_content, text_content, target_email)

    # ------------------------------------------------------------------
    # Channel 2: Mobile SMS Dispatch via Twilio REST API
    # ------------------------------------------------------------------
    async def send_sms_alert(self, message: str, phone: Optional[str] = None) -> Dict[str, Any]:
        """Send concise 160-char SMS alert to target mobile number."""
        target_phone = phone or self.alert_phone

        # Ensure message fits standard SMS bounds
        if len(message) > 160:
            sms_body = message[:157] + "..."
        else:
            sms_body = message

        if not (self.twilio_sid and self.twilio_token and self.twilio_from):
            logger.info(f"[J.A.R.V.I.S. NOTIFIER] Twilio credentials not configured. Simulated SMS to {target_phone} logged.")
            return {
                "channel": "SMS",
                "status": "SIMULATED_DISPATCH_LOGGED",
                "recipient": target_phone,
                "message": sms_body,
                "detail": "Simulated SMS dispatch logged. Add TWILIO_ACCOUNT_SID / AUTH_TOKEN in .env for live SMS."
            }

        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Messages.json"
        data = {
            "From": self.twilio_from,
            "To": target_phone,
            "Body": sms_body
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, data=data, auth=(self.twilio_sid, self.twilio_token))
                if res.status_code in (200, 201):
                    logger.info(f"[J.A.R.V.I.S. NOTIFIER] Live SMS delivered to {target_phone}")
                    return {
                        "channel": "SMS",
                        "status": "DELIVERED",
                        "recipient": target_phone,
                        "sid": res.json().get("sid")
                    }
                else:
                    return {
                        "channel": "SMS",
                        "status": "FAILED",
                        "recipient": target_phone,
                        "code": res.status_code,
                        "detail": res.text
                    }
        except Exception as e:
            logger.warning(f"[J.A.R.V.I.S. NOTIFIER] SMS error ({e}). Falling back to simulated log.")
            return {
                "channel": "SMS",
                "status": "FALLBACK_LOGGED",
                "recipient": target_phone,
                "error": str(e)
            }

    # ------------------------------------------------------------------
    # Channel 3: Zero-Config Instant Mobile Push via ntfy.sh
    # ------------------------------------------------------------------
    async def send_mobile_push(
        self, 
        title: str, 
        message: str, 
        priority: str = "urgent", 
        tags: Optional[List[str]] = None,
        topic: Optional[str] = None
    ) -> Dict[str, Any]:
        """Post instant real-time mobile push alert to ntfy.sh (No API key needed!)."""
        target_topic = topic or self.ntfy_topic
        url = f"https://ntfy.sh/{target_topic}"
        tag_str = ",".join(tags or ["warning", "shield", "robot"])

        headers = {
            "Title": title,
            "Priority": priority,
            "Tags": tag_str,
            "Click": "http://localhost:3000"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, content=message, headers=headers)
                if res.status_code == 200:
                    logger.info(f"[J.A.R.V.I.S. NOTIFIER] Instant push alert posted to {url}")
                    return {
                        "channel": "PUSH_NTFY",
                        "status": "DELIVERED",
                        "endpoint": url,
                        "topic": target_topic
                    }
                else:
                    return {
                        "channel": "PUSH_NTFY",
                        "status": "FAILED",
                        "code": res.status_code,
                        "detail": res.text
                    }
        except Exception as e:
            logger.warning(f"[J.A.R.V.I.S. NOTIFIER] Push error ({e}). Falling back to local log.")
            return {
                "channel": "PUSH_NTFY",
                "status": "FALLBACK_LOGGED",
                "endpoint": url,
                "error": str(e)
            }

    # ------------------------------------------------------------------
    # Unified Multi-Channel Dispatcher
    # ------------------------------------------------------------------
    async def dispatch_incident_alert(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Concurrently dispatches security alerts across Email, SMS, and Mobile Push.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        severity = incident.get("severity", "CRITICAL")
        title = incident.get("title", "Autonomous Micro-Segmentation Safeguard Triggered")
        target_node = incident.get("target_node", "decoy-ssh-01")
        mitre_id = incident.get("mitre_id", "T1552.004")
        reasoning = incident.get("reasoning", "High-value Canary Token breached. Topological micro-segmentation enforced.")
        brvi = incident.get("brvi", "92% -> 0.0% (SECURE)")

        # 1. Prepare Subject & SMS
        subject = f"[J.A.R.V.I.S. ALERT] {severity}: {title} ({mitre_id})"
        sms_text = f"[J.A.R.V.I.S.] {severity}: {title} on {target_node} ({mitre_id}). Blast radius collapsed to 0.0%."

        # 2. Prepare HTML Email Body
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #050811; color: #e2e8f0; margin: 0; padding: 24px; }}
  .card {{ background: #0b1222; border: 1px solid #06b6d4; border-radius: 12px; max-width: 600px; margin: 0 auto; padding: 24px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
  .header {{ border-bottom: 1px solid #1e293b; padding-bottom: 16px; margin-bottom: 16px; }}
  .badge {{ display: inline-block; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 11px; text-transform: uppercase; font-family: monospace; }}
  .badge-critical {{ background: #450a0a; color: #f87171; border: 1px solid #ef4444; }}
  .badge-sentinel {{ background: #082f49; color: #38bdf8; border: 1px solid #0284c7; margin-left: 8px; }}
  h1 {{ margin: 8px 0 0 0; font-size: 18px; color: #ffffff; }}
  .metadata {{ margin: 16px 0; background: #070b16; border-radius: 8px; padding: 14px; border: 1px solid #1e293b; font-family: monospace; font-size: 12px; }}
  .row {{ display: flex; justify-content: space-between; margin-bottom: 8px; }}
  .label {{ color: #94a3b8; }}
  .val {{ color: #38bdf8; font-weight: bold; }}
  .reasoning {{ background: #172554; border-left: 4px solid #3b82f6; padding: 12px; margin: 16px 0; border-radius: 4px; font-size: 13px; line-height: 1.5; }}
  .btn {{ display: inline-block; background: #06b6d4; color: #000000; font-weight: bold; text-decoration: none; padding: 10px 20px; border-radius: 6px; font-size: 12px; margin-top: 12px; }}
  .footer {{ margin-top: 24px; border-top: 1px solid #1e293b; padding-top: 12px; font-size: 11px; color: #64748b; font-family: monospace; }}
</style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div>
        <span class="badge badge-critical">{severity}</span>
        <span class="badge badge-sentinel">J.A.R.V.I.S. SENTINEL</span>
      </div>
      <h1>🛡️ Autonomous Threat Safeguard Engaged</h1>
    </div>

    <div class="reasoning">
      <strong>Incident Summary:</strong><br>
      {reasoning}
    </div>

    <div class="metadata">
      <div class="row"><span class="label">Target Asset:</span><span class="val">{target_node}</span></div>
      <div class="row"><span class="label">MITRE ATT&CK:</span><span class="val">{mitre_id}</span></div>
      <div class="row"><span class="label">BRVI Risk Score:</span><span class="val">{brvi}</span></div>
      <div class="row"><span class="label">Action Enforced:</span><span class="val" style="color:#a855f7;">AUTONOMOUS_MICRO_SEGMENTATION</span></div>
      <div class="row"><span class="label">Timestamp:</span><span class="val">{timestamp}</span></div>
      <div class="row"><span class="label">Primary Recipient:</span><span class="val">{self.email_recipient} ({self.alert_phone})</span></div>
    </div>

    <p style="font-size: 12px; color: #94a3b8; margin: 0;">
      All outbound lateral movement egress edges for <code>{target_node}</code> were severed automatically in real time.
    </p>

    <a href="http://localhost:3000" class="btn">View SOC Command Center →</a>

    <div class="footer">
      PhantomShield (GraphShield AI) • hackFront India 2026 (Neo4j Track)<br>
      Team Lead: Dhanvin (dhanvincr007@gmail.com | +917708720395)
    </div>
  </div>
</body>
</html>
"""

        # 3. Plain Text Body
        plain_body = f"""
======================================================================
[J.A.R.V.I.S. ALERT] {severity}: {title}
======================================================================
Target Asset:    {target_node}
MITRE ATT&CK:    {mitre_id}
Risk Index:      {brvi}
Action Enforced: AUTONOMOUS_MICRO_SEGMENTATION
Timestamp:       {timestamp}
Reasoning:       {reasoning}

Primary Alerts:  {self.email_recipient} | {self.alert_phone}
Dashboard:       http://localhost:3000
======================================================================
PhantomShield (GraphShield AI) — hackFront India 2026
"""

        # 4. Push message body
        push_msg = f"Target: {target_node} ({mitre_id})\nRisk: {brvi}\n{reasoning}"

        # 5. Dispatch across all 3 channels concurrently
        email_task = self.send_email_alert(subject, html_body, plain_body)
        sms_task = self.send_sms_alert(sms_text)
        push_task = self.send_mobile_push(
            title=f"🛡️ J.A.R.V.I.S. [{severity}]: {target_node}",
            message=push_msg,
            priority="urgent",
            tags=["shield", "warning", "skull"]
        )

        email_res, sms_res, push_res = await asyncio.gather(email_task, sms_task, push_task, return_exceptions=True)

        dispatch_record = {
            "timestamp": timestamp,
            "incident": incident,
            "subject": subject,
            "channels": {
                "email": email_res if isinstance(email_res, dict) else {"status": "ERROR", "error": str(email_res)},
                "sms": sms_res if isinstance(sms_res, dict) else {"status": "ERROR", "error": str(sms_res)},
                "push": push_res if isinstance(push_res, dict) else {"status": "ERROR", "error": str(push_res)}
            }
        }

        self.dispatch_history.append(dispatch_record)
        if len(self.dispatch_history) > 50:
            self.dispatch_history.pop(0)

        self.total_dispatches += 1
        return dispatch_record

    async def test_dispatch(self, custom_note: Optional[str] = None) -> Dict[str, Any]:
        """Dispatch a test notification to verify all outbound channels."""
        test_incident = {
            "severity": "CRITICAL",
            "title": "J.A.R.V.I.S. Alert Dispatcher Verification Test",
            "target_node": "decoy-ssh-01",
            "mitre_id": "T1552.004",
            "reasoning": custom_note or "Diagnostic test verifying live Gmail SMTP, Twilio SMS, and ntfy.sh instant push routing.",
            "brvi": "92% -> 0.0% (SECURE)"
        }
        return await self.dispatch_incident_alert(test_incident)


# Global singleton instance
jarvis_notifier = JARVISNotifier()

