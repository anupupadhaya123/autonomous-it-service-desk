# Autonomous IT Service Desk (AITSD)

**An AI-Powered Multi-Agent Architecture for Enterprise IT Support & ITIL v4 Incident Management**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-ITIL%20v4%20Aligned-green.svg)](https://www.axelos.com/certifications/itil-service-management)
[![Architecture](https://img.shields.io/badge/Architecture-Multi--Agent%20System-orange.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<p align="center">
  <img src="images/clip.gif" alt="Autonomous IT Service Desk Dashboard Demo" width="100%" />
</p>

---

## 📌 Overview

**Autonomous IT Service Desk (AITSD)** is an enterprise-grade multi-agent system designed to automate IT Service Management (ITSM) and Helpdesk operations. Built around the **ITIL v4 framework**, it demonstrates how specialized AI agents collaborate to triage tickets, calculate dynamic SLAs, dispatch to appropriate support tiers, execute runbook diagnostics, and initiate Major Incident Management (MIM) and SecOps containment protocols.

This project bridges the gap between AI agent automation and real-world IT system support, mimicking the workflows of modern enterprise platforms like **ServiceNow**, **Jira Service Management**, and **PagerDuty**.

---

## 🏛️ Multi-Agent Architecture

```
                       Incoming IT Ticket / Monitoring Alert
                                        │
                                        ▼
    ┌──────────────────────────────────────────────────────────────────────────┐
    │  [1] ITIL Triage & Classification Agent                                 │
    │  • Distinguishes Incident (Break/Fix) vs Service Request                │
    │  • Identifies Technical Domain (Identity, Network, Endpoint, Cloud, Sec) │
    │  • Extracts Technical Entities (Error codes, Hostnames, Systems, IPs)    │
    └─────────────────────────────────────┬────────────────────────────────────┘
                                          │
                                          ▼
    ┌──────────────────────────────────────────────────────────────────────────┐
    │  [2] ITIL Priority & SLA Matrix Agent                                    │
    │  • Computes: Business Impact (Scope) × Urgency (Time-Sensitivity)        │
    │  • Assigns: P1 (Critical), P2 (High), P3 (Medium), P4 (Low)             │
    │  • Calculates SLA Target Deadlines (Response & Resolution Timers)        │
    └─────────────────────────────────────┬────────────────────────────────────┘
                                          │
                                          ▼
    ┌──────────────────────────────────────────────────────────────────────────┐
    │  [3] Support Tier Dispatch & Router Agent                                │
    │  • Routes to: Tier 1 (Helpdesk) | Tier 2 (Desktop) | Tier 3 (Infra)      │
    │  • SecOps CSIRT Queue for security incidents                             │
    │  • Evaluates Emergency On-Call Paging (Opsgenie / PagerDuty)             │
    └─────────────────────────────────────┬────────────────────────────────────┘
                                          │
                                          ▼
    ┌──────────────────────────────────────────────────────────────────────────┐
    │  [4] Runbook & Technical Remediation Agent                               │
    │  • Matches against Knowledge Base (KB) Runbooks                          │
    │  • Generates CLI Diagnostic Commands (PowerShell / CMD / Bash)           │
    │  • Formulates Step-by-Step SOPs for Technicians                          │
    │  • Generates User-Facing Self-Service Guidance                           │
    └─────────────────────────────────────┬────────────────────────────────────┘
                                          │
                                          ▼
    ┌──────────────────────────────────────────────────────────────────────────┐
    │  [5] Major Incident (MIM) & SecOps Escalation Agent                      │
    │  • P1 Critical Bridge: Initiates Emergency Conference Bridge             │
    │  • SecOps Containment: Triggers EDR Host Network Isolation               │
    │  • Recommends Executive & Leadership Actions                             │
    └──────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key IT Support & ITSM Concepts Implemented

### 1. ITIL v4 Record Type Classification
- **Incident Management**: Identifies unplanned service disruptions, crashes, and performance degradations (e.g., Domain Controller outage, VPN failure, BSOD).
- **Service Request Management**: Identifies standard user requests for access, hardware, software licensing, and onboarding (e.g., new hire provisioning).

### 2. Impact × Urgency Priority Matrix
Priorities are dynamically calculated using the standard ITIL matrix:

| Impact (Scope) \ Urgency (Speed) | CRITICAL | HIGH | MEDIUM | LOW |
| :--- | :---: | :---: | :---: | :---: |
| **HIGH** (Organization-Wide / Mission-Critical) | **P1 - Critical** | **P1 - Critical** | **P2 - High** | **P3 - Medium** |
| **MEDIUM** (Department / Multiple Users) | **P2 - High** | **P2 - High** | **P3 - Medium** | **P4 - Low** |
| **LOW** (Single User Affected) | **P2 - High** | **P3 - Medium** | **P4 - Low** | **P4 - Low** |

### 3. Service Level Agreement (SLA) Tracking
Every ticket receives automated response and resolution deadlines:
- **P1 Critical**: 15-minute response target | 4-hour resolution target | *Emergency On-Call Paging*
- **P2 High**: 60-minute response target | 8-hour resolution target | *Lead Engineer Notification*
- **P3 Medium**: 4-hour response target | 24-hour resolution target
- **P4 Low**: 8-hour response target | 72-hour resolution target

### 4. Specialized IT Support Tiers
- **Tier 1 (Service Desk)**: First Contact Resolution (FCR), password resets, MFA resync, basic VPN configuration, and end-user self-service.
- **Tier 2 (Desktop & Systems Support)**: Workstation troubleshooting, OS stop errors (BSOD minidump analysis), hardware diagnostics, and driver rollbacks.
- **Tier 3 (Infrastructure & Cloud Operations)**: Core network routing, enterprise DNS/DHCP, Active Directory domain controllers, and cloud environments (AWS/Azure).
- **SecOps CSIRT**: Security incident response, malware containment, phishing investigation, and credential compromise mitigation.

### 5. Technical Knowledge Base (KB) Runbooks
Contains production-ready standard operating procedures (SOPs) with exact diagnostic commands:
- **KB-1001**: Active Directory / MFA Account Lockout & Reset (`net user %USERNAME% /domain`)
- **KB-1002**: VPN Gateway Tunnel Failure & MTU/DNS Resolution (`ipconfig /flushdns && ping -n 4 vpn.corp.internal`)
- **KB-1003**: Outlook / M365 Authentication Loop & Credential Cache Reset (`cmdkey /list | findstr "MicrosoftOffice"`)
- **KB-1004**: Windows BSOD Stop Error & System File Repair (`sfc /scannow && DISM /Online /Cleanup-Image /RestoreHealth`)
- **KB-1005**: Enterprise Network Latency & Gateway Packet Loss (`tracert -d 8.8.8.8 && nslookup dc01.corp.internal`)
- **KB-1006**: Ransomware Host Containment & SecOps Protocol (`netsh interface set interface name="Wi-Fi" admin=DISABLED`)
- **KB-1007**: Service Request: Software Provisioning & RBAC (`dsregcmd /status`)

---

## 📂 Project Structure

```
intelligent-support-system/
├── agents/
│   ├── __init__.py                # Package initialization and exports
│   ├── classifier_agent.py        # ITIL Triage & Entity Extraction Agent
│   ├── router_agent.py            # Support Tier Dispatcher & Router Agent
│   ├── response_agent.py          # Runbook Matching & Remediation Agent
│   └── escalation_agent.py        # Major Incident (MIM) & SecOps Agent
├── config/
│   ├── settings.yaml              # SLA targets, tier mappings, system config
│   └── prompts.yaml               # ITIL system prompts and templates
├── data/
│   └── knowledge_base.json        # IT Knowledge Base (KB) Runbooks & SOPs
├── utils/
│   ├── __init__.py
│   ├── constants.py               # ITIL Record Types, Priorities, Tiers, Domains
│   └── helpers.py                 # Technical entity regexes, SLA & Priority calculators
├── web/
│   ├── index.html                 # Enterprise Operations Center Dashboard UI
│   ├── style.css                  # Dark-mode styling, glassmorphism, responsive grid
│   └── app.js                     # Frontend API controller & dynamic dossier renderer
├── app.py                         # Web dashboard server (zero-dependency HTTP server)
├── main.py                        # System orchestrator, demo runner & interactive CLI
├── requirements.txt               # Dependencies (PyYAML, python-dotenv)
├── .env.template                  # Environment template
└── README.md                      # Project documentation
```

---

## 🚀 Quickstart & Installation

### Prerequisites
- Python 3.8 or higher
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/anupupadhaya123/autonomous-it-service-desk.git
cd autonomous-it-service-desk
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 💻 Usage

### 1. Launch Enterprise Web Dashboard (GUI) ⭐
Launch the interactive, dark-mode operations center dashboard in your browser:

```bash
python app.py
```
This starts the local web server and automatically opens `http://localhost:5000` in your default browser. You can click 1-click enterprise scenarios or test your own custom IT issues with live agent visualizers.

### 2. Run Automated Enterprise CLI Demo
Process 5 diverse real-world IT scenarios in your terminal:

```bash
python main.py
```

### 3. Run Interactive CLI Mode
Type or paste any real-world IT issue directly in your terminal:

```bash
python main.py --interactive
```

*Example input in interactive mode:*
```
> User reports error 0x80070005 when opening Outlook after Windows update.
```

---

## 📊 Sample Output (Incident Dossier)

```
================================================================================
INGESTING NEW IT TICKET: INC-20260921-110919
================================================================================
Input: "ALERT: An employee on finance workstation ws-fin-04 opened an email attachment named 'Invoice_March.exe' and now their..."

[STEP 1] Triage & Classification Agent analyzing ticket...
  * Record Type:       INCIDENT
  * Technical Domain:  security_incident
  * Business Impact:   LOW
  * Business Urgency:  CRITICAL
  * ITIL Priority:     P2_HIGH
  * SLA Target:        Response in 60m | Resolution in 8h
  * Extracted Errors:  exe

[STEP 2] IT Router Agent determining support tier queue...
  * Assigned Tier:     SECOPS_CSIRT
  * Secondary Queue:   tier_3_infrastructure
  * On-Call Paging:    [!] YES (EMERGENCY ON-CALL PAGING)

[STEP 3] Remediation Agent querying IT Knowledge Base...
  * Matched Runbook:   [KB-1006] Suspected Phishing, Ransomware & Host Containment Protocol
  * Diagnostic CLI:    netsh interface set interface name="Wi-Fi" admin=DISABLED

[STEP 4] Escalation Agent evaluating MIM & Security containment...
  * Escalation Status: [!] ESCALATION TRIGGERED
  * Escalation Level:  Level 3
  * Reason:            Active Security Threat Detected: ransomware, encrypted files, bitcoin ransom
  * Host Isolation:    [SECOPS] IMMEDIATE NETWORK ISOLATION PROTOCOL ACTIVE

################################################################################
IT SERVICE DESK INCIDENT DOSSIER - INC-20260921-110919
################################################################################
Status: [ESCALATED] | Priority: [P2_HIGH] | SLA Target: [2026-09-21 12:09:19]
Assigned Support Tier: secops_csirt
Record Type: incident | Domain: security_incident

--- TECHNICIAN TROUBLESHOOTING RUNBOOK ---
Knowledge Base Reference: KB-1006 - Suspected Phishing, Ransomware & Host Containment Protocol
Diagnostic / Remediation Command:
  $ netsh interface set interface name="Wi-Fi" admin=DISABLED

Standard Operating Procedure (SOP):
  1. IMMEDIATELY isolate the affected host from the network (unplug Ethernet cable and disable Wi-Fi).
  2. DO NOT power off or reboot the workstation to preserve volatile memory (RAM) and running processes.
  3. Trigger an EDR host isolation action via CrowdStrike / Defender for Endpoint console.
  4. Reset user's domain credentials and revoke all active OAuth/Azure AD refresh tokens.
  5. Capture memory dump with WinPmem and preserve MFT/event logs for CSIRT forensic timeline.

--- RECOMMENDED OPERATIONAL ACTION ---
Action: EMERGENCY SECOPS: Trigger EDR network containment on endpoint, revoke Active Directory session tokens, and preserve memory dump.

--- END-USER COMMUNICATION (AUTOMATED ACKNOWLEDGMENT) ---
--------------------------------------------------
Hello,

Thank you for contacting Corporate IT Support.

Your report has been flagged as a **Security Incident** and transferred to SecOps Cyber Security Incident Response Team.
**CRITICAL ACTION REQUIRED:** Please disconnect your computer from the network (unplug Ethernet cable and disconnect Wi-Fi) immediately. Do not restart or power off your machine. An incident responder will contact you shortly.

Ticket Reference: INC-20260921-110919
SLA Target Deadline: 2026-09-21 12:09:19
IT Systems & Support Operations
--------------------------------------------------
################################################################################
```

---

## 🎙️ How to Talk About This Project in an IT Interview

This project demonstrates deep familiarity with enterprise IT support workflows. Here is how you can present it in interviews:

| Role Applied For | What This Project Demonstrates | Interview Talking Points |
| :--- | :--- | :--- |
| **IT Helpdesk / Service Desk Analyst** | First Contact Resolution, Ticket Triage, SLA Compliance | *"I built an automated IT Service Desk system aligned with ITIL v4 that distinguishes Incidents from Service Requests, calculates SLAs, and provides users with immediate self-service troubleshooting steps."* |
| **Desktop Support / Junior SysAdmin** | Technical Troubleshooting, Runbooks, Command-Line Diagnostics | *"The system matches endpoint errors—like Windows BSODs and VPN tunnel drops—to Knowledge Base runbooks, generating exact PowerShell and CMD commands (e.g. SFC, DISM, DNS flush) to accelerate Tier 2 diagnostics."* |
| **ITSM / Incident Coordinator** | ITIL Governance, Impact/Urgency Matrix, Major Incident Management | *"I implemented an ITIL v4 priority matrix where business impact and urgency determine P1–P4 severity. P1 incidents automatically trigger Major Incident Management (MIM) bridge alerts and on-call paging."* |
| **Junior SOC / SecOps Analyst** | Incident Containment, Ransomware Triage, EDR Protocol | *"The system includes security trigger detection. When ransomware or phishing is detected, it automatically routes to SecOps, activates host isolation protocols, and instructs the user to disconnect from the network to prevent lateral movement."* |

---

## 🛠️ Extensibility & Future Enhancements

- [x] **Web Dashboard**: Interactive dark-mode operations dashboard with real-time multi-agent visualization, SLA timers, and runbook execution.
- [ ] **REST API Integration**: FastAPI backend to ingest webhooks from Jira Service Management and ServiceNow.
- [ ] **LLM Integration (RAG)**: Connect to Google Gemini / OpenAI / local Ollama for semantic vector search over enterprise confluence documentation.
- [ ] **Active Directory Integration**: Live LDAP/Graph API connection to query user lockout status and reset passwords directly.

---

## 👤 Author

**anup-work** ([@anupupadhaya123](https://github.com/anupupadhaya123))

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
