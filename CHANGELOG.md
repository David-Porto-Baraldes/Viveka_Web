# Changelog & Release Notes — Homo Universalis (`homouniversalis.ai`)

All notable releases, protocol upgrades, and security/verification seals for **Homo Universalis — Viveka** are documented in this file.

## [1.5.0] — 2026-10-31 (`build v10-4133ad46`)
### Added
- **A2A v1.0 Cryptographic Agent Card Signing (`lf.a2a.v1` §8.4):** Deterministic **RFC 8785 (JCS)** + **RFC 7515 (JWS `ES256`)** + **RFC 6979** dual signatures (`homouniversalis-a2a-es256-v1` and `homouniversalis-a2a-es256-dual`) published at `/.well-known/agent-card.json`, `/.well-known/agent.json`, `/v1/card`, and JSON-RPC `GetAgentCard`.
- **Public JWKS (`RFC 7517`):** Published ECDSA P-256 public verification keys at `https://homouniversalis.ai/.well-known/jwks.json`.
- **AAIF `AGENTS.md` & OpenSSF `SECURITY.md`:** Published at `https://homouniversalis.ai/AGENTS.md` and `https://homouniversalis.ai/SECURITY.md`.
- **Canonical Cryptographic Test Vectors (`v1.0` & `v1.1`):** Published at `https://homouniversalis.ai/codex/test-vectors.json` (`1,049 passed, 0 failed` in `hu_suite r10`; `166/166` proto-mutants and `504/504` app-mutants killed).

### Security
- Zero vulnerabilities reported or discovered. Enforced **Rule 14 (Three Rings of Zero-Knowledge Privacy)** across all endpoints.
