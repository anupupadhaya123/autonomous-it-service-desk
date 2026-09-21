"""
IT Support Tier Dispatcher & Router Agent - Dispatches triaged tickets to appropriate
support tiers (Tier 1 Service Desk, Tier 2 Desktop Systems, Tier 3 Infrastructure, SecOps)
and manages on-call paging requirements.
"""

import yaml
from typing import Dict, Any, List
from utils.constants import (
    TechnicalDomain, SupportTier, Priority, Impact, TicketStatus
)
from utils.helpers import log_agent_action


class RouterAgent:
    """
    Agent responsible for routing IT tickets to the correct support tier
    and evaluating on-call paging triggers.
    """
    
    def __init__(self, config_path: str = "config/settings.yaml", prompts_path: str = "config/prompts.yaml"):
        """Initialize the router agent with tier mapping configurations"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        with open(prompts_path, 'r') as f:
            self.prompts = yaml.safe_load(f)
            
        self.agent_config = self.config['agents']['it_router_agent']
        self.tier_mappings = self.config.get('tier_mappings', {})
        self.sla_targets = self.config.get('sla_targets', {})
    
    def route_ticket(self, triage: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route a triaged IT ticket to the appropriate support tier
        
        Args:
            triage: Triage and classification data from ClassifierAgent
            
        Returns:
            Structured routing decision
        """
        log_agent_action("ROUTER_AGENT", "Evaluating Support Tier Dispatch", {"ticket_id": triage['ticket_id']})
        
        domain = triage['domain']
        priority = triage['priority']
        impact = triage['impact']
        record_type = triage['record_type']
        
        # 1. Determine Assigned Support Tier
        primary_tier, secondary_tier = self._select_tier(domain, priority, impact)
        
        # 2. Check On-Call Paging Trigger (P1 Critical or Active Security Incident)
        paging_required, paging_reason = self._check_on_call_paging(priority, domain)
        
        # 3. Generate Routing Rationale
        rationale = self._generate_rationale(primary_tier, domain, priority, impact)
        
        routing_decision = {
            "ticket_id": triage['ticket_id'],
            "assigned_tier": primary_tier,
            "secondary_tier": secondary_tier,
            "paging_required": paging_required,
            "paging_reason": paging_reason,
            "routing_rationale": rationale,
            "status": TicketStatus.ROUTED,
            "dispatch_confidence": 0.96
        }
        
        log_agent_action("ROUTER_AGENT", "Routing Complete", {
            "ticket_id": triage['ticket_id'],
            "assigned_tier": primary_tier,
            "paging_required": paging_required
        })
        
        return routing_decision
    
    def _select_tier(self, domain: str, priority: str, impact: str) -> tuple:
        """Select primary and secondary support tier based on domain and severity"""
        # Security incidents go directly to SecOps CSIRT
        if domain == TechnicalDomain.SECURITY_INCIDENT:
            return SupportTier.SECOPS_CSIRT, SupportTier.TIER_3_INFRASTRUCTURE
            
        # Enterprise-wide infrastructure/network outages go to Tier 3
        if impact == Impact.HIGH and domain in [TechnicalDomain.NETWORK_VPN, TechnicalDomain.SOFTWARE_CLOUD]:
            return SupportTier.TIER_3_INFRASTRUCTURE, SupportTier.TIER_2_DESKTOP_SYSTEMS
            
        # Hardware, BSOD, and OS level crashes go to Tier 2 Desktop Systems
        if domain == TechnicalDomain.ENDPOINT_HARDWARE:
            return SupportTier.TIER_2_DESKTOP_SYSTEMS, SupportTier.TIER_1_SERVICE_DESK
            
        # Look up default tier mappings from settings
        mapping = self.tier_mappings.get(domain, {
            "primary_tier": SupportTier.TIER_1_SERVICE_DESK,
            "secondary_tier": SupportTier.TIER_2_DESKTOP_SYSTEMS
        })
        
        return mapping.get("primary_tier"), mapping.get("secondary_tier")
    
    def _check_on_call_paging(self, priority: str, domain: str) -> tuple:
        """Determine if an emergency page (PagerDuty/Opsgenie) is required"""
        if priority == Priority.P1_CRITICAL:
            return True, "P1 Critical Outage: Mandatory on-call lead escalation within 15 minutes."
            
        if domain == TechnicalDomain.SECURITY_INCIDENT:
            return True, "Active Security Threat: SecOps incident responder paging activated."
            
        return False, "Standard operational queue; on-call paging not required."
    
    def _generate_rationale(self, tier: str, domain: str, priority: str, impact: str) -> str:
        """Generate technical explanation for the dispatch choice"""
        tier_names = {
            SupportTier.TIER_1_SERVICE_DESK: "Tier 1 Service Desk (First Contact Resolution / Self-Service)",
            SupportTier.TIER_2_DESKTOP_SYSTEMS: "Tier 2 Desktop & Systems (OS / Hardware / Endpoint Troubleshooting)",
            SupportTier.TIER_3_INFRASTRUCTURE: "Tier 3 Infrastructure & Network Operations (Core Systems / Cloud)",
            SupportTier.SECOPS_CSIRT: "SecOps CSIRT (Security Incident Response & Containment)"
        }
        
        return f"Dispatched to {tier_names.get(tier, tier)} based on domain '{domain}' with {priority} priority and {impact} impact."
