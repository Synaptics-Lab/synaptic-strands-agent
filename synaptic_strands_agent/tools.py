"""
Official AWS Strands Agents Tools for SynapticChain
Decorated with `@tool` from the Strands Agents SDK to automate corporate treasury, invoicing, and ISO 20022 wire settlements.
"""

import json
import uuid
import logging
from typing import Dict, Any, Optional, List

from .compat import tool
from .treasury_engine import TreasuryEngine
from .models import Invoice, TreasuryPolicy

logger = logging.getLogger("synaptic_strands.tools")

# Global singleton engine instance for tools
_DEFAULT_ENGINE: Optional[TreasuryEngine] = None

def get_engine() -> TreasuryEngine:
    """Returns or initializes the default TreasuryEngine."""
    global _DEFAULT_ENGINE
    if _DEFAULT_ENGINE is None:
        _DEFAULT_ENGINE = TreasuryEngine()
    return _DEFAULT_ENGINE

def set_engine(engine: TreasuryEngine) -> None:
    """Overrides the global TreasuryEngine instance (e.g. for testing or custom policies)."""
    global _DEFAULT_ENGINE
    _DEFAULT_ENGINE = engine


@tool
def settle_x402_invoice(
    invoice_id: str,
    amount_susd: float,
    vendor_address: str,
    memo: str = "Automated x402 API Settlement"
) -> str:
    """
    Settles an HTTP 402 ('Payment Required') invoice autonomously on SynapticChain Layer-1.
    Routes through a dedicated non-blocking concurrency lane with sub-150ms finality.

    Args:
        invoice_id: Unique invoice identifier (e.g. 'inv_api_scraping_9021').
        amount_susd: Invoice amount in stable units (sUSD).
        vendor_address: Bech32m recipient address of the vendor/API provider.
        memo: Optional transaction memo / purpose.

    Returns:
        JSON string containing the confirmed cryptographic transaction hash, allocated lane, and finality metrics.
    """
    engine = get_engine()

    # Policy Check
    if amount_susd > engine.policy.require_human_approval_above:
        return json.dumps({
            "status": "ESCALATION_REQUIRED",
            "invoice_id": invoice_id,
            "amount_susd": amount_susd,
            "reason": f"Invoice amount exceeds auto-approval threshold (${engine.policy.require_human_approval_above:.2f} sUSD).",
            "requires_human_signature": True
        }, indent=2)

    try:
        receipt = engine.execute_transfer(
            sender=engine.policy.treasury_address,
            recipient=vendor_address,
            amount=amount_susd,
            currency="sUSD",
            memo=f"{memo} | ID:{invoice_id}"
        )
        return json.dumps({
            "status": "SETTLED_CONFIRMED",
            "invoice_id": invoice_id,
            "tx_hash": receipt.tx_hash,
            "allocated_lane": receipt.lane_id,
            "nonce": receipt.nonce,
            "amount_susd": receipt.amount,
            "finality_ms": receipt.finality_ms,
            "block_height": receipt.block_height,
            "recipient": receipt.recipient,
            "protocol": "HTTP_402_M2M_FAST_PATH"
        }, indent=2)
    except Exception as err:
        logger.error(f"Failed to settle x402 invoice {invoice_id}: {err}")
        return json.dumps({
            "status": "FAILED",
            "invoice_id": invoice_id,
            "error": str(err)
        }, indent=2)


