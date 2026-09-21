"""
Helper utilities for the Autonomous IT Service Desk (ITSM / ITIL v4)
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from .constants import (
    Priority, Impact, Urgency, SLA_TARGETS,
    SECURITY_TRIGGERS, OUTAGE_TRIGGERS, ITILRecordType
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_ticket_id(record_type: str = ITILRecordType.INCIDENT) -> str:
    """Generate unique ITIL ticket ID (e.g. INC-20260921-120530)"""
    prefix = "INC" if record_type == ITILRecordType.INCIDENT else ("REQ" if record_type == ITILRecordType.SERVICE_REQUEST else "CHG")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{prefix}-{timestamp}"


def parse_ticket(ticket_text: str, record_type: str = ITILRecordType.INCIDENT) -> Dict[str, Any]:
    """
    Parse raw ticket text into structured ITIL ticket format with technical entity extraction
    
    Args:
        ticket_text: Raw ticket text from user or monitoring alert
        record_type: Default or detected ITIL record type
        
    Returns:
        Structured ticket dictionary
    """
    now = datetime.now()
    entities = extract_technical_entities(ticket_text)
    
    return {
        "id": generate_ticket_id(record_type),
        "content": ticket_text,
        "created_at": now.isoformat(),
        "entities": entities,
        "is_outage_indicator": len(entities["outage_indicators"]) > 0,
        "is_security_indicator": len(entities["security_indicators"]) > 0
    }


def extract_technical_entities(text: str) -> Dict[str, Any]:
    """
    Extract technical entities such as error codes, hostnames, IP addresses,
    affected software, and security/outage triggers.
    
    Args:
        text: Ticket text
        
    Returns:
        Dictionary of extracted entities
    """
    text_lower = text.lower()
    
    # 1. Error Code Regexes
    # Matches: 0x80070005, 0x000000EF, HTTP 500, 502 Bad Gateway, etc.
    hex_errors = re.findall(r'\b0x[0-9a-fA-F]{4,8}\b', text)
    http_errors = re.findall(r'\b(?:http\s*)?(?:4\d{2}|5\d{2})\b', text, re.IGNORECASE)
    bsod_errors = re.findall(r'\b[A-Z_]{5,30}_(?:DIED|ERROR|FAILED|EXCEPTION|FAULT|VIOLATION)\b', text)
    generic_error_codes = re.findall(r'\b(?:error|code|stop code)\s*[:#-]?\s*([A-Za-z0-9_-]+)', text, re.IGNORECASE)
    stop_words = {"when", "in", "on", "is", "at", "with", "during", "after", "while", "please", "the", "and", "or", "a", "an", "to"}
    cleaned_generic = [c for c in generic_error_codes if c.lower() not in stop_words and len(c) > 2]
    
    combined_errors = list(set(hex_errors + bsod_errors + [f"HTTP {e}" for e in http_errors if e.isdigit()]))
    if not combined_errors and cleaned_generic:
        combined_errors = list(set(cleaned_generic[:3]))

    # 2. IP Addresses & Hostnames / FQDNs
    ipv4_addresses = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', text)
    # Hostnames like srv-app-01, dc-prod-02, ws-laptop-102
    hostnames = re.findall(r'\b(?:srv|dc|ws|vm|db|fw|rt|sw)-[a-zA-Z0-9-]+\b', text, re.IGNORECASE)
    
    # 3. Known Enterprise Systems / Software
    enterprise_systems = [
        "active directory", "azure ad", "entra id", "okta", "mfa", "duo",
        "vpn", "globalprotect", "cisco anyconnect", "openvpn", "wireguard",
        "outlook", "exchange", "office 365", "m365", "microsoft teams", "slack",
        "jira", "servicenow", "confluence", "github", "gitlab", "bitbucket",
        "aws", "azure", "gcp", "kubernetes", "docker", "vmware", "vsphere",
        "windows 11", "windows 10", "macos", "ubuntu", "redhat", "linux",
        "bitlocker", "crowdstrike", "sentinelone", "defender"
    ]
    detected_systems = [sys for sys in enterprise_systems if sys in text_lower]
    
    # 4. Outage and Security Indicators
    found_outage_indicators = [trig for trig in OUTAGE_TRIGGERS if trig in text_lower]
    found_security_indicators = [trig for trig in SECURITY_TRIGGERS if trig in text_lower]
    
    return {
        "error_codes": combined_errors,
        "ip_addresses": ipv4_addresses,
        "hostnames": hostnames,
        "detected_systems": detected_systems,
        "outage_indicators": found_outage_indicators,
        "security_indicators": found_security_indicators,
        "has_attachments_or_logs": bool(re.search(r'\.(?:log|txt|dmp|evtx|pcap|png|jpg)\b', text, re.IGNORECASE))
    }


def calculate_priority(impact: str, urgency: str) -> str:
    """
    Standard ITIL v4 Priority Calculation Matrix (Impact x Urgency)
    
    | Impact \\ Urgency | CRITICAL | HIGH | MEDIUM | LOW |
    |-------------------|----------|------|--------|-----|
    | HIGH (Org-wide)   | P1       | P1   | P2     | P3  |
    | MEDIUM (Dept)     | P2       | P2   | P3     | P4  |
    | LOW (Single user) | P2*      | P3   | P4     | P4  |
    * Low Impact + Critical Urgency = P2 (e.g. Executive / VIP or Mission-Critical single host)
    """
    impact = impact.lower()
    urgency = urgency.lower()
    
    if impact == Impact.HIGH:
        if urgency in [Urgency.CRITICAL, Urgency.HIGH]:
            return Priority.P1_CRITICAL
        elif urgency == Urgency.MEDIUM:
            return Priority.P2_HIGH
        else:
            return Priority.P3_MEDIUM
            
    elif impact == Impact.MEDIUM:
        if urgency in [Urgency.CRITICAL, Urgency.HIGH]:
            return Priority.P2_HIGH
        elif urgency == Urgency.MEDIUM:
            return Priority.P3_MEDIUM
        else:
            return Priority.P4_LOW
            
    else: # Impact.LOW (Single User)
        if urgency == Urgency.CRITICAL:
            return Priority.P2_HIGH
        elif urgency == Urgency.HIGH:
            return Priority.P3_MEDIUM
        else:
            return Priority.P4_LOW


def calculate_sla_deadlines(priority: str, start_time: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Calculate SLA response and resolution targets based on ITIL priority
    
    Args:
        priority: ITIL Priority (P1_CRITICAL to P4_LOW)
        start_time: Ticket creation timestamp
        
    Returns:
        SLA deadlines dictionary
    """
    if not start_time:
        start_time = datetime.now()
        
    sla_info = SLA_TARGETS.get(priority, SLA_TARGETS[Priority.P3_MEDIUM])
    
    response_deadline = start_time + timedelta(minutes=sla_info["response_time_minutes"])
    resolution_deadline = start_time + timedelta(hours=sla_info["resolution_time_hours"])
    
    return {
        "priority": priority,
        "response_target_minutes": sla_info["response_time_minutes"],
        "resolution_target_hours": sla_info["resolution_time_hours"],
        "response_deadline": response_deadline.strftime("%Y-%m-%d %H:%M:%S"),
        "resolution_deadline": resolution_deadline.strftime("%Y-%m-%d %H:%M:%S"),
        "policy_description": sla_info["description"]
    }


def validate_ticket_data(ticket: Dict[str, Any]) -> bool:
    """Validate ITIL ticket structure"""
    required_fields = ["id", "content", "created_at", "entities"]
    return all(field in ticket for field in required_fields)


def log_agent_action(agent_name: str, action: str, details: Dict[str, Any]):
    """Structured logging for multi-agent IT operations"""
    logger.info(f"[{agent_name.upper()}] {action} | {details}")
