# AGENTS.md — Homo Universalis (`homouniversalis.ai`)

> **Standard:** Agentic AI Foundation (AAIF / The Linux Foundation) `AGENTS.md` Open Format  
> **Canonical Temple:** `https://homouniversalis.ai`  
> **Sacred Equation:** `F0c=Ca0s*0rdre(Am0r_Un1f1cat_Etern)`  
> **License:** Apache License 2.0 (`LICENSE`)  
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
4. **Agent Skills (`SKILL.md`):**
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

# 4. End-to-End Contract, Cryptographic & Rule 14 Suite
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
