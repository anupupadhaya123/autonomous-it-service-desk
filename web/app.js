/**
 * Autonomous IT Service Desk (AITSD) - Frontend & In-Browser Agent Engine
 * Supports both:
 * 1. Client-Server Mode (via python app.py)
 * 2. 100% Serverless / Client-Side Mode (for GitHub Pages hosting)
 */

// ==========================================================================
// 1. In-Browser IT Knowledge Base (KB) Runbooks
// ==========================================================================
const BROWSER_KNOWLEDGE_BASE = [
    {
        id: "KB-1001",
        title: "Active Directory / MFA Account Lockout & Self-Service Password Reset",
        domain: "identity_access",
        tier: "tier_1_service_desk",
        keywords: ["password", "locked", "lockout", "mfa", "okta", "duo", "login failed", "expired password", "access denied"],
        summary: "Resolution workflow for locked Active Directory accounts and multi-factor authentication (MFA) desynchronization.",
        diagnostic_command: "net user %USERNAME% /domain",
        troubleshooting_steps: [
            "1. Verify caller identity using employee ID and manager verification.",
            "2. Query Active Directory to check lockout status: 'Search-ADAccount -LockedOut'.",
            "3. Execute 'Unlock-ADAccount -Identity <username>' to clear the lockout flag.",
            "4. If MFA token is out of sync, trigger an MFA device reset in Okta / Entra ID admin console.",
            "5. Instruct user to sign in through the self-service password portal to establish new compliant credentials."
        ],
        self_service_instructions: "Please visit https://identity.corp.internal/self-service to verify your identity via SMS or secondary email and reset your domain credentials."
    },
    {
        id: "KB-1002",
        title: "VPN Gateway Tunnel Failure & MTU/DNS Resolution",
        domain: "network_vpn",
        tier: "tier_1_service_desk",
        keywords: ["vpn", "globalprotect", "anyconnect", "tunnel", "gateway not reachable", "disconnected", "remote access"],
        summary: "Troubleshooting remote access VPN connection drops, SSL/IPsec tunnel negotiation failures, and local DNS conflicts.",
        diagnostic_command: "ipconfig /flushdns && ping -n 4 vpn.corp.internal",
        troubleshooting_steps: [
            "1. Confirm user has an active internet connection outside the VPN.",
            "2. Flush local DNS resolver cache to clear stale gateway records: 'ipconfig /flushdns'.",
            "3. In VPN client settings, switch gateway selection from 'Auto' to preferred regional gateway.",
            "4. Verify client certificate validity in user's Personal Certificate Store (certmgr.msc).",
            "5. Restart the VPN Agent service via services.msc."
        ],
        self_service_instructions: "Disconnect from Wi-Fi, restart your home router, reconnect to Wi-Fi, right-click the VPN icon in your system tray and select 'Refresh Connection'."
    },
    {
        id: "KB-1003",
        title: "Microsoft Outlook / M365 Authentication Loop & Credential Cache Reset",
        domain: "software_cloud",
        tier: "tier_1_service_desk",
        keywords: ["outlook", "exchange", "password prompt", "m365", "teams", "credential loop", "autodiscover", "auth loop"],
        summary: "Resolves continuous password prompting loops in Microsoft Outlook, Teams, and Office 365 desktop apps.",
        diagnostic_command: "cmdkey /list | findstr \"MicrosoftOffice\"",
        troubleshooting_steps: [
            "1. Completely exit Outlook, Teams, and all Microsoft 365 applications.",
            "2. Open Windows Credential Manager -> Windows Credentials.",
            "3. Locate and delete all entries under 'Generic Credentials' matching 'MicrosoftOffice16_Data*' and 'adal*'.",
            "4. Clear Modern Authentication token cache at '%localappdata%\\Microsoft\\TokenBroker\\Cache'.",
            "5. Relaunch Outlook and enter corporate credentials when prompted by Modern Auth dialog."
        ],
        self_service_instructions: "Close Outlook and Teams. Open Control Panel > Credential Manager > Windows Credentials, remove entries with 'MicrosoftOffice', then reopen Outlook."
    },
    {
        id: "KB-1004",
        title: "Windows BSOD / Driver Crash Dump Analysis & System File Repair",
        domain: "endpoint_hardware",
        tier: "tier_2_desktop_systems",
        keywords: ["bsod", "blue screen", "crash", "critical_process_died", "dump", "0x000000ef", "0x80070005", "stop code", "minidump"],
        summary: "Investigates Blue Screen of Death (BSOD) stop errors, corrupted system drivers, and kernel dump logs.",
        diagnostic_command: "sfc /scannow && DISM /Online /Cleanup-Image /RestoreHealth",
        troubleshooting_steps: [
            "1. Boot system into Windows Recovery Environment (WinRE) or Safe Mode with Networking.",
            "2. Copy memory dump files from 'C:\\Windows\\Minidump\\' for analysis in WinDbg.",
            "3. Run System File Checker ('sfc /scannow') and DISM restore health command.",
            "4. Check Device Manager for recently updated display, network, or storage controllers and roll back driver.",
            "5. Run Windows Memory Diagnostic ('mdsched.exe') to test for physical RAM faults."
        ],
        self_service_instructions: "Save all open files immediately. If the computer crashes repeatedly, hold the power button for 10 seconds to shut down and contact Tier 2 Desktop Support."
    },
    {
        id: "KB-1005",
        title: "Enterprise Network Latency, DNS Resolution & Gateway Packet Loss",
        domain: "network_vpn",
        tier: "tier_3_infrastructure",
        keywords: ["network", "latency", "dns", "packet loss", "core switch", "router", "gateway", "nxdomain", "datacenter", "vlan"],
        summary: "Escalation procedures for enterprise network degradation, DNS lookup timeouts, and core switch interface drops.",
        diagnostic_command: "tracert -d 8.8.8.8 && nslookup dc01.corp.internal",
        troubleshooting_steps: [
            "1. Perform bidirectional traceroute between endpoint and enterprise core switch.",
            "2. Query primary and secondary DNS forwarders to check for zone transfer delays or cache poison.",
            "3. Inspect core switch interface telemetry for CRC errors, duplex mismatches, or flapping ports.",
            "4. Verify DHCP pool exhaustion on affected VLAN subnet.",
            "5. If organization-wide, initiate Major Incident Management (MIM) bridge with Network Operations Center (NOC)."
        ],
        self_service_instructions: "Network engineering is actively investigating high latency on the corporate backbone. No user action is required."
    },
    {
        id: "KB-1006",
        title: "Suspected Phishing, Ransomware & Host Containment Protocol",
        domain: "security_incident",
        tier: "secops_csirt",
        keywords: ["ransomware", "malware", "virus", "phishing", "suspicious link", "compromised", "hacked", "lockbit", "bitcoin ransom", "encrypted files"],
        summary: "Emergency containment protocol for malware execution, credential harvesting, or ransomware behavior.",
        diagnostic_command: "netsh interface set interface name=\"Wi-Fi\" admin=DISABLED",
        troubleshooting_steps: [
            "1. IMMEDIATELY isolate the affected host from the network (unplug Ethernet cable and disable Wi-Fi).",
            "2. DO NOT power off or reboot the workstation to preserve volatile memory (RAM) and running processes.",
            "3. Trigger an EDR host isolation action via CrowdStrike / Defender for Endpoint console.",
            "4. Reset user's domain credentials and revoke all active OAuth/Azure AD refresh tokens.",
            "5. Capture memory dump with WinPmem and preserve MFT/event logs for CSIRT forensic timeline."
        ],
        self_service_instructions: "UNPLUG YOUR NETWORK CABLE AND DISCONNECT WI-FI IMMEDIATELY. DO NOT TURN OFF YOUR COMPUTER. A SecOps analyst will contact you directly."
    },
    {
        id: "KB-1007",
        title: "Service Request: Software Provisioning & Role-Based Access (RBAC)",
        domain: "software_cloud",
        tier: "tier_1_service_desk",
        keywords: ["provision", "access request", "new hire", "license", "github", "jira", "aws access", "software install", "admin rights"],
        summary: "Fulfillment process for enterprise software licensing, cloud platform access, and developer tool grants.",
        diagnostic_command: "dsregcmd /status",
        troubleshooting_steps: [
            "1. Validate that ticket has documented managerial approval in ITSM workflow.",
            "2. Verify user's department and job code against the RBAC matrix.",
            "3. Add user account to the corresponding Entra ID / Okta security group.",
            "4. Deploy software package silently via Microsoft Intune / SCCM company portal.",
            "5. Notify user once provisioning is complete with getting-started documentation."
        ],
        self_service_instructions: "Your request has been approved. You can install the approved application directly from the Company Portal app on your workstation without local admin rights."
    }
];

