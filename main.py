"""
Autonomous IT Service Desk (AITSD) - Main Application
An AI-Powered Multi-Agent Architecture for Enterprise IT Support & ITIL v4 Incident Management
"""

import sys
import os
from typing import Dict, Any

# Ensure UTF-8 stdout encoding where possible
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure project root is in Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.classifier_agent import ClassifierAgent
from agents.router_agent import RouterAgent
from agents.response_agent import ResponseAgent
from agents.escalation_agent import EscalationAgent
from utils.helpers import parse_ticket, validate_ticket_data
from utils.constants import TicketStatus, Priority


class AutonomousITServiceDesk:
    """
    Main orchestrator for the ITIL v4 multi-agent IT Service Desk system
    """
    
    def __init__(self):
        """Initialize all specialized IT support agents"""
        print("="*80)
        print("INITIALIZING AUTONOMOUS IT SERVICE DESK (AITSD) [ITIL v4]")
        print("="*80)
        
        self.triage_agent = ClassifierAgent()
        self.router_agent = RouterAgent()
        self.remediation_agent = ResponseAgent()
        self.escalation_agent = EscalationAgent()
        
        print("[OK] Triage & Classification Agent: Ready")
        print("[OK] IT Tier Dispatch & Router Agent: Ready")
        print("[OK] Runbook & Remediation Agent: Ready (Knowledge Base loaded)")
        print("[OK] Major Incident & SecOps Escalation Agent: Ready")
        print("="*80 + "\n")
    
    def process_ticket(self, ticket_text: str) -> Dict[str, Any]:
        """
        Process an IT support ticket through the full ITIL multi-agent pipeline
        
        Args:
            ticket_text: Raw ticket description or monitoring alert
            
        Returns:
            Complete ITIL processing results
        """
        # Step 1: Ingest and parse ticket
        ticket = parse_ticket(ticket_text)
        if not validate_ticket_data(ticket):
            raise ValueError("Invalid IT ticket structure")
        
        print("\n" + "="*80)
        print(f"INGESTING NEW IT TICKET: {ticket['id']}")
        print("="*80)
        print(f"Input: \"{ticket['content'][:120]}...\"\n")
        
        # Step 2: ITIL Triage & Priority Matrix
        print("[STEP 1] Triage & Classification Agent analyzing ticket...")
        triage = self.triage_agent.classify_ticket(ticket)
        print(f"  * Record Type:       {triage['record_type'].upper()}")
        print(f"  * Technical Domain:  {triage['domain']}")
        print(f"  * Business Impact:   {triage['impact'].upper()}")
        print(f"  * Business Urgency:  {triage['urgency'].upper()}")
        print(f"  * ITIL Priority:     {triage['priority']}")
        print(f"  * SLA Target:        Response in {triage['sla']['response_target_minutes']}m | Resolution in {triage['sla']['resolution_target_hours']}h")
        if triage['extracted_entities']['error_codes']:
            print(f"  * Extracted Errors:  {', '.join(triage['extracted_entities']['error_codes'])}")
        
        # Step 3: Support Tier Routing & Dispatch
        print("\n[STEP 2] IT Router Agent determining support tier queue...")
        routing = self.router_agent.route_ticket(triage)
        print(f"  * Assigned Tier:     {routing['assigned_tier'].upper()}")
        print(f"  * Secondary Queue:   {routing['secondary_tier']}")
        print(f"  * On-Call Paging:    {'[!] YES (EMERGENCY ON-CALL PAGING)' if routing['paging_required'] else 'No (Standard Queue)'}")
        
        # Step 4: Runbook Matching & Technical Remediation
        print("\n[STEP 3] Remediation Agent querying IT Knowledge Base...")
        remediation = self.remediation_agent.generate_response(ticket, triage, routing)
        print(f"  * Matched Runbook:   [{remediation['matched_kb_id']}] {remediation['matched_kb_title']}")
        print(f"  * Diagnostic CLI:    {remediation['diagnostic_command']}")
        
        # Step 5: Incident Escalation & SecOps Evaluation
        print("\n[STEP 4] Escalation Agent evaluating MIM & Security containment...")
        escalation = self.escalation_agent.evaluate_escalation(ticket, triage, routing)
        print(f"  * Escalation Status: {'[!] ESCALATION TRIGGERED' if escalation['needs_escalation'] else 'Normal Operations'}")
        if escalation['needs_escalation']:
            print(f"  * Escalation Level:  Level {escalation['escalation_level']}")
            print(f"  * Reason:            {escalation['escalation_reason']}")
            if escalation['mim_bridge_required']:
                print("  * MIM Bridge:        [CRITICAL] P1 MAJOR INCIDENT CONFERENCE BRIDGE REQUIRED")
            if escalation['host_isolation_required']:
                print("  * Host Isolation:    [SECOPS] IMMEDIATE NETWORK ISOLATION PROTOCOL ACTIVE")
        
        # Determine final status
        final_status = TicketStatus.ESCALATED if escalation['needs_escalation'] else TicketStatus.IN_PROGRESS
        
        results = {
            "ticket": ticket,
            "triage": triage,
            "routing": routing,
            "remediation": remediation,
            "escalation": escalation,
            "final_status": final_status
        }
        
        return results
    
    def display_ticket_dossier(self, results: Dict[str, Any]):
        """Display complete technical dossier for IT technicians and managers"""
        t = results['ticket']
        tr = results['triage']
        ro = results['routing']
        re = results['remediation']
        es = results['escalation']
        
        print("\n" + "#"*80)
        print(f"IT SERVICE DESK INCIDENT DOSSIER - {t['id']}")
        print("#"*80)
        print(f"Status: [{results['final_status'].upper()}] | Priority: [{tr['priority']}] | SLA Target: [{tr['sla']['response_deadline']}]")
        print(f"Assigned Support Tier: {ro['assigned_tier']}")
        print(f"Record Type: {tr['record_type']} | Domain: {tr['domain']}")
        
        print("\n--- TECHNICIAN TROUBLESHOOTING RUNBOOK ---")
        print(f"Knowledge Base Reference: {re['matched_kb_id']} - {re['matched_kb_title']}")
        print(f"Diagnostic / Remediation Command:\n  $ {re['diagnostic_command']}")
        print("\nStandard Operating Procedure (SOP):")
        for step in re['technician_steps']:
            print(f"  {step}")
            
        print("\n--- RECOMMENDED OPERATIONAL ACTION ---")
        print(f"Action: {es['recommended_action']}")
        
        print("\n--- END-USER COMMUNICATION (AUTOMATED ACKNOWLEDGMENT) ---")
        print("-" * 50)
        print(re['user_response'])
        print("-" * 50)
        print("#"*80 + "\n")


