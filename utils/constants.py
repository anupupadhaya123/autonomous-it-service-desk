"""
Constants for the Autonomous IT Service Desk (ITSM / ITIL v4)
"""

# ITIL Record Types
class ITILRecordType:
    INCIDENT = "incident"               # Unplanned interruption or reduction in quality of an IT service (Break/Fix)
    SERVICE_REQUEST = "service_request" # Formal request from a user for something to be provided (Access, Hardware, Software)
    CHANGE_REQUEST = "change_request"   # Request to add, modify, or remove anything that could affect IT services
    PROBLEM = "problem"                 # Cause or potential cause of one or more incidents (Root cause analysis)

# Technical Categories / Domains
class TechnicalDomain:
    IDENTITY_ACCESS = "identity_access"       # Active Directory, Okta, SSO, MFA, Password Reset, IAM
    NETWORK_VPN = "network_vpn"               # VPN, Wi-Fi, DNS, DHCP, Firewall, Gateway, Packet Loss
    ENDPOINT_HARDWARE = "endpoint_hardware"   # Workstation, Laptop, BSOD, BitLocker, Peripherals, RAM, SSD
    SOFTWARE_CLOUD = "software_cloud"         # M365, Outlook, SaaS, Azure, AWS, Databases, Applications
    SECURITY_INCIDENT = "security_incident"   # Phishing, Malware, Ransomware, Unauthorized Access, DLP Alert
    GENERAL_IT = "general_it"                 # General IT inquiries, asset tagging, documentation

# ITIL Impact Levels (Scope of damage/affected users)
class Impact:
    HIGH = "high"       # Entire organization or mission-critical service down (Multiple users/departments)
    MEDIUM = "medium"   # Single department, team, or non-critical service impaired
    LOW = "low"         # Single user affected, localized inconvenience

# ITIL Urgency Levels (Time-sensitivity of business need)
class Urgency:
    CRITICAL = "critical" # Business operations halted immediately; no workaround available
    HIGH = "high"         # Business operations significantly degraded; workaround is cumbersome
    MEDIUM = "medium"     # Business operations impaired; viable workaround exists
    LOW = "low"           # Minimal or no impact on current business operations; planned task

# ITIL Priority Levels (Impact x Urgency)
class Priority:
    P1_CRITICAL = "P1_CRITICAL" # Organization-wide / mission critical outage
    P2_HIGH = "P2_HIGH"         # Significant department impact or high-urgency single system
    P3_MEDIUM = "P3_MEDIUM"     # Standard operational issue with existing workaround
    P4_LOW = "P4_LOW"           # Minor request or cosmetic issue

# Service Level Agreement (SLA) Targets
SLA_TARGETS = {
    Priority.P1_CRITICAL: {
        "response_time_minutes": 15,
        "resolution_time_hours": 4,
        "description": "Critical Outage: 15-min response, 4-hour resolution target"
    },
    Priority.P2_HIGH: {
        "response_time_minutes": 60,
        "resolution_time_hours": 8,
        "description": "High Priority: 1-hour response, 8-hour resolution target"
    },
    Priority.P3_MEDIUM: {
        "response_time_minutes": 240,
        "resolution_time_hours": 24,
        "description": "Medium Priority: 4-hour response, 24-hour resolution target"
    },
    Priority.P4_LOW: {
        "response_time_minutes": 480,
        "resolution_time_hours": 72,
        "description": "Low Priority: 8-hour response, 72-hour resolution target"
    }
}

# Support Tiers / Queues
class SupportTier:
    TIER_1_SERVICE_DESK = "tier_1_service_desk"       # First Contact Resolution, Self-Service, Basic Diagnostics
    TIER_2_DESKTOP_SYSTEMS = "tier_2_desktop_systems" # On-site/remote OS troubleshooting, Hardware, Local Admin
    TIER_3_INFRASTRUCTURE = "tier_3_infrastructure"   # Network Engineers, Cloud/DevOps, SysAdmins, DBAs
    SECOPS_CSIRT = "secops_csirt"                     # Security Operations Center, Incident Response Team

# Ticket Lifecyle Status
class TicketStatus:
    NEW = "new"
    TRIAGED = "triaged"
    ROUTED = "routed"
    IN_PROGRESS = "in_progress"
    AWAITING_USER = "awaiting_user"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"

# Agent Types
class AgentType:
    TRIAGE = "triage_agent"
    SLA_PRIORITY = "sla_priority_agent"
    ROUTER = "it_router_agent"
    REMEDIATION = "remediation_agent"
    INCIDENT_ESCALATION = "incident_escalation_agent"

# Security & Escalation Trigger Keywords
SECURITY_TRIGGERS = [
    "ransomware", "malware", "virus", "phishing", "suspicious link", "compromised",
    "unauthorized access", "data breach", "data leak", "credential theft", "lockbit",
    "trojan", "bitcoin ransom", "encrypted files", "hacked", "stolen laptop"
]

OUTAGE_TRIGGERS = [
    "all users", "company-wide", "production down", "entire team", "everyone is locked out",
    "datacenter", "core switch", "domain controller", "active directory down", "exchange down",
    "complete outage", "site down", "erp down", "cannot process orders", "revenue impact"
]
