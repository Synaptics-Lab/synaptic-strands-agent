"""
Synaptic Strands Agent: Autonomous Corporate Treasury & ISO 20022 Clearing
Built with AWS Strands Agents SDK on SynapticChain Layer-1.
"""

from .compat import Agent, tool
from .models import (
    Invoice,
    LineItem,
    Pacs008Message,
    TaxSplitReceipt,
    ExecutionReceipt,
    TreasuryPolicy
)
from .treasury_engine import TreasuryEngine
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
from .agent import create_strands_treasury_agent
from .bedrock import (
    BedrockConverseAgent,
    export_bedrock_action_group_openapi,
    get_bedrock_tools_spec
)

__version__ = "0.1.0"
__author__ = "SynapticChain Core Architecture Team"
__license__ = "MIT"

__all__ = [
    "Agent",
    "tool",
    "create_strands_treasury_agent",
    "BedrockConverseAgent",
    "export_bedrock_action_group_openapi",
    "get_bedrock_tools_spec",
    "TreasuryEngine",
    "Invoice",
    "LineItem",
    "Pacs008Message",
    "TaxSplitReceipt",
    "ExecutionReceipt",
    "TreasuryPolicy",
    "settle_x402_invoice",
    "generate_and_clear_pacs008",
    "execute_tax_split_payment",
    "query_treasury_status",
    "batch_dispatch_invoices",
    "verify_invoice_policy",
    "auto_onboard_agent_tap",
    "get_engine",
    "set_engine"
]

