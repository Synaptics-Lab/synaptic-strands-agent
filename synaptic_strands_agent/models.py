"""
Data Schemas and Domain Models for Synaptic Strands Agent
Provides strongly typed structures for B2B invoices, ISO 20022 messages, and Layer-1 settlement receipts.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import time
import uuid

@dataclass
class LineItem:
    """Individual invoice line item."""
    description: str
    quantity: int
    unit_price: float
    total: float

@dataclass
class Invoice:
    """Incoming B2B / M2M invoice."""
    invoice_id: str
    vendor_name: str
    vendor_address: str
    amount: float
    currency: str = "sUSD"
    due_date: Optional[str] = None
    tax_rate_percent: float = 0.50
    is_x402_paywall: bool = False
    endpoint_url: Optional[str] = None
    line_items: List[LineItem] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Pacs008Message:
    """ISO 20022 pacs.008.001.08 Financial Message Data."""
    msg_id: str
    uetr: str
    debtor_name: str
    debtor_iban: str
    creditor_name: str
    creditor_iban: str
    amount: float
    currency: str
    purpose_code: str
    raw_xml: str
    created_at: float = field(default_factory=time.time)

@dataclass
class TaxSplitReceipt:
    """Statutory tax split and withholding distribution record."""
    split_id: str
    gross_amount: float
    net_vendor_amount: float
    tax_withheld: float
    tax_rate_percent: float
    vendor_address: str
    tax_authority_address: str
    vendor_tx_hash: str
    tax_tx_hash: str
    timestamp: float = field(default_factory=time.time)

@dataclass
class ExecutionReceipt:
    """Layer-1 settlement receipt across 256 parallel lanes."""
    tx_hash: str
    sender: str
    recipient: str
    amount: float
    currency: str
    lane_id: int
    nonce: int
    finality_ms: float
    block_height: int
    status: str
    memo: str
    uetr: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

@dataclass
class TreasuryPolicy:
    """Corporate governance and human-in-the-loop limits."""
    treasury_address: str = "syn1corp_treasury_master_vault_001"
    max_auto_settle_amount: float = 2500.00
    require_human_approval_above: float = 10000.00
    daily_spend_limit: float = 50000.00
    current_daily_spend: float = 0.0
    auto_tax_withholding_enabled: bool = True
    default_tax_rate_percent: float = 0.50
    tax_authority_address: str = "syn1tsa_revenue_authority_vault"
    allowed_currencies: List[str] = field(default_factory=lambda: ["sUSD", "SYN", "cTZS", "cKES", "cNGN", "ZMW"])
