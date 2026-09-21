"""
ITIL Triage & Classification Agent - Analyzes IT tickets, classifies record types,
evaluates Impact/Urgency, and assigns ITIL priorities and SLA targets.
"""

import yaml
from typing import Dict, Any, List
from utils.constants import (
    ITILRecordType, TechnicalDomain, Impact, Urgency, Priority, TicketStatus
)
from utils.helpers import (
    calculate_priority, calculate_sla_deadlines, log_agent_action
)


class ClassifierAgent:
    """
    Agent responsible for ITIL ticket triage, domain classification,
    and priority calculation using the ITIL v4 Impact x Urgency matrix.
    """
    
    def __init__(self, config_path: str = "config/settings.yaml", prompts_path: str = "config/prompts.yaml"):
        """Initialize the triage agent with ITIL configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        with open(prompts_path, 'r') as f:
            self.prompts = yaml.safe_load(f)
        
        self.agent_config = self.config['agents']['triage_agent']
    
    def classify_ticket(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform ITIL triage on an IT support ticket
        
        Args:
            ticket: Structured ticket dictionary
            
        Returns:
            ITIL triage and classification results
        """
        log_agent_action("TRIAGE_AGENT", "Starting ITIL Triage", {"ticket_id": ticket['id']})
        
        content = ticket['content']
        entities = ticket.get('entities', {})
        
        # 1. Determine ITIL Record Type (Incident vs Service Request)
        record_type = self._determine_record_type(content, entities)
        
        # 2. Determine Technical Domain
        domain = self._determine_domain(content, entities)
        
        # 3. Determine ITIL Impact and Urgency
        impact = self._determine_impact(content, entities)
        urgency = self._determine_urgency(content, entities, domain)
        
        # 4. Calculate Priority using ITIL Matrix (Impact x Urgency)
        priority = calculate_priority(impact, urgency)
        
        # 5. Compute SLA Target Deadlines
        sla_info = calculate_sla_deadlines(priority)
        
        triage_results = {
            "ticket_id": ticket['id'],
            "record_type": record_type,
            "domain": domain,
            "impact": impact,
            "urgency": urgency,
            "priority": priority,
            "sla": sla_info,
            "extracted_entities": entities,
            "status": TicketStatus.TRIAGED,
            "triage_confidence": 0.94
        }
        
        log_agent_action("TRIAGE_AGENT", "ITIL Triage Complete", {
            "ticket_id": ticket['id'],
            "record_type": record_type,
            "domain": domain,
            "priority": priority
        })
        
        return triage_results
    
    def _determine_record_type(self, content: str, entities: Dict[str, Any]) -> str:
        """Distinguish between ITIL Incident (break/fix) and Service Request"""
        content_lower = content.lower()
        
        # Incident triggers (service disruptions, errors, crashes)
        incident_triggers = [
            "down", "error", "broken", "not working", "crash", "fails",
            "cannot access", "offline", "outage", "slow", "freeze", "bsod",
            "502", "500", "locked out", "bug", "corrupt", "unresponsive"
        ]
        
        # Service request triggers (new provisioning, access, requests)
        request_triggers = [
            "request", "provision", "need access", "new hire", "onboarding",
            "license", "permission", "install", "grant", "order", "setup new"
        ]
        
        # Check if error codes or outage indicators exist -> Incident
        if entities.get('error_codes') or entities.get('outage_indicators') or entities.get('security_indicators'):
            return ITILRecordType.INCIDENT
            
        has_incident = any(trig in content_lower for trig in incident_triggers)
        has_request = any(trig in content_lower for trig in request_triggers)
        
        if has_request and not has_incident:
            return ITILRecordType.SERVICE_REQUEST
            
        return ITILRecordType.INCIDENT
    
    def _determine_domain(self, content: str, entities: Dict[str, Any]) -> str:
        """Classify into technical domain"""
        content_lower = content.lower()
        
        # Security incident check first
        if entities.get('security_indicators') or any(k in content_lower for k in [
            "ransomware", "malware", "virus", "phishing", "compromised", "hacked", "breach"
        ]):
            return TechnicalDomain.SECURITY_INCIDENT
            
        # Identity & Access (IAM)
        if any(k in content_lower for k in [
            "password", "lockout", "locked", "mfa", "okta", "duo", "active directory",
            "login failed", "sso", "entra id", "credentials", "authenticator"
        ]):
            return TechnicalDomain.IDENTITY_ACCESS
            
        # Network & VPN
        if any(k in content_lower for k in [
            "vpn", "globalprotect", "anyconnect", "wi-fi", "wifi", "dns", "dhcp",
            "latency", "packet loss", "core switch", "router", "gateway", "nxdomain", "ping"
        ]):
            return TechnicalDomain.NETWORK_VPN
            
        # Endpoint & Hardware
        if any(k in content_lower for k in [
            "bsod", "blue screen", "laptop", "monitor", "printer", "bitlocker",
            "ram", "ssd", "hardware", "docking station", "screen", "keyboard"
        ]):
            return TechnicalDomain.ENDPOINT_HARDWARE
            
        # Software & Cloud Services
        if any(k in content_lower for k in [
            "outlook", "m365", "teams", "exchange", "aws", "azure", "jira",
            "database", "sql", "server 500", "bad gateway", "docker", "kubernetes"
        ]):
            return TechnicalDomain.SOFTWARE_CLOUD
            
        return TechnicalDomain.GENERAL_IT
    
    def _determine_impact(self, content: str, entities: Dict[str, Any]) -> str:
        """Evaluate business impact based on scope of affected users/systems"""
        content_lower = content.lower()
        
        # High impact indicators (Enterprise-wide / Mission-critical)
        if entities.get('outage_indicators') or any(k in content_lower for k in [
            "all users", "company-wide", "production down", "entire team", "datacenter",
            "everyone", "all employees", "core switch", "domain controller", "revenue"
        ]):
            return Impact.HIGH
            
        # Medium impact indicators (Department / Multiple users)
        if any(k in content_lower for k in [
            "department", "marketing team", "finance team", "sales floor",
            "multiple users", "several people", "branch office", "floor 3"
        ]):
            return Impact.MEDIUM
            
        # Default: Single user affected
        return Impact.LOW
    
    def _determine_urgency(self, content: str, entities: Dict[str, Any], domain: str) -> str:
        """Evaluate business urgency based on operational impediment"""
        content_lower = content.lower()
        
        # Critical Urgency: Active security breach or complete operational halt
        if domain == TechnicalDomain.SECURITY_INCIDENT or any(k in content_lower for k in [
            "completely down", "halted", "emergency", "cannot work", "losing money", "urgent", "critical"
        ]):
            return Urgency.CRITICAL
            
        # High Urgency: Major degradation, no easy workaround
        if any(k in content_lower for k in [
            "blocking", "asap", "deadline", "cannot access", "failing repeatedly", "intermittent drop"
        ]):
            return Urgency.HIGH
            
        # Medium Urgency: Standard issues with potential workarounds
        if any(k in content_lower for k in [
            "inconvenient", "workaround", "slow", "prompting", "trouble"
        ]):
            return Urgency.MEDIUM
            
        return Urgency.LOW
