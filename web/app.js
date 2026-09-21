/**
 * Autonomous IT Service Desk (AITSD) - Frontend Controller
 */

// Enterprise Scenario Presets
const PRESET_SCENARIOS = {
    p1: "URGENT: Active Directory domain controller dc01.corp.internal is completely unresponsive. Over 400 employees across all departments are locked out and production systems cannot authenticate users. This is a complete company-wide outage!",
    ransomware: "ALERT: An employee on finance workstation ws-fin-04 opened an email attachment named 'Invoice_March.exe' and now their screen shows a LockBit ransomware note saying all corporate files are encrypted. Bitcoin ransom demanded immediately!",
    bsod: "My Dell Latitude laptop has blue screened 3 times this morning with stop code 0x000000ef (CRITICAL_PROCESS_DIED). It keeps rebooting into Windows Recovery. Need assistance as I cannot attend client meetings.",
    vpn: "Hello IT helpdesk, my GlobalProtect VPN client is failing to connect with 'Gateway not reachable' error when working remotely from home. I have tried restarting my laptop twice.",
    provisioning: "Service request: Please provision new hire laptop and accounts for Alex Rivera (Senior Cloud Engineer) starting next Monday. Needs 32GB MacBook Pro, AWS production IAM access, and GitHub Enterprise organization invite."
};

let sessionTickets = [];

document.addEventListener("DOMContentLoaded", () => {
    const ticketForm = document.getElementById("ticketForm");
    const ticketContent = document.getElementById("ticketContent");
    const submitBtn = document.getElementById("submitBtn");
    const clearBtn = document.getElementById("clearBtn");
    const copyCliBtn = document.getElementById("copyCliBtn");
    const emptyState = document.getElementById("emptyState");
    const resultsContainer = document.getElementById("resultsContainer");
    const scenarioChips = document.getElementById("scenarioChips");

    // 1. Setup Quick Scenario Buttons
    scenarioChips.addEventListener("click", (e) => {
        const btn = e.target.closest(".chip-btn");
        if (!btn) return;
        const scenarioKey = btn.getAttribute("data-scenario");
        if (PRESET_SCENARIOS[scenarioKey]) {
            ticketContent.value = PRESET_SCENARIOS[scenarioKey];
            ticketContent.focus();
        }
    });

    // 2. Clear Button
    clearBtn.addEventListener("click", () => {
        ticketContent.value = "";
        ticketContent.focus();
    });

    // 3. Copy CLI Command Button
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

    // 4. Form Submit & Process
    ticketForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const content = ticketContent.value.trim();
        if (!content) return;

        // UI Loading State
        setLoading(true);

        try {
            const response = await fetch("/api/process", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ content: content })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            renderDossier(data);
            addToSessionQueue(data);

        } catch (error) {
            console.error("Failed to process ticket:", error);
            alert("Error communicating with IT Service Desk backend. Ensure app.py is running.");
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

    // 5. Render Incident Dossier
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

    // 6. Add to Session Queue Table
    function addToSessionQueue(data) {
        sessionTickets.unshift(data);
        const tbody = document.getElementById("queueTableBody");
        const countSpan = document.getElementById("queueCount");

        countSpan.innerText = `${sessionTickets.length} Ticket${sessionTickets.length === 1 ? '' : 's'} Processed`;

        // Clear empty placeholder
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