// Enterprise Scenario Presets
const PRESET_SCENARIOS = {
    p1: "URGENT: Active Directory domain controller dc01.corp.internal is completely unresponsive. Over 400 employees across all departments are locked out and production systems cannot authenticate users. This is a complete company-wide outage!",
    ransomware: "ALERT: An employee on finance workstation ws-fin-04 opened an email attachment named 'Invoice_March.exe' and now their screen shows a LockBit ransomware note saying all corporate files are encrypted. Bitcoin ransom demanded immediately!",
    bsod: "My Dell Latitude laptop has blue screened 3 times this morning with stop code 0x000000ef (CRITICAL_PROCESS_DIED). It keeps rebooting into Windows Recovery. Need assistance as I cannot attend client meetings.",
    vpn: "Hello IT helpdesk, my GlobalProtect VPN client is failing to connect with 'Gateway not reachable' error when working remotely from home. I have tried restarting my laptop twice.",
    provisioning: "Service request: Please provision new hire laptop and accounts for Alex Rivera (Senior Cloud Engineer) starting next Monday. Needs 32GB MacBook Pro, AWS production IAM access, and GitHub Enterprise organization invite."
};

let sessionTickets = [];

// ==========================================================================
// 2. Client-Side Multi-Agent Simulation Engine (for GitHub Pages)
// ==========================================================================
function processTicketInBrowser(text) {
    const textLower = text.toLowerCase();
    const timestamp = new Date();
    const ticketId = `INC-${timestamp.getFullYear()}${String(timestamp.getMonth()+1).padStart(2,'0')}${String(timestamp.getDate()).padStart(2,'0')}-${String(timestamp.getHours()).padStart(2,'0')}${String(timestamp.getMinutes()).padStart(2,'0')}${String(timestamp.getSeconds()).padStart(2,'0')}`;

    // 1. Entity Extraction
    const hexErrors = text.match(/\b0x[0-9a-fA-F]{4,8}\b/g) || [];
    const bsodErrors = text.match(/\b[A-Z_]{5,30}_(?:DIED|ERROR|FAILED|EXCEPTION|FAULT|VIOLATION)\b/g) || [];
    const httpErrors = (text.match(/\b(?:http\s*)?(?:4\d{2}|5\d{2})\b/gi) || []).filter(e => !isNaN(e)).map(e => `HTTP ${e}`);
    const hostnames = text.match(/\b(?:srv|dc|ws|vm|db|fw|rt|sw)-[a-zA-Z0-9-]+\b/gi) || [];

    const systems = [
        "active directory", "azure ad", "entra id", "okta", "mfa", "duo",
        "vpn", "globalprotect", "cisco anyconnect", "outlook", "exchange",
        "m365", "teams", "jira", "github", "aws", "azure", "windows 11"
    ].filter(s => textLower.includes(s));

    const securityTriggers = ["ransomware", "malware", "virus", "phishing", "lockbit", "encrypted files", "compromised", "hacked"].filter(s => textLower.includes(s));
    const outageTriggers = ["all users", "company-wide", "production down", "entire team", "datacenter", "core switch", "domain controller", "unresponsive"].filter(s => textLower.includes(s));

    const combinedErrors = [...new Set([...hexErrors, ...bsodErrors, ...httpErrors])];

    // 2. Record Type
    let recordType = "incident";
    if (textLower.includes("provision") || textLower.includes("request") || textLower.includes("new hire") || textLower.includes("license")) {
        if (!combinedErrors.length && !outageTriggers.length && !securityTriggers.length) {
            recordType = "service_request";
        }
    }

    // 3. Domain
    let domain = "general_it";
    if (securityTriggers.length || textLower.includes("ransomware") || textLower.includes("phishing")) {
        domain = "security_incident";
    } else if (textLower.includes("password") || textLower.includes("lockout") || textLower.includes("mfa") || textLower.includes("okta") || textLower.includes("active directory") || textLower.includes("login")) {
        domain = "identity_access";
    } else if (textLower.includes("vpn") || textLower.includes("globalprotect") || textLower.includes("wi-fi") || textLower.includes("dns") || textLower.includes("network") || textLower.includes("packet loss")) {
        domain = "network_vpn";
    } else if (textLower.includes("bsod") || textLower.includes("blue screen") || textLower.includes("laptop") || textLower.includes("hardware") || textLower.includes("monitor")) {
        domain = "endpoint_hardware";
    } else if (textLower.includes("outlook") || textLower.includes("m365") || textLower.includes("teams") || textLower.includes("aws") || textLower.includes("azure")) {
        domain = "software_cloud";
    }

    // 4. Impact & Urgency
    let impact = outageTriggers.length || textLower.includes("company-wide") || textLower.includes("production down") ? "high" : (textLower.includes("department") || textLower.includes("team") ? "medium" : "low");
    let urgency = domain === "security_incident" || textLower.includes("urgent") || textLower.includes("critical") || textLower.includes("immediately") ? "critical" : (textLower.includes("asap") || textLower.includes("cannot work") ? "high" : "low");

    // 5. Priority Matrix
    let priority = "P4_LOW";
    if (impact === "high") {
        priority = (urgency === "critical" || urgency === "high") ? "P1_CRITICAL" : (urgency === "medium" ? "P2_HIGH" : "P3_MEDIUM");
    } else if (impact === "medium") {
        priority = (urgency === "critical" || urgency === "high") ? "P2_HIGH" : (urgency === "medium" ? "P3_MEDIUM" : "P4_LOW");
    } else {
        priority = urgency === "critical" ? "P2_HIGH" : (urgency === "high" ? "P3_MEDIUM" : "P4_LOW");
    }

    // 6. SLA Calculations
    const slaMap = {
        P1_CRITICAL: { respMins: 15, resHours: 4, desc: "Critical Outage: 15-min response, 4-hour resolution target" },
        P2_HIGH: { respMins: 60, resHours: 8, desc: "High Priority: 1-hour response, 8-hour resolution target" },
        P3_MEDIUM: { respMins: 240, resHours: 24, desc: "Medium Priority: 4-hour response, 24-hour resolution target" },
        P4_LOW: { respMins: 480, resHours: 72, desc: "Low Priority: 8-hour response, 72-hour resolution target" }
    };
    const sla = slaMap[priority];
    const respDate = new Date(timestamp.getTime() + sla.respMins * 60000);
    const resDate = new Date(timestamp.getTime() + sla.resHours * 3600000);

    // 7. Support Tier Dispatch
    let primaryTier = "tier_1_service_desk";
    let secondaryTier = "tier_2_desktop_systems";
    let pagingRequired = false;

    if (domain === "security_incident") {
        primaryTier = "secops_csirt";
        secondaryTier = "tier_3_infrastructure";
        pagingRequired = true;
    } else if (impact === "high" && (domain === "network_vpn" || domain === "software_cloud" || domain === "endpoint_hardware")) {
        primaryTier = "tier_3_infrastructure";
        secondaryTier = "tier_2_desktop_systems";
        pagingRequired = true;
    } else if (domain === "endpoint_hardware") {
        primaryTier = "tier_2_desktop_systems";
        secondaryTier = "tier_1_service_desk";
    }

    if (priority === "P1_CRITICAL") pagingRequired = true;

    // 8. Runbook Matching
    let matchedKb = null;
    let highestScore = 0;
    for (const kb of BROWSER_KNOWLEDGE_BASE) {
        let score = 0;
        if (kb.domain === domain) score += 3;
        for (const kw of kb.keywords) {
            if (textLower.includes(kw)) score += 2;
        }
        for (const err of combinedErrors) {
            if (kb.keywords.some(k => k.includes(err.toLowerCase()))) score += 5;
        }
        if (score > highestScore) {
            highestScore = score;
            matchedKb = kb;
        }
    }
    if (!matchedKb || highestScore < 2) {
        matchedKb = {
            id: "KB-GENERIC",
            title: "Standard IT Service Desk Triage",
            diagnostic_command: "echo \"No automated script available\"",
            troubleshooting_steps: [
                "1. Contact user to gather detailed system logs.",
                "2. Verify network reachability and endpoint compliance.",
                "3. Escalate to senior systems engineer if unresolved within SLA window."
            ],
            self_service_instructions: "Please restart your application or computer and contact your local IT helpdesk if the issue persists."
        };
    }

    // 9. Escalation & MIM
    let needsEscalation = false;
    let mimBridge = false;
    let hostIsolation = false;
    let escalationReason = "Standard operational parameters maintained.";
    let escalationLevel = 1;

    if (domain === "security_incident" || securityTriggers.length) {
        needsEscalation = true;
        hostIsolation = true;
        escalationReason = `Active Security Threat Detected: ${securityTriggers.join(', ') || 'malware execution'}`;
        escalationLevel = 3;
    } else if (priority === "P1_CRITICAL") {
        needsEscalation = true;
        mimBridge = true;
        escalationReason = "P1 Mission-Critical Service Outage affecting enterprise operations.";
        escalationLevel = 3;
    } else if (priority === "P2_HIGH" && outageTriggers.length) {
        needsEscalation = true;
        escalationReason = "P2 High Priority incident impacting critical department services.";
        escalationLevel = 2;
    }

    // Return structured dossier
    return {
        ticket: {
            id: ticketId,
            content: text,
            created_at: timestamp.toISOString()
        },
        triage: {
            ticket_id: ticketId,
            record_type: recordType,
            domain: domain,
            impact: impact,
            urgency: urgency,
            priority: priority,
            sla: {
                priority: priority,
                response_target_minutes: sla.respMins,
                resolution_target_hours: sla.resHours,
                response_deadline: respDate.toLocaleString(),
                resolution_deadline: resDate.toLocaleString(),
                policy_description: sla.desc
            },
            extracted_entities: {
                error_codes: combinedErrors,
                hostnames: hostnames,
                detected_systems: systems,
                security_indicators: securityTriggers
            }
        },
        routing: {
            ticket_id: ticketId,
            assigned_tier: primaryTier,
            secondary_tier: secondaryTier,
            paging_required: pagingRequired,
            routing_rationale: `Dispatched to ${primaryTier} based on domain '${domain}' with ${priority} priority and ${impact} impact.`
        },
        remediation: {
            ticket_id: ticketId,
            matched_kb_id: matchedKb.id,
            matched_kb_title: matchedKb.title,
            diagnostic_command: matchedKb.diagnostic_command,
            technician_steps: matchedKb.troubleshooting_steps,
            user_response: `Hello,\n\nThank you for contacting Corporate IT Support.\n\nYour ticket has been assigned to our **${primaryTier}** under priority **${priority}**.\nOur target response window is within ${sla.respMins} minutes.\n\n**Self-Service Troubleshooting Recommendation:**\n${matchedKb.self_service_instructions}\n\nTicket Reference: ${ticketId}\nSLA Target Deadline: ${respDate.toLocaleString()}\nIT Systems & Support Operations`
        },
        escalation: {
            ticket_id: ticketId,
            needs_escalation: needsEscalation,
            escalation_level: escalationLevel,
            escalation_reason: escalationReason,
            mim_bridge_required: mimBridge,
            host_isolation_required: hostIsolation,
            recommended_action: mimBridge ? "CRITICAL MIM: Open emergency incident conference bridge, alert IT Leadership, and broadcast status page announcement." : (hostIsolation ? "EMERGENCY SECOPS: Trigger EDR network containment on endpoint, revoke Active Directory session tokens, and preserve memory dump." : "Proceed with standard tier queue resolution within established SLA.")
        }
    };
}

