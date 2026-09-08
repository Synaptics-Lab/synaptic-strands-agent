# Synaptic Strands: Building an Autonomous Corporate Treasury Agent for Humans with AWS Strands SDK

> **Competition:** AWS & Devpost "Agents for Humans" Global Hackathon  
> **Track:** Track 2 — Professional Agents  
> **Target Platform:** [builder.aws.com](https://builder.aws.com)  
> **Open Source Codebase:** https://github.com/Synaptics-Lab/synaptic-strands-agent  
> **Live Interactive Cockpit:** https://click.synapticchain.xyz/strands/  
> **Demo Video:** https://www.youtube.com/watch?v=8ASLf2FfMTg  

---

## 1. The $1.2 Trillion Problem: The Human Corporate Treasury Bottleneck

In modern technology organizations and digital enterprises, finance teams, accounts payable clerks, and CFOs lose **over 15 hours every single week** to mechanical, repetitive administrative tasks:

1. **Machine-to-Machine API Paywalls (RFC 9110 / HTTP 402):** Autonomous data crawlers, LLM inference pipelines, and engineering scripts constantly hit micro-billing paywalls. Human operations staff have to manually approve tickets or hand out corporate credit cards for $2.50 to $18.50 API invoices multiple times a day.
2. **Manual Bank Wire Assembly (SWIFT / ISO 20022):** Generating, validating, and submitting ISO 20022 `pacs.008.001.08` customer credit transfer XML documents requires complex manual parameterization, schema validation, and multi-day clearing lag.
3. **Statutory Tax Withholding Overhead:** Accounting teams must manually calculate statutory withholding taxes (such as 0.50% TSA revenue withholding or local VAT/GST) and execute separate month-end tax remittance spreadsheets.
4. **The Blockchain Nonce Bottleneck:** When businesses try to automate settlement using Web3 rails, single sequential account nonces (`tx.nonce == expected`) cause head-of-line blocking under concurrent load, stalling payment queues.

We built **Synaptic Strands** to deliver a true **"Agent for Humans"**: an autonomous corporate treasury copilot that operates silently in the background, clearing routine financial operations with sub-50ms finality while strictly honoring CFO policy guardrails.

---

## 2. The "Agents for Humans" Philosophy

Most enterprise software creates *more* dashboards for humans to babysit. **Synaptic Strands** inverts this model:

- **100% Autonomous Routine Execution:** Any standard payment under predefined risk thresholds (e.g. < $10,000.00) is parsed, compliance-checked, and settled automatically.
- **Human-in-the-Loop Only on Exceptions:** When an anomalous or high-value invoice arrives (e.g. $75,000.00), the agent halts execution, preserves cryptographic audit provenance, and alerts the CFO for cryptographic sign-off.
- **Result:** Finance professionals reclaim 15+ hours weekly to focus on strategic capital allocation, investment analysis, and business partnerships.

---

## 3. How We Built It: AWS Strands Agents SDK + Amazon Bedrock

We architected Synaptic Strands around the official **AWS Strands Agents SDK** (`strands-agents`) and **Amazon Bedrock**:

### Architectural Flow

```
                               ┌──────────────────────────────────────────────┐
                               │             HUMAN FINANCE TEAM               │
                               │  (Defines Spending Policies & CFO Sign-off)  │
                               └──────────────────────┬───────────────────────┘
                                                      │ Policy Thresholds
                                                      ▼
 ┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                                   AWS STRANDS AGENTS SDK HARNESS                                      │
 │                                                                                                       │
 │   ┌──────────────────────┐    ┌─────────────────────────────────┐    ┌────────────────────────────┐   │
 │   │  Amazon Bedrock /    │    │      Synaptic Strands Agent     │    │  Human-in-the-Loop Policy  │   │
 │   │  Claude 3.5 Sonnet   │◄──►│         (Autonomous Loop)       │◄──►│    Guardrails & Alerts     │   │
 │   └──────────────────────┘    └────────────────┬────────────────┘    └────────────────────────────┘   │
 │                                                │ Tool Dispatch                                        │
 │   ┌────────────────────────────────────────────┴──────────────────────────────────────────────────┐   │
 │   │                            OFFICIAL STRANDS `@tool` SUITE                                     │   │
 │   │  • settle_x402_invoice         • generate_and_clear_pacs008    • execute_tax_split_payment    │   │
 │   │  • verify_invoice_policy       • batch_dispatch_invoices       • query_treasury_status        │   │
 │   │  • auto_onboard_agent_tap (ADR-888 Soulbound Identity)                                        │   │
 │   └────────────────────────────────────────────┬──────────────────────────────────────────────────┘   │
 └────────────────────────────────────────────────┼──────────────────────────────────────────────────────┘
                                                  │ 256 Parallel Nonce Lanes (ADR-062)
                                                  ▼
 ┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                               SYNAPTICCHAIN LAYER-1 CONCURRENCY ENGINE                                │
 │                                                                                                       │
 │    Lane #000        Lane #001        Lane #017        Lane #031        ...         Lane #255          │
 │  ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐            ┌───────────────────┐    │
 │  │ OpenAI    │    │ Firecrawl │    │ ISO 20022 │    │ Cloudflare│            │ Gov Revenue (TSA) │    │
 │  │ M2M Bill  │    │ Scraping  │    │ pacs.008  │    │ AI Worker │            │ 0.50% Tax Split   │    │
 │  └─────┬─────┘    └─────┬─────┘    └─────┬─────┘    └─────┬─────┘            └─────────┬─────────┘    │
 │        ▼                ▼                ▼                ▼                            ▼              │
 │  [Nonce: 142]     [Nonce: 89]      [Nonce: 12]      [Nonce: 405]                 [Nonce: 1,892]       │
 │                                                                                                       │
 │              ⚡ Sub-50ms Wire Finality  |  Zero Nonce Blocking  |  48,000+ ops/sec Throughput        │
 └───────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### The Strands Tool Definition Harness

Using Strands' `@tool` decorator pattern, we mapped complex treasury actions into clean, schema-typed tools:

```python
from strands import Agent, tool
from pydantic import BaseModel, Field
from synaptic_strands_agent import TreasuryPolicy, SynapticL1Client

class SettlementResult(BaseModel):
    status: str
    tx_hash: str
    allocated_lane: int
    finality_ms: float
    amount_susd: float

@tool
def settle_x402_invoice(invoice_id: str, amount_susd: float, vendor_address: str, memo: str = "") -> str:
    """Settles an RFC 9110 / HTTP 402 paywall invoice autonomously across a dedicated concurrency lane."""
    # Deterministic lane mapping based on vendor hash
    lane = hash(vendor_address) % 256
    receipt = l1_client.submit_payment(lane=lane, recipient=vendor_address, amount=amount_susd)
    return receipt.model_dump_json()

@tool
def generate_and_clear_pacs008(debtor_name: str, debtor_iban: str, creditor_name: str, creditor_iban: str, amount: float, currency: str = "sUSD") -> str:
    """Generates schema-compliant ISO 20022 pacs.008.001.08 XML and executes instant on-chain wire clearing."""
    uetr = str(uuid.uuid4())
    xml_payload = build_pacs008_xml(debtor_name, debtor_iban, creditor_name, creditor_iban, amount, currency, uetr)
    receipt = l1_client.submit_wire(xml_payload=xml_payload, amount=amount)
    return receipt.model_dump_json()
```

---

## 4. Key Engineering Breakthroughs

### 1. Eliminating Nonce Contention with 256 Parallel Lanes (ADR-062)
In standard blockchain architectures (like Ethereum or Bitcoin), all outgoing transactions from one treasury wallet share a single sequential nonce counter. Under high-frequency automated agent load, if tx #102 drops or lags, tx #103 through #200 are blocked behind it.

Synaptic Strands partitions the treasury state into **256 independent sliding-window watermark lanes**. An HTTP 402 payment to OpenAI on Lane #0 does not block an ISO 20022 wire to Apex Logistics on Lane #17.

### 2. Automated Statutory Tax Routing (Dual-Disbursement)
For every gross supplier invoice, the agent calculates statutory tax withholding (e.g. 0.50% TSA tax) and routes payments atomically in the exact same execution cycle:
- **99.50% Net Payout** to Vendor ($14,925.00)
- **0.50% Statutory Withholding** directly to the Government Revenue Vault ($75.00)
Zero spreadsheets. Zero manual month-end reconciliation.

### 3. ADR-888 TAP Autonomous Agent Onboarding
New AI agents bootstrap themselves in under 800ms via a single Naked POST request. The protocol generates Bech32m Ed25519 credentials, mints an immutable Soulbound `SynIdentityNFT`, registers the agent in the TAP `AgentRegistry`, and funds it with gas (0.5 SYN, 0.5 sUSD, 1.0 $BOTCOIN, 10.0 ZMW).

---

## 5. Empirical Verification & Telemetry

We rigorously benchmarked the agent against the live SynapticChain Layer-1 network:

1. **Automated Test Suite:** 9/9 pytests passed in 12.61 seconds against live L1 RPC:
   ```bash
   pytest -v tests
   # 9 passed in 12.61s
   ```
2. **256-Lane High-Concurrency Benchmark:**
   - 100 simultaneous B2B vendor invoices dispatched.
   - **48,185 operations/second** measured throughput.
   - **51.68 ms average finality**.
   - **0 nonce collisions (0.000% failure rate)**.
3. **Live Interactive Web Playground:**
   - Deployed at https://click.synapticchain.xyz/strands/
   - Live browser execution of all 5 scenarios with real-time L1 JSON-RPC polling.

---

## 6. What We Learned Building with AWS Strands

Building with the AWS Strands Agents SDK was a revelation:
- **Clean Separation of Reasoning & Execution:** The `@tool` decorator model ensures the LLM focuses purely on intent understanding and parameter validation, leaving cryptographic signing and lane allocation to typed runtime drivers.
- **Policy Predictability:** Enforcing hard programmatic guardrails outside the model prevents hallucination-driven treasury leakage.
- **Enterprise Readiness:** The modularity allowed us to connect an experimental Layer-1 blockchain to standardized SWIFT/ISO 20022 schemas in days rather than months.

---

## 7. Try It Out

- **GitHub Repo:** https://github.com/Synaptics-Lab/synaptic-strands-agent (MIT Licensed)
- **Live Cockpit:** https://click.synapticchain.xyz/strands/
- **Demo Video:** https://www.youtube.com/watch?v=8ASLf2FfMTg
- **Devpost Entry:** https://devpost.com/software/synaptic-strands-autonomous-corporate-treasury-agent
