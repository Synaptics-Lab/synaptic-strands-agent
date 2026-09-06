"""
Unit and Integration Test Suite for Synaptic Strands Agent
Tests tools, 256-lane concurrency, ISO 20022 generation, tax splits, and policy guardrails.
"""

import unittest
import json
import uuid
import os
import sys

# Ensure package is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from synaptic_strands_agent import (
    create_strands_treasury_agent,
    TreasuryEngine,
    TreasuryPolicy,
    Invoice,
    settle_x402_invoice,
    generate_and_clear_pacs008,
    execute_tax_split_payment,
    query_treasury_status,
    batch_dispatch_invoices,
    verify_invoice_policy,
    get_engine,
    set_engine
)


class TestSynapticStrandsAgent(unittest.TestCase):

    def setUp(self):
        self.policy = TreasuryPolicy(
            treasury_address="syn1corp_test_vault_001",
            max_auto_settle_amount=1000.00,
            require_human_approval_above=5000.00,
            daily_spend_limit=50000.00,
            default_tax_rate_percent=0.50,
            tax_authority_address="syn1tsa_revenue_authority_test"
        )
        self.engine = TreasuryEngine(policy=self.policy)
        set_engine(self.engine)
        self.agent = create_strands_treasury_agent(
            name="TestTreasuryAgent",
            policy=self.policy
        )

    def test_01_agent_initialization(self):
        """Verifies that the Strands Agent is correctly instantiated with all tools."""
        self.assertEqual(self.agent.name, "TestTreasuryAgent")
        self.assertIn("settle_x402_invoice", self.agent.tools)
        self.assertIn("generate_and_clear_pacs008", self.agent.tools)
        self.assertIn("execute_tax_split_payment", self.agent.tools)
        self.assertIn("query_treasury_status", self.agent.tools)
        self.assertIn("batch_dispatch_invoices", self.agent.tools)
        self.assertIn("verify_invoice_policy", self.agent.tools)

    def test_02_settle_x402_invoice(self):
        """Tests autonomous settlement of an HTTP 402 micro-payment."""
        res_str = settle_x402_invoice(
            invoice_id="inv_test_402_001",
            amount_susd=25.50,
            vendor_address="syn1vendor_api_provider_node",
            memo="Test Scraping API Fee"
        )
        data = json.loads(res_str)
        self.assertEqual(data["status"], "SETTLED_CONFIRMED")
        self.assertEqual(data["invoice_id"], "inv_test_402_001")
        self.assertTrue(data["tx_hash"].startswith("0x"))
        self.assertTrue(0 <= data["allocated_lane"] < 256)
        self.assertGreater(data["finality_ms"], 0)

    def test_03_generate_and_clear_pacs008(self):
        """Tests ISO 20022 pacs.008 XML creation and on-chain clearing."""
        uetr = str(uuid.uuid4())
        res_str = generate_and_clear_pacs008(
            debtor_name="Acme Corp",
            debtor_iban="GB82WEST12345678901234",
            creditor_name="Supplier LLC",
            creditor_iban="DE89370400440532013000",
            amount=1500.00,
            currency="sUSD",
            uetr=uetr
        )
        data = json.loads(res_str)
        self.assertEqual(data["status"], "CLEARED_AND_SETTLED")
        self.assertEqual(data["uetr"], uetr)
        self.assertEqual(data["iso_standard"], "ISO 20022 pacs.008.001.08")
        self.assertTrue(data["tx_hash"].startswith("0x"))

    def test_04_execute_tax_split_payment(self):
        """Tests automated statutory tax withholding (0.50% TSA split)."""
        gross = 10000.00
        res_str = execute_tax_split_payment(
            vendor_address="syn1vendor_service_llc",
            gross_amount=gross,
            tax_rate_percent=0.50
        )
        data = json.loads(res_str)
        self.assertEqual(data["status"], "TAX_SPLIT_EXECUTED")
        self.assertEqual(data["gross_amount"], 10000.00)
        self.assertEqual(data["net_vendor_payout"], 9950.00)
        self.assertEqual(data["tax_withheld"], 50.00)
        self.assertTrue(data["vendor_tx_hash"].startswith("0x"))
        self.assertTrue(data["tax_tx_hash"].startswith("0x"))

    def test_05_policy_guardrails(self):
        """Tests compliance rules and human escalation thresholds."""
        # Under threshold -> Approved
        res_approved = json.loads(verify_invoice_policy(amount_susd=500.00, vendor_address="syn1vendor"))
        self.assertTrue(res_approved["approval_granted"])
        self.assertEqual(res_approved["status"], "APPROVED_AUTO_EXECUTION")

        # Over threshold -> Human signature required
        res_escalated = json.loads(verify_invoice_policy(amount_susd=7500.00, vendor_address="syn1vendor"))
        self.assertFalse(res_escalated["approval_granted"])
        self.assertEqual(res_escalated["status"], "REQUIRE_HUMAN_SIGNATURE")

    def test_06_batch_dispatch_concurrency(self):
        """Tests concurrent batch invoice execution across multiple lanes."""
        invoices = [
            {"invoice_id": f"inv_{i}", "vendor_address": f"syn1vendor_{i}", "amount": 10.0 + i}
            for i in range(10)
        ]
        res_str = batch_dispatch_invoices(json.dumps(invoices))
        data = json.loads(res_str)
        self.assertEqual(data["status"], "BATCH_DISPATCH_COMPLETE")
        self.assertEqual(data["total_invoices_settled"], 10)
        self.assertGreater(data["distinct_lanes_utilized"], 1)

    def test_07_agent_prompt_execution(self):
        """Tests full agent prompt routing for x402 invoice resolution."""
        prompt = "Please settle HTTP 402 invoice for $12.50 from vendor syn1vendor_api_provider_node."
        response = self.agent(prompt)
        self.assertIn("SETTLED_CONFIRMED", response)
        self.assertIn("0x", response)

    def test_08_live_l1_rpc_connectivity(self):
        """Tests real-time JSON-RPC connectivity against SynapticChain Layer-1 node."""
        l1_info = self.engine.sync_l1_state()
        self.assertTrue(l1_info["connected"], "Should successfully connect to SynapticChain L1 RPC")
        self.assertGreater(l1_info["canonical_height"], 13000, "Live checkpoint height should exceed #13,000")
        self.assertIn("SCBFT", l1_info["consensus"], "Consensus should be verified as SCBFT DAG-Primary")
        
        # Verify live on-chain balance query
        treasury_addr = "syn1y7qf8tfthtgz0rpn9s574wdwc5y2s8xa5tv47r"
        onchain_bal = self.engine.query_onchain_balance(treasury_addr)
        self.assertIsNotNone(onchain_bal, "On-chain balance query should succeed")
        self.assertGreater(onchain_bal, 90000.0, "Treasury should have verified real on-chain balance (>90,000 SYN)")


if __name__ == "__main__":
    unittest.main()

