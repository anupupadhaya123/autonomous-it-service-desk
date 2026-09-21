"""
Incident Escalation & SecOps Agent - Evaluates tickets for Major Incident Management (MIM),
P1 critical bridge triggers, SecOps emergency containment protocols, and SLA breach risks.
"""

import yaml
from typing import Dict, Any, Tuple
from utils.constants import Priority, TechnicalDomain, SupportTier, TicketStatus
from utils.helpers import log_agent_action


class EscalationAgent:
    """
    Agent responsible for detecting critical incidents requiring Major Incident Management (MIM)
    or immediate SecOps containment workflows.
    """
    
    def __init__(self, config_path: str = "config/settings.yaml", prompts_path: str = "config/prompts.yaml"):
        """Initialize escalation agent with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        with open(prompts_path, 'r') as f:
            self.prompts = yaml.safe_load(f)
            
        self.agent_config = self.config['agents']['incident_escalation_agent']
    
    def evaluate_escalation(self, ticket: Dict[str, Any], triage: Dict[str, Any],
                            routing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate if ticket requires immediate MIM bridge or SecOps escalation
        
        Args:
            ticket: Original ticket data
            triage: Triage and classification data
            routing: Support tier routing data
            
        Returns:
            Structured escalation evaluation
        """
        log_agent_action("ESCALATION_AGENT", "Evaluating Incident Escalation & MIM Criteria", {"ticket_id": ticket['id']})
        
        priority = triage['priority']
        domain = triage['domain']
        entities = ticket.get('entities', {})
        
        # 1. Check escalation criteria
        needs_escalation, reason, mim_bridge_required, host_isolation_required = self._check_criteria(
            priority, domain, entities
        )
        
        # 2. Determine escalation level (1 to 3)
        escalation_level = self._determine_escalation_level(priority, domain)
        
        # 3. Formulate recommended action
        recommended_action = self._determine_action(
            needs_escalation, escalation_level, mim_bridge_required, host_isolation_required
        )
        
        escalation_data = {
            "ticket_id": ticket['id'],
            "needs_escalation": needs_escalation,
            "escalation_level": escalation_level,
            "escalation_reason": reason,
            "mim_bridge_required": mim_bridge_required,
            "host_isolation_required": host_isolation_required,
            "recommended_action": recommended_action,
            "status": TicketStatus.ESCALATED if needs_escalation else TicketStatus.IN_PROGRESS
        }
        
        log_agent_action("ESCALATION_AGENT", "Escalation Evaluation Complete", {
            "ticket_id": ticket['id'],
            "needs_escalation": needs_escalation,
            "level": escalation_level
        })
        
        return escalation_data
    
    def _check_criteria(self, priority: str, domain: str, entities: Dict[str, Any]) -> Tuple[bool, str, bool, bool]:
        """Evaluate MIM and SecOps criteria"""
        # Security Incident
        if domain == TechnicalDomain.SECURITY_INCIDENT or entities.get('security_indicators'):
            indicators = ", ".join(entities.get('security_indicators', ['malware/threat']))
            return True, f"Active Security Threat Detected: {indicators}", False, True
            
        # P1 Critical Outage -> MIM Bridge
        if priority == Priority.P1_CRITICAL:
            return True, "P1 Mission-Critical Service Outage affecting enterprise operations.", True, False
            
        # P2 High Priority with Outage Indicators
        if priority == Priority.P2_HIGH and entities.get('outage_indicators'):
            return True, "P2 High Priority incident impacting critical department services.", False, False
            
        return False, "Standard operational parameters maintained.", False, False
    
    def _determine_escalation_level(self, priority: str, domain: str) -> int:
        """
        Determine escalation level:
        Level 3: Major Incident (P1) or Active Security Breach (SecOps)
        Level 2: High Priority (P2) or Department Outage
        Level 1: Standard Operational Ticket
        """
        if priority == Priority.P1_CRITICAL or domain == TechnicalDomain.SECURITY_INCIDENT:
            return 3
        elif priority == Priority.P2_HIGH:
            return 2
        return 1
    
    def _determine_action(self, needs_escalation: bool, level: int,
                          mim_required: bool, isolation_required: bool) -> str:
        """Formulate operational instructions for incident managers and technicians"""
        if not needs_escalation:
            return "Proceed with standard tier queue resolution within established SLA."
            
        if level == 3 and mim_required:
            return "CRITICAL MIM: Open emergency incident conference bridge, alert IT Leadership, and broadcast status page announcement."
            
        if level == 3 and isolation_required:
            return "EMERGENCY SECOPS: Trigger EDR network containment on endpoint, revoke Active Directory session tokens, and preserve memory dump."
            
        if level == 2:
            return "ESCALATION: Notify Support Tier Team Lead and assign dedicated senior engineer."
            
        return "Monitor ticket SLA progress."
