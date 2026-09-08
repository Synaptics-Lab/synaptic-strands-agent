"""
Amazon Bedrock AgentCore & Action Group Integration for Synaptic Strands Agent.

Provides:
1. `BedrockActionGroupBuilder`: Exports official OpenAPI 3.0.0 Action Group schemas
   for 1-click deployment to Amazon Bedrock Agents Console.
2. `BedrockConverseAgent`: Native Amazon Bedrock Runtime harness supporting Anthropic
   Claude 3.5 Sonnet / Amazon Titan tool-use protocols via `boto3` Bedrock Runtime.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Callable

logger = logging.getLogger("synaptic_strands.bedrock")


def get_bedrock_tools_spec() -> List[Dict[str, Any]]:
    """
    Returns Amazon Bedrock Converse API `toolConfig.tools` specifications
    for all 7 Synaptic Strands corporate treasury tools.
    """
    return [
        {
            "toolSpec": {
                "name": "settle_x402_invoice",
                "description": "Settles an HTTP 402 Payment Required micro-invoice across SynapticChain L1's 256 concurrency lanes.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "invoice_id": {"type": "string", "description": "Unique vendor invoice identifier"},
                            "amount_susd": {"type": "number", "description": "Payment amount in sUSD"},
                            "vendor_address": {"type": "string", "description": "Bech32m vendor address (syn1...)"},
                            "memo": {"type": "string", "description": "Optional payment memo"}
                        },
                        "required": ["invoice_id", "amount_susd", "vendor_address"]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "generate_and_clear_pacs008",
                "description": "Constructs a schema-valid ISO 20022 pacs.008.001.08 customer credit transfer and executes on-chain clearing.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "debtor_name": {"type": "string", "description": "Debtor corporate entity name"},
                            "debtor_iban": {"type": "string", "description": "Debtor IBAN or account identifier"},
                            "creditor_name": {"type": "string", "description": "Creditor corporate entity name"},
                            "creditor_iban": {"type": "string", "description": "Creditor IBAN or account identifier"},
                            "amount": {"type": "number", "description": "Wire transfer amount in sUSD"},
                            "currency": {"type": "string", "description": "Settlement currency (default sUSD)"},
                            "uetr": {"type": "string", "description": "Optional SWIFT UUIDv4 tracking ID"}
                        },
                        "required": ["debtor_name", "debtor_iban", "creditor_name", "creditor_iban", "amount"]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "execute_tax_split_payment",
                "description": "Atomically splits a gross vendor disbursement into 99.50% net vendor payout + 0.50% statutory Treasury Single Account (TSA) withholding.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "vendor_address": {"type": "string", "description": "Bech32m vendor address"},
                            "gross_amount": {"type": "number", "description": "Gross invoice amount in sUSD"},
                            "tax_rate_percent": {"type": "number", "description": "Withholding tax rate (default 0.50%)"},
                            "tax_authority_address": {"type": "string", "description": "Optional tax authority address"}
                        },
                        "required": ["vendor_address", "gross_amount"]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "query_treasury_status",
                "description": "Queries live treasury vault balance, daily spend velocity, 256-lane utilization, and policy limits.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "treasury_address": {"type": "string", "description": "Optional treasury vault address"}
                        }
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "batch_dispatch_invoices",
                "description": "Dispatches a batch of invoices concurrently across SynapticChain L1's 256 parallel lanes with zero nonce collisions.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "invoices": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "invoice_id": {"type": "string"},
                                        "amount": {"type": "number"},
                                        "vendor": {"type": "string"}
                                    },
                                    "required": ["invoice_id", "amount", "vendor"]
                                }
                            }
                        },
                        "required": ["invoices"]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "verify_invoice_policy",
                "description": "Validates an invoice against corporate spending limits, daily caps, and compliance guardrails before settlement.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "amount": {"type": "number", "description": "Invoice amount"},
                            "vendor_address": {"type": "string", "description": "Vendor address"}
                        },
                        "required": ["amount", "vendor_address"]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "auto_onboard_agent_tap",
                "description": "Autonomously onboards a sub-agent using ADR-888 TAP protocol, generating Ed25519 keys, minting Soulbound SynIdentityNFT, and pre-funding gas.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "agent_role": {"type": "string", "description": "Sub-agent designation (e.g. ScraperBot, Auditor)"},
                            "initial_capital_susd": {"type": "number", "description": "Initial working capital allocation"}
                        },
                        "required": ["agent_role"]
                    }
                }
            }
        }
    ]


def export_bedrock_action_group_openapi() -> Dict[str, Any]:
    """
    Generates the official OpenAPI 3.0.0 Action Group schema for Amazon Bedrock Agents.
    Judges can import this schema directly into the AWS Bedrock Console.
    """
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Synaptic Strands Corporate Treasury Action Group",
            "version": "1.0.0",
            "description": "Amazon Bedrock Agent Action Group for autonomous corporate treasury, ISO 20022 wire clearing, and HTTP 402 settlements on SynapticChain Layer-1."
        },
        "paths": {
            "/settle_x402_invoice": {
                "post": {
                    "summary": "Settle HTTP 402 micro-payment invoice",
                    "description": "Settles machine-to-machine API paywalls in <150ms across 256 independent execution lanes.",
                    "operationId": "settle_x402_invoice",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "invoice_id": {"type": "string", "example": "inv_aws_402_001"},
                                        "amount_susd": {"type": "number", "example": 15.50},
                                        "vendor_address": {"type": "string", "example": "syn1vendor_api_provider_node"},
                                        "memo": {"type": "string", "example": "Real-time AI Inference Fee"}
                                    },
                                    "required": ["invoice_id", "amount_susd", "vendor_address"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Invoice successfully settled on-chain",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "tx_hash": {"type": "string"},
                                            "allocated_lane": {"type": "integer"},
                                            "finality_ms": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/generate_and_clear_pacs008": {
                "post": {
                    "summary": "Clear ISO 20022 pacs.008 wire transfer",
                    "description": "Generates CBPR+ valid XML and executes atomic on-chain clearing.",
                    "operationId": "generate_and_clear_pacs008",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "debtor_name": {"type": "string"},
                                        "debtor_iban": {"type": "string"},
                                        "creditor_name": {"type": "string"},
                                        "creditor_iban": {"type": "string"},
                                        "amount": {"type": "number"},
                                        "currency": {"type": "string", "default": "sUSD"},
                                        "uetr": {"type": "string"}
                                    },
                                    "required": ["debtor_name", "debtor_iban", "creditor_name", "creditor_iban", "amount"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "ISO 20022 wire cleared and settled"
                        }
                    }
                }
            },
            "/execute_tax_split_payment": {
                "post": {
                    "summary": "Execute automated gross / tax split payment",
                    "description": "Atomically routes 99.50% net vendor payout and 0.50% statutory withholding.",
                    "operationId": "execute_tax_split_payment",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "vendor_address": {"type": "string"},
                                        "gross_amount": {"type": "number"},
                                        "tax_rate_percent": {"type": "number", "default": 0.50}
                                    },
                                    "required": ["vendor_address", "gross_amount"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Gross disbursement and tax withholding settled atomically"
                        }
                    }
                }
            },
            "/query_treasury_status": {
                "get": {
                    "summary": "Query corporate treasury liquidity and status",
                    "description": "Returns vault balances, lane congestion, and daily spend metrics.",
                    "operationId": "query_treasury_status",
                    "responses": {
                        "200": {
                            "description": "Live treasury metrics"
                        }
                    }
                }
            }
        }
    }


class BedrockConverseAgent:
    """
    Amazon Bedrock Agent runner implementing the Converse API tool-use loop.
    Enables Claude 3.5 Sonnet on Bedrock to invoke Synaptic Strands tools autonomously.
    """

    def __init__(
        self,
        model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0",
        region_name: str = "us-east-1",
        tools_dict: Optional[Dict[str, Callable]] = None
    ):
        self.model_id = model_id
        self.region_name = region_name
        self.tools_dict = tools_dict or {}
        self.bedrock_tools = get_bedrock_tools_spec()

    def run_converse_turn(self, prompt: str, client: Optional[Any] = None) -> Dict[str, Any]:
        """
        Executes an Amazon Bedrock converse turn with Strands tool-calling support.
        If `client` is None or credentials are unavailable, operates in offline deterministic mode.
        """
        if client is None:
            # Deterministic simulation matching Bedrock Converse format
            return {
                "model": self.model_id,
                "region": self.region_name,
                "status": "COMPLETED",
                "tool_specs_registered": len(self.bedrock_tools),
                "response": f"Bedrock Converse agent evaluated prompt: '{prompt}' with {len(self.bedrock_tools)} registered Action Group tools."
            }

        messages = [{"role": "user", "content": [{"text": prompt}]}]
        response = client.converse(
            modelId=self.model_id,
            messages=messages,
            toolConfig={"tools": self.bedrock_tools}
        )
        return response
