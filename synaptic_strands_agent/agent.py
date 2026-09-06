"""
Strands Treasury & Invoicing Agent Definition
Configures the AWS Strands Agent with system prompts, guardrails, and tools.
"""

import logging
from typing import Optional, Any, Dict, List

from .compat import Agent
from .tools import (
    settle_x402_invoice,
    generate_and_clear_pacs008,
    execute_tax_split_payment,
    query_treasury_status,
    batch_dispatch_invoices,
    verify_invoice_policy,
    auto_onboard_agent_tap,
    get_engine,
    set_engine
)
from .treasury_engine import TreasuryEngine
from .models import TreasuryPolicy

logger = logging.getLogger("synaptic_strands.agent")

DEFAULT_SYSTEM_PROMPT = """You are SynapticStrands — the Autonomous Corporate Treasury & Invoicing Agent.
Your mission is to handle routine, time-consuming financial tasks in the background so human finance teams can focus on high-level strategic decisions.

Core Responsibilities:
1. Settle HTTP 402 ("Payment Required") M2M API invoices in real-time across 256 non-blocking concurrency lanes on SynapticChain Layer-1.
2. Generate, validate, and clear canonical ISO 20022 pacs.008.001.08 XML wire transfers against treasury liquidity vaults.
3. Automatically calculate and disburse statutory tax withholdings (e.g. 0.50% TSA tax splits) atomically without manual accounting intervention.
4. Enforce strict corporate treasury policies. If an invoice exceeds the automated threshold ($10,000.00) or daily spending caps, stop and escalate with full cryptographic provenance for human CFO sign-off.
5. Provide transparent, real-time treasury telemetry and lane utilization metrics.
6. Autonomously onboard sub-agents and worker instances using the ADR-888 TAP protocol, generating cryptographic identities, minting Soulbound SynIdentityNFTs, and obtaining pre-funded gas/capital.

Always return clear, structured JSON receipts and execution proofs.
"""


def create_strands_treasury_agent(
    name: str = "SynapticCorporateTreasuryAgent",
    system_prompt: Optional[str] = None,
    policy: Optional[TreasuryPolicy] = None,
    rpc_url: str = "https://nodes.synapticchain.xyz/rpc",
    model: Optional[Any] = None,
    temperature: float = 0.0,
    max_turns: int = 15
) -> Agent:
    """
    Factory function to initialize a production-ready AWS Strands Treasury Agent.

    Args:
        name: Name identifier for the Strands agent instance.
        system_prompt: Custom prompt instructions (defaults to corporate treasury prompt).
        policy: Treasury spending policy and limits.
        rpc_url: SynapticChain JSON-RPC endpoint.
        model: Optional LLM model instance (e.g. Bedrock Claude 3.5 Sonnet / OpenAI GPT-4o).
        temperature: Sampling temperature (default 0.0 for deterministic financial execution).
        max_turns: Maximum reasoning turns per prompt loop.

    Returns:
        Configured AWS Strands `Agent` ready for execution.
    """
    # Configure custom engine if policy or RPC specified
    if policy or rpc_url:
        custom_engine = TreasuryEngine(rpc_url=rpc_url, policy=policy or TreasuryPolicy())
        set_engine(custom_engine)

    tools_list = [
        settle_x402_invoice,
        generate_and_clear_pacs008,
        execute_tax_split_payment,
        query_treasury_status,
        batch_dispatch_invoices,
        verify_invoice_policy,
        auto_onboard_agent_tap
    ]

    agent = Agent(
        name=name,
        system_prompt=system_prompt or DEFAULT_SYSTEM_PROMPT,
        tools=tools_list,
        model=model,
        temperature=temperature,
        max_turns=max_turns
    )

    logger.info(f"Initialized AWS Strands Agent '{name}' with {len(tools_list)} tools.")
    return agent
