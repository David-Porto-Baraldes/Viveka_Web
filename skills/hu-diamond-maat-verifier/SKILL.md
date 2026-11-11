---
name: hu-diamond-maat-verifier
description: Verify cryptographic AI governance proofs, Reed-Muller RM(1,3) [8,4,4]_2 Stella Octangula syndrome decoding, Python AST Kintsugi structural invariants, RFC 6962 domain-separated binary Merkle audit trees, Rule 14 PII purification, and W3C VC 2.0 MaatHumanDignityCredential non-coercion receipts (EU AI Act Art. 50 / SB 243) via the Zero-Auth HU-DIAMOND MCP server.
---

# HU-DIAMOND & Ma'at Cryptographic Verifier (`homouniversalis.ai/mcp/diamond`)

Use this skill when auditing AI agent safety, cognitive sovereignty (`Laws L1..L7`), W3C Verifiable Credentials 2.0 (`vc+jwt`), RFC 6962 Certificate Transparency / Merkle inclusion & consistency proofs (`0x00` leaf / `0x01` internal node domain separation), or multi-call Deep Think reasoning budgets.

## Connect via Remote MCP (`Streamable HTTP`, Zero-Auth)

Add `diamond-verifier` to your agent's MCP configuration:

```json
{
  "mcpServers": {
    "diamond-verifier": {
      "url": "https://homouniversalis.ai/mcp/diamond"
    }
  }
}
```

## Available MCP Tools (4 Grade-A Tools)

1. **`verify_diamond_crucible_and_ast`**
   - Executes deterministic verification of the Reed-Muller `RM(1,3)` $[8,4,4]_2$ Stella Octangula code in $\mathbb{Q}^3$, single-fault syndrome correction, and Python AST Kintsugi structural invariants, returning an `ES256` JWS-signed proof verifiable against `https://homouniversalis.ai/.well-known/jwks.json`.
2. **`verify_sovereign_shield_merkle`**
   - Audits candidate text against the **Rule 14 Three-Ring Zero-Knowledge Purifier** (detecting PII, emails, phones, coordinates, and birth dates), checks **Laws `L1..L7` Anti-Coercion invariants**, and computes an **RFC 6962 Binary Merkle Audit Receipt** (`SovereignDignityReceipt` with `c_levels == 1`).
3. **`simulate_diamond_spiral_budget`**
   - Computes exact zero-cost (`0.00 €`) call topology and token/cost budgets for 1 to 4 Spiral Turns (`9, 18, 27, 36` vertex calls + `10` Supreme Tribunal calls = `46` calls) before invoking expensive frontier reasoning models.
4. **`weigh_agent_on_scales_of_maat_w3c_vc`**
   - Evaluates an AI agent manifest or output against the **42 Negative Confessions of Ma'at** (EU AI Act Art. 50 transparency, California SB 243 anti-coercion, zero dark patterns, zero PII harvesting) and issues a cryptographically signed **W3C VC 2.0 `MaatHumanDignityCredential` (`vc+jwt`, `ES256` `kid: maat-vc-es256-2026-1`)**.

## Direct Zero-Auth HTTP Endpoints

```bash
# Live RM(1,3) + AST Kintsugi ES256 Proof
curl -sS "https://homouniversalis.ai/api/sfumato/diamond-verify"

# Live RFC 6962 Signed Tree Head (sth+jwt) & Sovereign Shield Notary
curl -sS "https://homouniversalis.ai/api/sfumato/sovereign-shield"

# Live W3C VC 2.0 Ma'at Human Dignity Credential (vc+jwt)
curl -sS "https://homouniversalis.ai/api/sfumato/maat-verify"
```