@tool
def generate_and_clear_pacs008(
    debtor_name: str,
    debtor_iban: str,
    creditor_name: str,
    creditor_iban: str,
    amount: float,
    currency: str = "sUSD",
    uetr: str = ""
) -> str:
    """
    Generates a canonical ISO 20022 pacs.008.001.08 financial credit transfer XML message
    and immediately clears and settles it on-chain against liquidity vaults.

    Args:
        debtor_name: Originating corporate entity name.
        debtor_iban: Debtor IBAN / account number.
        creditor_name: Beneficiary corporate entity name.
        creditor_iban: Creditor IBAN / account number.
        amount: Settlement payment amount.
        currency: Settlement currency (default: 'sUSD').
        uetr: Unique End-to-End Transaction Reference (UUIDv4). If empty, auto-generated.

    Returns:
        JSON string containing the confirmed ISO 20022 transaction hash, validated XML, and UETR.
    """
    engine = get_engine()
    msg_id = f"MSG_{uuid.uuid4().hex[:12].upper()}"
    uetr_val = uetr if uetr else str(uuid.uuid4())

    xml_payload = engine.generate_iso20022_pacs008_xml(
        msg_id=msg_id,
        uetr=uetr_val,
        debtor_name=debtor_name,
        debtor_iban=debtor_iban,
        creditor_name=creditor_name,
        creditor_iban=creditor_iban,
        amount=amount,
        currency=currency
    )

    is_valid = engine.validate_pacs008_xml(xml_payload)
    if not is_valid:
        return json.dumps({
            "status": "REJECTED_INVALID_XML",
            "error": "Generated ISO 20022 XML failed schema validation."
        }, indent=2)

    try:
        # Counterparty proxy address
        creditor_addr = f"syn1iban_{creditor_iban[:10].lower()}"
        receipt = engine.execute_transfer(
            sender=engine.policy.treasury_address,
            recipient=creditor_addr,
            amount=amount,
            currency=currency,
            memo=f"ISO 20022 pacs.008 | MsgId:{msg_id} | UETR:{uetr_val}",
            uetr=uetr_val
        )

        return json.dumps({
            "status": "CLEARED_AND_SETTLED",
            "iso_standard": "ISO 20022 pacs.008.001.08",
            "msg_id": msg_id,
            "uetr": uetr_val,
            "tx_hash": receipt.tx_hash,
            "amount": amount,
            "currency": currency,
            "debtor": {"name": debtor_name, "iban": debtor_iban},
            "creditor": {"name": creditor_name, "iban": creditor_iban},
            "allocated_lane": receipt.lane_id,
            "finality_ms": receipt.finality_ms,
            "block_height": receipt.block_height,
            "raw_xml_preview": xml_payload[:250] + "... [TRUNCATED]"
        }, indent=2)
    except Exception as err:
        return json.dumps({
            "status": "CLEARING_FAILED",
            "error": str(err)
        }, indent=2)


@tool
def execute_tax_split_payment(
    vendor_address: str,
    gross_amount: float,
    tax_rate_percent: float = 0.50,
    tax_authority_address: str = ""
) -> str:
    """
    Splits an invoice into Net Vendor Payment and Statutory Tax Withholding (e.g. 0.50% TSA),
    executing both atomic disbursements concurrently on Layer-1 with zero manual accounting.

    Args:
        vendor_address: Vendor's receiving address.
        gross_amount: Total gross invoice amount before withholding.
        tax_rate_percent: Statutory withholding percentage (default: 0.50%).
        tax_authority_address: Optional override for government revenue treasury.

    Returns:
        JSON string breakdown of gross, net vendor, tax withheld, and dual on-chain transaction hashes.
    """
    engine = get_engine()
    if tax_authority_address:
        engine.policy.tax_authority_address = tax_authority_address

    try:
        split_receipt = engine.execute_tax_split(
            vendor_address=vendor_address,
            gross_amount=gross_amount,
            tax_rate_percent=tax_rate_percent
        )

        return json.dumps({
            "status": "TAX_SPLIT_EXECUTED",
            "split_id": split_receipt.split_id,
            "gross_amount": split_receipt.gross_amount,
            "net_vendor_payout": split_receipt.net_vendor_amount,
            "tax_withheld": split_receipt.tax_withheld,
            "tax_rate_percent": f"{split_receipt.tax_rate_percent:.2f}%",
            "vendor_address": split_receipt.vendor_address,
            "tax_authority_address": split_receipt.tax_authority_address,
            "vendor_tx_hash": split_receipt.vendor_tx_hash,
            "tax_tx_hash": split_receipt.tax_tx_hash,
            "accounting_compliance": "STATUTORY_WITHHOLDING_AUTOMATED"
        }, indent=2)
    except Exception as err:
        return json.dumps({
            "status": "TAX_SPLIT_FAILED",
            "error": str(err)
        }, indent=2)


