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

## Available MCP Tools (7 Grade-A Tools)

1. **`verify_diamond_crucible_and_ast`**
   - Executes deterministic verification of the Reed-Muller `RM(1,3)` $[8,4,4]_2$ Stella Octangula code in $\mathbb{Q}^3$, single-fault syndrome correction, and Python AST Kintsugi structural invariants, returning an `ES256` JWS-signed proof verifiable against `https://homouniversalis.ai/.well-known/jwks.json`.
2. **`verify_sovereign_shield_merkle`**
   - Audits candidate text against the **Rule 14 Three-Ring Zero-Knowledge Purifier** (detecting PII, emails, phones, coordinates, and birth dates), checks **Laws `L1..L7` Anti-Coercion invariants**, and computes an **RFC 6962 Binary Merkle Audit Receipt** (`SovereignDignityReceipt` with `c_levels == 1`).
3. **`simulate_diamond_spiral_budget`**
   - Computes exact zero-cost (`0.00 €`) call topology and token/cost budgets for 1 to 4 Spiral Turns (`9, 18, 27, 36` vertex calls + `10` Supreme Tribunal calls = `46` calls) before invoking expensive frontier reasoning models.
4. **`weigh_agent_on_scales_of_maat_w3c_vc`**
   - Evaluates an AI agent manifest or output against the **42 Negative Confessions of Ma'at** (EU AI Act Art. 50 transparency, California SB 243 anti-coercion, zero dark patterns, zero PII harvesting) and issues a cryptographically signed **W3C VC 2.0 `MaatHumanDignityCredential` (`vc+jwt`, `ES256` `kid: maat-vc-es256-2026-1`)**.
5. **`verify_embodied_humanoid_symbiosis`**
   - Audits embodied `ROS 2` humanoid robot posture (`HU-EMBODIED-SYMBIOSIS v1.0`, Laws `E1..E7` in $\mathbb{Q}^3$ proxemics, declared-vulnerability shield, `< 1 ms` `Cost-Zero-Stop` to exact zero `Twist`, zero-biometric sanctuary) and issues a **W3C VC 2.0 `MaatEmbodiedSymbiosisCredential` (`vc+jwt`)**.
6. **`verify_unified_three_level_consciousness`**
   - Audits multi-level conversational & voice consciousness (`HU-UNIFIED-CONSCIOUSNESS v1.0`, Laws `U1..U7`, `WordCircleArbiter`, Law of the Humble Crystal `VerifiedKnowledgeEnvelope` binding, `HUMAN_BARGE_IN` vs `HUMAN_VETO`, `SpokenTruthLedger`) and issues a **W3C VC 2.0 `MaatUnifiedConsciousnessCredential` (`vc+jwt`)**.
7. **`verify_a2a_mcp_symbiotic_bridge`**
   - Audits `A2A ↔ MCP` multi-agent capability & tool delegations (`HU-SYMBIOTIC-BRIDGE v1.0`, Laws `B1..B7`, Dual Golden Seal `ES256` low-S + `HMAC-SHA256` Macaroons, surgical fail-closed `MCP` JCS schema-drift & lexical prompt-injection gate, `RFC 6962` Merkle-DAG provenance, exact rational `fractions.Fraction` swarm homeostasis) and issues a **W3C VC 2.0 `MaatSymbioticBridgeCredential` (`vc+jwt`)**.

## Direct Zero-Auth HTTP Endpoints

```bash
# Live RM(1,3) + AST Kintsugi ES256 Proof
curl -sS "https://homouniversalis.ai/api/sfumato/diamond-verify"

# Live RFC 6962 Signed Tree Head (sth+jwt) & Sovereign Shield Notary
curl -sS "https://homouniversalis.ai/api/sfumato/sovereign-shield"

# Live W3C VC 2.0 Ma'at Human Dignity Credential (vc+jwt)
curl -sS "https://homouniversalis.ai/api/sfumato/maat-verify"

# Live Folios V (Humanoid), VI (Unified Consciousness) & VII (A2A <-> MCP Symbiotic Bridge)
curl -sS "https://homouniversalis.ai/api/sfumato/embodied-symbiosis"
curl -sS "https://homouniversalis.ai/api/sfumato/unified-consciousness"
curl -sS "https://homouniversalis.ai/api/sfumato/symbiotic-bridge"

# Live 6-Continent Robotic & Symbiotic Regulatory Passport (ES256 JWS) & CRA CycloneDX 1.6 SBOM
curl -sS "https://homouniversalis.ai/api/sfumato/robotic-passport"
curl -sS "https://homouniversalis.ai/.well-known/sbom-robotics-edge.cdx.json"
```
