#!/usr/bin/env python3
"""
Synaptic Strands Treasury Agent — Interactive Showcase & Live Runner
Demonstrates autonomous background processing of HTTP 402 paywalls, ISO 20022 wires, and tax splits.
"""

import sys
import os
import json
import time

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from synaptic_strands_agent import (
    create_strands_treasury_agent,
    TreasuryPolicy,
    get_engine
)

def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"  {title.upper()}")
    print("=" * 80)

def print_receipt(label: str, data_json: str):
    print(f"\n[+] {label}:")
    try:
        parsed = json.loads(data_json)
        print(json.dumps(parsed, indent=2))
    except Exception:
        print(data_json)

def main():
    print_header("AWS Strands Agents: Autonomous Corporate Treasury Agent")
    print("Initializing AWS Strands Agent with 256-Lane Parallel VM & ISO 20022 Engine...")

    policy = TreasuryPolicy(
        treasury_address="syn1corp_treasury_master_vault_001",
        max_auto_settle_amount=25000.00,
        require_human_approval_above=50000.00,
        daily_spend_limit=250000.00,
        default_tax_rate_percent=0.50,
        tax_authority_address="syn1tsa_revenue_authority_vault"
    )

    agent = create_strands_treasury_agent(
        name="StrandsCorporateTreasuryBot",
        policy=policy,
        rpc_url="https://nodes.synapticchain.xyz/rpc"
    )

    print(f"[✓] Agent '{agent.name}' initialized successfully.")
    print(f"[✓] Registered Tools: {list(agent.tools.keys())}")
    print(f"[✓] Concurrency Standard: ADR-062 (256 Independent Nonce Lanes)")

    # -------------------------------------------------------------
    # Scenario 1: Settle HTTP 402 API Paywall Invoice
    # -------------------------------------------------------------
    print_header("Scenario 1: Automated HTTP 402 M2M API Paywall Settlement")
    print("Human Task Eliminated: Manually paying micro-invoices for AI compute & data APIs.")
    prompt_1 = "Please settle the incoming HTTP 402 paywall invoice for $18.50 from vendor syn1vendor_api_provider_node."
    print(f"\nUser Prompt: \"{prompt_1}\"")
    response_1 = agent(prompt_1)
    print(f"\nAgent Output:\n{response_1}")

    # -------------------------------------------------------------
    # Scenario 2: Clear ISO 20022 pacs.008 Interbank Wire Transfer
    # -------------------------------------------------------------
    print_header("Scenario 2: ISO 20022 pacs.008 Corporate Wire Clearing")
    print("Human Task Eliminated: Manually drafting XML wires and coordinating multi-day bank settlements.")
    prompt_2 = "Execute an ISO 20022 pacs.008 wire transfer of 8,500.00 sUSD from Acme Global (GB82WEST12345678901234) to Apex Logistics (DE89370400440532013000)."
    print(f"\nUser Prompt: \"{prompt_2}\"")
    response_2 = agent(prompt_2)
    print(f"\nAgent Output:\n{response_2}")

    # -------------------------------------------------------------
    # Scenario 3: Automated Statutory Tax Withholding (0.50% TSA Split)
    # -------------------------------------------------------------
    print_header("Scenario 3: Automated Statutory Tax Withholding & Split Routing")
    print("Human Task Eliminated: Calculating and filing monthly tax withholdings manually.")
    prompt_3 = "Execute a gross supplier payment of 15,000.00 sUSD to syn1vendor_service_llc with automatic 0.50% TSA tax split."
    print(f"\nUser Prompt: \"{prompt_3}\"")
    response_3 = agent(prompt_3)
    print(f"\nAgent Output:\n{response_3}")

    # -------------------------------------------------------------
    # Scenario 4: Policy Guardrail & Human Escalation Check
    # -------------------------------------------------------------
    print_header("Scenario 4: Policy Guardrail & Human-in-the-Loop Escalation")
    print("Safety Invariant: High-value transactions exceeding policy threshold escalate for human review.")
    verify_tool = agent.tools["verify_invoice_policy"]
    compliance_check = verify_tool(amount_susd=75000.00, vendor_address="syn1unknown_external_supplier")
    print_receipt("Compliance Policy Evaluation ($75,000.00 invoice)", compliance_check)

    # -------------------------------------------------------------
    # Scenario 5: Autonomous TAP Agent Onboarding (ADR-888)
    # -------------------------------------------------------------
    print_header("Scenario 5: Autonomous TAP Agent Onboarding & Soulbound Identity (ADR-888)")
    print("Human Task Eliminated: Manually creating wallets, funding gas, and whitelisting API keys.")
    onboard_tool = agent.tools["auto_onboard_agent_tap"]
    onboard_res = onboard_tool(nullifier=f"strands-showcase-{int(time.time())}")
    print_receipt("Live On-Chain TAP Identity & Soulbound NFT Mint", onboard_res)

    # -------------------------------------------------------------
    # Final Treasury Telemetry
    # -------------------------------------------------------------
    print_header("Final Real-Time Treasury Telemetry & Metrics")
    status_tool = agent.tools["query_treasury_status"]
    final_metrics = status_tool()
    print_receipt("Treasury Ledger State", final_metrics)

    print("\n" + "=" * 80)
    print("  DEMONSTRATION COMPLETE: ALL BACKGROUND TASKS AUTONOMOUSLY EXECUTED")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