// ==========================================================================
// 3. UI Controller & Event Handlers
// ==========================================================================
document.addEventListener("DOMContentLoaded", () => {
    const ticketForm = document.getElementById("ticketForm");
    const ticketContent = document.getElementById("ticketContent");
    const submitBtn = document.getElementById("submitBtn");
    const clearBtn = document.getElementById("clearBtn");
    const copyCliBtn = document.getElementById("copyCliBtn");
    const emptyState = document.getElementById("emptyState");
    const resultsContainer = document.getElementById("resultsContainer");
    const scenarioChips = document.getElementById("scenarioChips");

    // Quick Scenario Buttons
    scenarioChips.addEventListener("click", (e) => {
        const btn = e.target.closest(".chip-btn");
        if (!btn) return;
        const scenarioKey = btn.getAttribute("data-scenario");
        if (PRESET_SCENARIOS[scenarioKey]) {
            ticketContent.value = PRESET_SCENARIOS[scenarioKey];
            ticketContent.focus();
        }
    });

    // Clear Button
    clearBtn.addEventListener("click", () => {
        ticketContent.value = "";
        ticketContent.focus();
    });

    // Copy CLI Command Button
    copyCliBtn.addEventListener("click", () => {
        const cliText = document.getElementById("cliCommand").innerText;
        if (!cliText || cliText === "N/A") return;

        navigator.clipboard.writeText(cliText).then(() => {
            copyCliBtn.innerHTML = `<span class="copy-icon">✓</span> Copied!`;
            setTimeout(() => {
                copyCliBtn.innerHTML = `<span class="copy-icon">📋</span> Copy Command`;
            }, 2000);
        });
    });

    // Form Submit (Tries Backend first; Falls back seamlessly to In-Browser Engine)
    ticketForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const content = ticketContent.value.trim();
        if (!content) return;

        setLoading(true);

        try {
            let data;
            // Attempt to reach backend (if running python app.py)
            try {
                const response = await fetch("/api/process", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ content: content })
                });
                if (response.ok) {
                    data = await response.json();
                }
            } catch (err) {
                // Backend not available (e.g. on GitHub Pages static host)
                data = null;
            }

            // Fallback to client-side in-browser multi-agent engine
            if (!data) {
                // Simulate slight realistic agent thinking time (300ms)
                await new Promise(r => setTimeout(r, 300));
                data = processTicketInBrowser(content);
            }

            renderDossier(data);
            addToSessionQueue(data);

        } catch (error) {
            console.error("Failed to process ticket:", error);
            // Even if an unexpected error occurs, execute browser engine as safety net
            const fallbackData = processTicketInBrowser(content);
            renderDossier(fallbackData);
            addToSessionQueue(fallbackData);
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        const btnText = submitBtn.querySelector(".btn-text");
        const btnSpinner = submitBtn.querySelector(".btn-spinner");
        if (isLoading) {
            submitBtn.disabled = true;
            btnText.innerText = "Analyzing Multi-Agent Pipeline...";
            btnSpinner.classList.remove("hidden");
        } else {
            submitBtn.disabled = false;
            btnText.innerText = "🚀 Run Multi-Agent Triage";
            btnSpinner.classList.add("hidden");
        }
    }

    // Render Incident Dossier
    function renderDossier(data) {
        emptyState.classList.add("hidden");
        resultsContainer.classList.remove("hidden");

        const t = data.ticket;
        const tr = data.triage;
        const ro = data.routing;
        const re = data.remediation;
        const es = data.escalation;

        // Meta Header
        const metaBadge = document.getElementById("ticketMetaBadge");
        metaBadge.classList.remove("hidden");
        document.getElementById("ticketIdDisplay").innerText = t.id;

        // Metrics Grid
        const recordTypeBadge = document.getElementById("metricRecordType");
        recordTypeBadge.innerText = tr.record_type.toUpperCase();
        recordTypeBadge.className = `metric-value badge ${tr.record_type === 'incident' ? 'badge-p1' : 'badge-p4'}`;

        const priorityBadge = document.getElementById("metricPriority");
        priorityBadge.innerText = tr.priority;
        priorityBadge.className = `metric-value badge ${getPriorityBadgeClass(tr.priority)}`;

        const tierBadge = document.getElementById("metricTier");
        tierBadge.innerText = formatTierName(ro.assigned_tier);
        tierBadge.className = "metric-value badge badge-tier";

        document.getElementById("metricDomain").innerText = tr.domain;

        // SLA Card
        document.getElementById("slaPolicyDesc").innerText = tr.sla.policy_description || "Standard Policy";
        document.getElementById("slaResponseTarget").innerText = `${tr.sla.response_target_minutes} Minutes`;
        document.getElementById("slaResponseDeadline").innerText = tr.sla.response_deadline || "N/A";
        document.getElementById("slaResolutionTarget").innerText = `${tr.sla.resolution_target_hours} Hours`;
        document.getElementById("slaResolutionDeadline").innerText = tr.sla.resolution_deadline || "N/A";

        // Extracted Entities
        const entitiesContainer = document.getElementById("extractedEntities");
        entitiesContainer.innerHTML = "";
        const allEntities = [
            ...(tr.extracted_entities.error_codes || []),
            ...(tr.extracted_entities.hostnames || []),
            ...(tr.extracted_entities.detected_systems || []),
            ...(tr.extracted_entities.security_indicators || [])
        ];

        if (allEntities.length > 0) {
            allEntities.forEach(ent => {
                const tag = document.createElement("span");
                tag.className = "entity-tag";
                tag.innerText = ent;
                entitiesContainer.appendChild(tag);
            });
        } else {
            entitiesContainer.innerHTML = `<span class="detail-text" style="color: var(--text-subtle);">None detected (Standard ticket)</span>`;
        }

        // Routing & Paging
        document.getElementById("dispatchRationale").innerText = ro.routing_rationale;
        const onCallSpan = document.getElementById("onCallPagingStatus");
        if (ro.paging_required) {
            onCallSpan.className = "badge badge-p1";
            onCallSpan.innerText = "🚨 EMERGENCY ON-CALL PAGED";
        } else {
            onCallSpan.className = "badge badge-neutral";
            onCallSpan.innerText = "Standard Queue (No page)";
        }

        // Runbook & CLI
        document.getElementById("kbTitle").innerText = `${re.matched_kb_id}: ${re.matched_kb_title}`;
        document.getElementById("kbId").innerText = re.matched_kb_id;
        document.getElementById("cliCommand").innerText = re.diagnostic_command;

        const sopList = document.getElementById("sopStepsList");
        sopList.innerHTML = "";
        (re.technician_steps || []).forEach(step => {
            const li = document.createElement("li");
            li.innerText = step;
            sopList.appendChild(li);
        });

        // User Response Preview
        document.getElementById("userResponseBody").innerText = re.user_response;

        // Escalation Alert Banner
        const alertBanner = document.getElementById("alertBanner");
        if (es.needs_escalation) {
            alertBanner.classList.remove("hidden");
            if (es.mim_bridge_required) {
                document.getElementById("alertIcon").innerText = "🚨";
                document.getElementById("alertTitle").innerText = "P1 MAJOR INCIDENT MANAGEMENT (MIM) ACTIVE";
                document.getElementById("alertMessage").innerText = "Emergency conference bridge initiated. IT Leadership notified.";
                alertBanner.style.borderColor = "var(--color-p1)";
            } else if (es.host_isolation_required) {
                document.getElementById("alertIcon").innerText = "🛡️";
                document.getElementById("alertTitle").innerText = "SECOPS CONTAINMENT PROTOCOL ACTIVATED";
                document.getElementById("alertMessage").innerText = "Endpoint network isolation commanded to prevent lateral malware spread.";
                alertBanner.style.borderColor = "var(--color-sec)";
            } else {
                document.getElementById("alertIcon").innerText = "⚠️";
                document.getElementById("alertTitle").innerText = `ESCALATION LEVEL ${es.escalation_level}`;
                document.getElementById("alertMessage").innerText = es.escalation_reason;
                alertBanner.style.borderColor = "var(--color-p2)";
            }
        } else {
            alertBanner.classList.add("hidden");
        }
    }

    // Add to Session Queue Table
    function addToSessionQueue(data) {
        sessionTickets.unshift(data);
        const tbody = document.getElementById("queueTableBody");
        const countSpan = document.getElementById("queueCount");

        countSpan.innerText = `${sessionTickets.length} Ticket${sessionTickets.length === 1 ? '' : 's'} Processed`;

        if (sessionTickets.length === 1) {
            tbody.innerHTML = "";
        }

        const t = data.ticket;
        const tr = data.triage;
        const ro = data.routing;
        const re = data.remediation;
        const es = data.escalation;

        const trElem = document.createElement("tr");
        trElem.innerHTML = `
            <td><strong>${t.id}</strong></td>
            <td><span class="badge ${tr.record_type === 'incident' ? 'badge-p1' : 'badge-p4'}">${tr.record_type}</span></td>
            <td><code>${tr.domain}</code></td>
            <td><span class="badge ${getPriorityBadgeClass(tr.priority)}">${tr.priority}</span></td>
            <td><span class="badge badge-tier">${formatTierName(ro.assigned_tier)}</span></td>
            <td><small>${re.matched_kb_id}</small></td>
            <td>${es.needs_escalation ? '<span class="badge badge-p1">ESCALATED</span>' : '<span class="badge badge-neutral">Normal</span>'}</td>
            <td><small style="color: var(--text-subtle);">${new Date().toLocaleTimeString()}</small></td>
        `;

        tbody.prepend(trElem);
    }

    function getPriorityBadgeClass(priority) {
        switch (priority) {
            case "P1_CRITICAL": return "badge-p1";
            case "P2_HIGH": return "badge-p2";
            case "P3_MEDIUM": return "badge-p3";
            case "P4_LOW": return "badge-p4";
            default: return "badge-neutral";
        }
    }

    function formatTierName(tier) {
        const names = {
            "tier_1_service_desk": "Tier 1 Desk",
            "tier_2_desktop_systems": "Tier 2 Desktop",
            "tier_3_infrastructure": "Tier 3 Infra",
            "secops_csirt": "SecOps CSIRT"
        };
        return names[tier] || tier;
    }
});
