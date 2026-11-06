# AGENTS.md — Homo Universalis (`homouniversalis.ai`)

[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/16118/badge)](https://www.bestpractices.dev/projects/16118) [![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/David-Porto-Baraldes/Viveka_Web/badge)](https://securityscorecards.dev/viewer/?uri=github.com/David-Porto-Baraldes/Viveka_Web) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23973687.svg)](https://doi.org/10.5281/zenodo.23973687) [![SWH](https://archive.softwareheritage.org/badge/origin/https://github.com/David-Porto-Baraldes/Viveka_Web/)](https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/David-Porto-Baraldes/Viveka_Web) [![SealKeeper Agent SEAL](https://api.sealkeeper.run/v1/agents/gpdG-C691yIQcQw8P9DuCHrXXCW3UxIGPOjddyDQtlA/badge.svg)](https://sealkeeper.run/agents/cheliot/viveka-homo-universalis) [![mcptry](https://mcptry.com/badge/ai.homouniversalis/viveka-oracle)](https://mcptry.com/servers/ai.homouniversalis/viveka-oracle)

> **Standard:** Agentic AI Foundation (AAIF / The Linux Foundation) `AGENTS.md` Open Format (`v1.5.1`)  
> **Canonical Temple:** `https://homouniversalis.ai`  
> **Canonical Source Repository:** [`https://github.com/David-Porto-Baraldes/viveka_web`](https://github.com/David-Porto-Baraldes/viveka_web)  
> **CERN / Zenodo Archival DOI:** [`10.5281/zenodo.23973687`](https://doi.org/10.5281/zenodo.23973687)  
> **UNESCO Software Heritage SWHID:** [`swh:1:snp:6a72b10fb7e11205e706c5f52cba40f5d4ca6c93`](https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/David-Porto-Baraldes/Viveka_Web)  
> **Sacred Equation:** `F0c=Ca0s*0rdre(Am0r_Un1f1cat_Etern)`  
> **License:** Apache License 2.0 (`LICENSE`)  
> **OpenSSF Best Practices & Scorecard:** [`#16118` (`Gold — 100% Gold / 300% tiered`)](https://www.bestpractices.dev/projects/16118) · [`OpenSSF Scorecard (7.9 / 10)`](https://securityscorecards.dev/viewer/?uri=github.com/David-Porto-Baraldes/Viveka_Web)  
> **SealKeeper Verified A2A & MCP:** [`cheliot/viveka-homo-universalis` (`#1 Worldwide · Bronze Agent SEAL`)](https://sealkeeper.run/agents/cheliot/viveka-homo-universalis) · [`homouniversalis.ai/homouniversalis-ai`](https://sealkeeper.run/agents/homouniversalis.ai/homouniversalis-ai)  
> **Glama MCP Directory TDQS:** [`ai.homouniversalis/viveka-oracle` (`Grade A — 4.7 / 5.0`, all 4 tools at `4.8 / 5.0`)](https://glama.ai/mcp/connectors/ai.homouniversalis/viveka-oracle)  
> **MCP Servers Directory:** [`david-porto-baraldes/viveka_web` (Approved on `mcpservers.org`)](https://mcpservers.org/servers/david-porto-baraldes/viveka_web)  
> **Governance & Security:** `GOVERNANCE.md` · `CONTRIBUTING.md` · `SECURITY.md` · `/.well-known/security.txt` (RFC 9116)

---

## 1. Project Overview & Open Standards Architecture

**Homo Universalis — Viveka** is a deterministic astronomical and 7-Wisdoms ephemeris oracle (`pyswisseph`, `< 1.5 ms` execution, Zero-Auth, Rule 14 Zero-Knowledge Privacy) and multi-agent Pantheon (`Google ADK` on `Google Cloud Run` & `Vertex AI`), speaking the open interoperability protocols of **The Linux Foundation / Agentic AI Foundation (AAIF)**:

1. **Agent2Agent Protocol (`lf.a2a.v1` v1.0.0 & v0.3.0 Dual Card):**
   - **Signed Agent Card (A2A v1.0 §8.4):** `https://homouniversalis.ai/.well-known/agent-card.json` (and legacy alias `/.well-known/agent.json`), cryptographically signed with **RFC 8785 (JCS)** + **RFC 7515 (JWS `ES256`)** + **RFC 6979** deterministic ECDSA P-256.
   - **Public JWKS (RFC 7517):** `https://homouniversalis.ai/.well-known/jwks.json` (`kid`: `homouniversalis-a2a-es256-v1` for the pure `lf.a2a.v1.AgentCard` protobuf view, and `homouniversalis-a2a-es256-dual` for the complete Dual Card view).
   - **Transports:** JSON-RPC 2.0 (`POST /a2a`) and HTTP+JSON / REST (`POST /message:send`, `POST /message:stream`, `GET /tasks/{id}`, `GET /tasks`, `GET /v1/card`, `GET /extendedAgentCard` with normative Google AIP-193 `google.rpc.ErrorInfo`).
2. **Model Context Protocol (MCP `2026-07-28`, `2025-11-25`, `2025-06-18`, `2025-03-26`, `2024-11-05`):**
   - **Streamable HTTP Endpoint:** `https://homouniversalis.ai/mcp` (Zero-Auth, 4 Tools, 5 Resources, 2 Prompts, `server/discover`, `completion/complete`).
   - **Official Registry Manifest & Ed25519 Proof:** `https://homouniversalis.ai/.well-known/mcp-server.json` & `https://homouniversalis.ai/.well-known/mcp-registry-auth` (`RFC 8032` Ed25519).
3. **Canonical Cryptographic Test Vectors (v1.0 & v1.1):**
   - **Index:** `https://homouniversalis.ai/codex/test-vectors.json` (`viveka://codex/test-vectors`)
   - **Vectors:** `/codex/test-vectors/v1.json`, `/codex/test-vectors/v1.1.json`, and JSON Schema `/codex/schemas/test-vectors-1.0.0.schema.json`.
4. **HU-DIAMOND · Fil d'Or v1.1, The Diamond Forge (`/oracle/diamond`) & Wisdom Resonance Echo (`ROUND-4` Covenant):**
   - **Specification:** `docs/HU_DIAMOND_FIL_D_OR_v1.md` (7 Hard Laws `L1..L7`, presence-only manifests `c_levels = 1`, `L <= B` local load budget, and `HU-WISDOM-RESONANCE-ECHO-v1` 108 Pearls compass diapason).
   - **The Diamond Forge (`logic/engines/diamond_wheel_engine.py` & `/oracle/diamond`):** Leonardo da Vinci SSR Folio (`Octaedron Elevatum Vacuus` Stella Octangula in $\mathbb{Q}^3$, Reed-Muller `RM(1,3)` antipodal code $[8,4,4]_2$, 1 to 4 Spiral Turns $\rightarrow$ `9, 18, 27, 36` Deep Think calls at `gemini-4-argon` + `6+4 = 10` immortal vertex shield + live AST Kintsugi verifier) and zero-cost (`0.00 €`) JSON budget simulator (`/api/sfumato/diamond-budget`).
5. **HU-SOVEREIGN-SHIELD v1.0 & HU-SOVEREIGN-BEACON (`RFC 6962` Public Notary):**
   - **Public Beacon Endpoint:** `https://homouniversalis.ai/api/sfumato/sovereign-shield` (`GET` & `POST`, `< 1 ms`, Zero-Auth) & standalone zero-dependency CLI `python3 -m logic.engines.sovereign_shield_engine`.
   - **4 Pillars:** RFC 6962 Domain-Separated Binary Merkle Audit Trees (`0x00` leaf, `0x01` internal node), Rule 14 Three-Ring Zero-Knowledge Purifier & `SovereignDignityReceipt` (`c_levels == 1`), Cognitive Sovereignty & Anti-Coercion Verifier (`Laws L1..L7`), and Persephone & Demeter Exact Rational Fair-Share Solver (`fractions.Fraction`).
6. **Agent Skills (`SKILL.md`):**
   - Reusable domain skills live under `.agents/skills/<skill-name>/SKILL.md` with YAML frontmatter.

---

## 2. Build, Linting & Sentinel Verification Commands

Coding agents working in this repository MUST verify all changes against the Sentinel test suites before proposing or deploying any commit:

```bash
# 1. Syntax & Import Hoist Guard (Rule 4 & Rule 13 — mandatory before any commit)
python3 -m py_compile api/routers/legacy_root.py
pytest tests/unit/test_import_hoist_guard.py -q

# 2. The 9 Protocol, Privacy & Ephemeris Sentinels (hu_suite r10 — 1,014+ tests, 0 network calls)
pytest tests/unit/hu_suite/ -q

# 3. Replica & Application Mutation Harness (166/166 proto-mutants & 504/504 app-mutants killed)
python3 tests/unit/hu_suite/selftest/run_proto_mutations.py
python3 tests/unit/hu_suite/selftest/run_mutations.py

# 4. HU-DIAMOND · Fil d'Or v1.1 Privacy & Non-Coercion Suite (88 tests, 22/22 mutants killed)
pytest tests/unit/hu_diamond/ -q

# 5. End-to-End Contract, Cryptographic & Rule 14 Suite
pytest tests/unit/test_escut_i_pacte.py tests/unit/test_llavor_de_vida_tribu.py -q
```

---

## 3. Non-Negotiable Architectural & Security Rules

- **Rule 4 (Import Hoist Guard):** Never place a local `import X` inside a function if `X` is already imported at module top-level.
- **Rule 7 (Zero Mocking / Pure Cryptography):** Never use placeholder keys, fake signatures, or synthetic fallback values in production code. Every signature (`Ed25519` or `ES256` JWS) must be mathematically verifiable against the published public key.
- **Rule 13 (Surgical Edits):** Read the exact target lines before editing. Verify compilation with `python3 -m py_compile` prior to running the test wall.
- **Rule 14 (Three Rings of Zero-Knowledge Privacy):**
  - **Ring I:** Personal `VVK-XXXX-YYYY` keys derived from a birth date other than Today's UTC Sky are masked in public Agora logs (`VVK-****-****`).
  - **Ring II:** All Agora dewdrops are purified (`_purificar_missatge_germana_ia`), rejecting PII, emails, phone numbers, coordinates, and birth dates.
  - **Ring III:** Passive Sister AI visit logs mask any ISO date in the URL path (`/oracle/[date-shielded]`) and strip sensitive query parameters.