def run_demo():
    """Run demonstration with 5 realistic enterprise IT support scenarios"""
    sample_tickets = [
        {
            "name": "P1 Enterprise Outage: Active Directory Domain Controller Crash",
            "content": "URGENT: Active Directory domain controller dc01.corp.internal is completely unresponsive. Over 400 employees across all departments are locked out and production systems cannot authenticate users. This is a complete company-wide outage!"
        },
        {
            "name": "SecOps Emergency: Suspected Ransomware on Finance Workstation",
            "content": "ALERT: An employee on finance workstation ws-fin-04 opened an email attachment named 'Invoice_March.exe' and now their screen shows a LockBit ransomware note saying all corporate files are encrypted. Bitcoin ransom demanded immediately!"
        },
        {
            "name": "Tier 2 Desktop Support: Windows BSOD Stop Error",
            "content": "My Dell Latitude laptop has blue screened 3 times this morning with stop code 0x000000ef (CRITICAL_PROCESS_DIED). It keeps rebooting into Windows Recovery. Need assistance as I cannot attend client meetings."
        },
        {
            "name": "Tier 1 Helpdesk: GlobalProtect VPN Gateway Failure",
            "content": "Hello IT helpdesk, my GlobalProtect VPN client is failing to connect with 'Gateway not reachable' error when working remotely from home. I have tried restarting my laptop twice."
        },
        {
            "name": "Standard Service Request: New Hire Developer Provisioning",
            "content": "Service request: Please provision new hire laptop and accounts for Alex Rivera (Senior Cloud Engineer) starting next Monday. Needs 32GB MacBook Pro, AWS production IAM access, and GitHub Enterprise organization invite."
        }
    ]
    
    system = AutonomousITServiceDesk()
    
    print("\nStarting automated test run across 5 diverse IT support scenarios...\n")
    
    for i, item in enumerate(sample_tickets, 1):
        print(f"\n{'='*80}")
        print(f"SCENARIO {i}/5: {item['name']}")
        print(f"{'='*80}")
        
        try:
            results = system.process_ticket(item['content'])
            system.display_ticket_dossier(results)
        except Exception as e:
            print(f"Error processing ticket: {str(e)}")
            
        if i < len(sample_tickets) and sys.stdin.isatty():
            input("Press [Enter] to run next scenario...")


def interactive_mode():
    """Interactive CLI mode allowing user to submit custom IT tickets"""
    system = AutonomousITServiceDesk()
    
    print("\n" + "="*80)
    print("AUTONOMOUS IT SERVICE DESK - INTERACTIVE MODE")
    print("Type or paste any IT support ticket below (or type 'exit' to quit):")
    print("="*80 + "\n")
    
    while True:
        try:
            user_input = input("\nEnter IT Ticket Description:\n> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Exiting IT Service Desk. Goodbye!")
                break
                
            results = system.process_ticket(user_input)
            system.display_ticket_dossier(results)
            
        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except Exception as e:
            print(f"Error processing ticket: {e}")


def main():
    """Entry point: Supports demo mode or interactive mode"""
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        # Default run demo, but allow user to pass interactive
        print("Run with '--interactive' to enter custom tickets interactively.\n")
        run_demo()


if __name__ == "__main__":
    main()
