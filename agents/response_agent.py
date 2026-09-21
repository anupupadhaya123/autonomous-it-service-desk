"""
IT Runbook & Remediation Agent - Matches tickets against enterprise Knowledge Base (KB)
runbooks, generates exact CLI diagnostic commands, technician troubleshooting steps,
and user-facing self-service instructions.
"""

import json
import os
import yaml
from typing import Dict, Any, List, Optional
from utils.constants import Priority, TicketStatus
from utils.helpers import log_agent_action


class ResponseAgent:
    """
    Agent responsible for matching IT Knowledge Base runbooks and generating
    actionable technical remediation and user communication.
    """
    
    def __init__(self, config_path: str = "config/settings.yaml", prompts_path: str = "config/prompts.yaml"):
        """Initialize with configuration and load knowledge base runbooks"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        with open(prompts_path, 'r') as f:
            self.prompts = yaml.safe_load(f)
            
        kb_rel_path = self.config.get('knowledge_base', {}).get('path', 'data/knowledge_base.json')
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        kb_full_path = os.path.join(base_dir, kb_rel_path)
        
        self.knowledge_base = []
        if os.path.exists(kb_full_path):
            with open(kb_full_path, 'r') as f:
                self.knowledge_base = json.load(f)
    
    def generate_response(self, ticket: Dict[str, Any], triage: Dict[str, Any],
                          routing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate technical runbook remediation and user-facing communications
        
        Args:
            ticket: Original ticket data
            triage: Triage and classification data
            routing: Support tier routing data
            
        Returns:
            Remediation plan with KB match, diagnostic commands, and responses
        """
        log_agent_action("REMEDIATION_AGENT", "Matching Runbook and Generating Remediation", {"ticket_id": ticket['id']})
        
        content = ticket['content']
        domain = triage['domain']
        priority = triage['priority']
        sla = triage.get('sla', {})
        assigned_tier = routing['assigned_tier']
        
        # 1. Match Knowledge Base Runbook
        matched_kb = self._match_runbook(content, domain, ticket.get('entities', {}))
        
        # 2. Extract Diagnostic Commands and Steps
        diagnostic_command = matched_kb.get('diagnostic_command', 'echo "No automated script available"') if matched_kb else "N/A"
        technician_steps = matched_kb.get('troubleshooting_steps', []) if matched_kb else [
            "1. Contact user to gather detailed system logs.",
            "2. Verify network reachability and endpoint compliance.",
            "3. Escalate to senior systems engineer if unresolved within SLA window."
        ]
        
        # 3. Create User-Facing Communication
        user_response = self._create_user_response(ticket, triage, routing, matched_kb)
        
        remediation_data = {
            "ticket_id": ticket['id'],
            "matched_kb_id": matched_kb.get('id', 'KB-GENERIC') if matched_kb else "KB-GENERIC",
            "matched_kb_title": matched_kb.get('title', 'Standard IT Service Desk Triage') if matched_kb else "Standard IT Service Desk Triage",
            "diagnostic_command": diagnostic_command,
            "technician_steps": technician_steps,
            "user_response": user_response,
            "sla_response_deadline": sla.get('response_deadline', 'N/A'),
            "status": TicketStatus.IN_PROGRESS
        }
        
        log_agent_action("REMEDIATION_AGENT", "Remediation Generated", {
            "ticket_id": ticket['id'],
            "kb_id": remediation_data['matched_kb_id']
        })
        
        return remediation_data
    
    def _match_runbook(self, content: str, domain: str, entities: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find the best matching Knowledge Base article based on domain and keywords"""
        content_lower = content.lower()
        error_codes = [e.lower() for e in entities.get('error_codes', [])]
        
        best_match = None
        highest_score = 0
        
        for kb in self.knowledge_base:
            score = 0
            
            # Domain match gives base weight
            if kb.get('domain') == domain:
                score += 3
                
            # Keyword matches
            for kw in kb.get('keywords', []):
                if kw in content_lower:
                    score += 2
                    
            # Error code matches
            for err in error_codes:
                if any(err in kw for kw in kb.get('keywords', [])):
                    score += 5
                    
            if score > highest_score:
                highest_score = score
                best_match = kb
                
        return best_match if highest_score >= 2 else None
    
    def _create_user_response(self, ticket: Dict[str, Any], triage: Dict[str, Any],
                             routing: Dict[str, Any], matched_kb: Optional[Dict[str, Any]]) -> str:
        """Compose professional user-facing response tailored to ITIL priority and tier"""
        priority = triage['priority']
        sla = triage.get('sla', {})
        assigned_tier = routing['assigned_tier']
        
        tier_display = {
            "tier_1_service_desk": "IT Service Desk (Tier 1)",
            "tier_2_desktop_systems": "Desktop & Systems Support (Tier 2)",
            "tier_3_infrastructure": "Infrastructure & Network Operations (Tier 3)",
            "secops_csirt": "SecOps Cyber Security Incident Response Team"
        }.get(assigned_tier, assigned_tier)
        
        # Header
        greeting = "Hello,\n\nThank you for contacting Corporate IT Support."
        
        # Body
        if priority == Priority.P1_CRITICAL:
            body = (
                f"Your ticket has been classified as a **{priority} (Critical Incident)**.\n"
                f"Our {tier_display} has been automatically paged and is actively working on resolution.\n"
                f"Target initial response time: {sla.get('response_target_minutes', 15)} minutes.\n"
                f"Incident bridge updates will be posted to the corporate status portal."
            )
        elif triage['domain'] == "security_incident":
            body = (
                f"Your report has been flagged as a **Security Incident** and transferred to {tier_display}.\n"
                f"**CRITICAL ACTION REQUIRED:** Please disconnect your computer from the network (unplug Ethernet cable and disconnect Wi-Fi) immediately. "
                f"Do not restart or power off your machine. An incident responder will contact you shortly."
            )
        else:
            self_service = matched_kb.get('self_service_instructions', '') if matched_kb else ''
            self_service_text = f"\n\n**Self-Service Troubleshooting Recommendation:**\n{self_service}" if self_service else ""
            
            body = (
                f"Your ticket has been assigned to our **{tier_display}** under priority **{priority}**.\n"
                f"Our target response window is within {sla.get('response_target_minutes', 60)} minutes."
                f"{self_service_text}"
            )
            
        # Footer
        footer = (
            f"\n\nTicket Reference: {ticket['id']}\n"
            f"SLA Target Deadline: {sla.get('response_deadline', 'N/A')}\n"
            "IT Systems & Support Operations"
        )
        
        return f"{greeting}\n\n{body}{footer}"