@tool
def query_treasury_status(treasury_address: str = "") -> str:
    """
    Queries real-time balance, multi-lane concurrency telemetry, and daily expenditure for corporate treasury.

    Args:
        treasury_address: Optional treasury address to inspect.

    Returns:
        JSON string containing live balance, active lanes, total settled volume, and block height.
    """
    engine = get_engine()
    metrics = engine.get_treasury_metrics()
    return json.dumps(metrics, indent=2)


@tool
def batch_dispatch_invoices(invoices_json: str) -> str:
    """
    Dispatches multiple vendor invoices concurrently across 256 independent execution lanes.
    Completely eliminates the sequential nonce bottlenecks of traditional blockchains.

    Args:
        invoices_json: JSON string representing a list of invoice objects:
            [{"invoice_id": "1", "vendor_address": "syn1...", "amount": 150.0, "currency": "sUSD"}]

    Returns:
        JSON string summarizing all executed transactions, individual hashes, and aggregate throughput.
    """
    engine = get_engine()
    try:
        raw_items = json.loads(invoices_json)
        invoices = [
            Invoice(
                invoice_id=item.get("invoice_id", str(uuid.uuid4())[:8]),
                vendor_name=item.get("vendor_name", "Vendor"),
                vendor_address=item.get("vendor_address", "syn1vendor_api_provider_node"),
                amount=float(item.get("amount", 10.0)),
                currency=item.get("currency", "sUSD")
            )
            for item in raw_items
        ]

        receipts = engine.batch_execute_invoices(invoices)
        total_amount = sum(r.amount for r in receipts)
        lanes_used = len(set(r.lane_id for r in receipts))
        avg_finality = sum(r.finality_ms for r in receipts) / max(len(receipts), 1)

        return json.dumps({
            "status": "BATCH_DISPATCH_COMPLETE",
            "total_invoices_settled": len(receipts),
            "total_volume_settled": round(total_amount, 2),
            "distinct_lanes_utilized": lanes_used,
            "average_finality_ms": round(avg_finality, 2),
            "transactions": [
                {
                    "invoice_id": inv.invoice_id,
                    "tx_hash": r.tx_hash,
                    "lane_id": r.lane_id,
                    "amount": r.amount,
                    "finality_ms": r.finality_ms
                }
                for inv, r in zip(invoices, receipts)
            ]
        }, indent=2)
    except Exception as err:
        return json.dumps({
            "status": "BATCH_FAILED",
            "error": str(err)
        }, indent=2)


@tool
def verify_invoice_policy(amount_susd: float, vendor_address: str) -> str:
    """
    Pre-flight compliance check verifying that an invoice satisfies spending caps and security policies.

    Args:
        amount_susd: Total invoice amount.
        vendor_address: Destination vendor address.

    Returns:
        JSON string with approval status or escalation requirement.
    """
    engine = get_engine()
    policy = engine.policy

    if (policy.current_daily_spend + amount_susd) > policy.daily_spend_limit:
        return json.dumps({
            "status": "BLOCKED_DAILY_LIMIT",
            "amount_susd": amount_susd,
            "current_spend": policy.current_daily_spend,
            "daily_limit": policy.daily_spend_limit,
            "approval_granted": False,
            "reason": "Exceeds 24-hour treasury spending limit."
        }, indent=2)

    if amount_susd > policy.require_human_approval_above:
        return json.dumps({
            "status": "REQUIRE_HUMAN_SIGNATURE",
            "amount_susd": amount_susd,
            "threshold": policy.require_human_approval_above,
            "approval_granted": False,
            "reason": "Transaction amount exceeds automated threshold; CFO cryptographic sign-off required."
        }, indent=2)

    return json.dumps({
        "status": "APPROVED_AUTO_EXECUTION",
        "amount_susd": amount_susd,
        "approval_granted": True,
        "remaining_daily_budget": round(policy.daily_spend_limit - policy.current_daily_spend, 2)
    }, indent=2)
