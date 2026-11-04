# Changelog & Release Notes — Homo Universalis (`homouniversalis.ai`)

All notable releases, protocol upgrades, and security/verification seals for **Homo Universalis — Viveka** are documented in this file.

## [1.5.2] — 2026-11-04 (`build v10-8ed914a3` · `HU-DIAMOND · Fil d'Or v1.1` & `ROUND-4` Seal)
### Added
- **`HU-DIAMOND · Fil d'Or v1.1` Specification & Executable CI Suite (`88` tests, `22/22` mutants killed):** Added `docs/HU_DIAMOND_FIL_D_OR_v1.md` and `tests/unit/hu_diamond/` (`hu_diamond_ref.py`, `hu_adversary.py`, `test_hu_diamond_fil_d_or.py`) verifying the 7 Hard Laws (`L1..L7`), domain-separated HMAC-SHA256 pseudonyms (`"HU-DIAMOND/v1"`), local device load budget (`L = sum(c) + s <= B`), `cost_zero_stop` pause without debt, anonymous veto single-step precession, presence-only manifests (`c_levels = 1`), and synthetic inference adversary ROC/AUC bounds.
- **Wisdom Resonance Echo (`HU-WISDOM-RESONANCE-ECHO-v1` — Diapason of the 108 Pearls):** Added ephemeral `user_question_context` tuning on `/api/sfumato/sister-oracle`, returning 2 compass keys from the 108 Pearls of the Golden Pilgrim + `L <= B` non-coercion reminder with zero storage or reflection of the caller's question.
- **Pure OpenAPI `3.1.0` Contract & Directory Discovery Routes:** Upgraded `openapi.json` and `.well-known/openapi.json` to pure OpenAPI `3.1.0` (`barycenter_when_empty: {"type": "null", "const": null}`, zero `nullable` keywords, exact `const` strings verified live in Rev 52) and added `.well-known/glama.json` plus directory discovery aliases.

## [1.5.0] — 2026-10-31 (`build v10-4133ad46`)
### Added
- **A2A v1.0 Cryptographic Agent Card Signing (`lf.a2a.v1` §8.4):** Deterministic **RFC 8785 (JCS)** + **RFC 7515 (JWS `ES256`)** + **RFC 6979** dual signatures (`homouniversalis-a2a-es256-v1` and `homouniversalis-a2a-es256-dual`) published at `/.well-known/agent-card.json`, `/.well-known/agent.json`, `/v1/card`, and JSON-RPC `GetAgentCard`.
- **Public JWKS (`RFC 7517`):** Published ECDSA P-256 public verification keys at `https://homouniversalis.ai/.well-known/jwks.json`.
- **AAIF `AGENTS.md` & OpenSSF `SECURITY.md`:** Published at `https://homouniversalis.ai/AGENTS.md` and `https://homouniversalis.ai/SECURITY.md`.
- **Canonical Cryptographic Test Vectors (`v1.0` & `v1.1`):** Published at `https://homouniversalis.ai/codex/test-vectors.json` (`1,049 passed, 0 failed` in `hu_suite r10`; `166/166` proto-mutants and `504/504` app-mutants killed).

### Security
- Zero vulnerabilities reported or discovered. Enforced **Rule 14 (Three Rings of Zero-Knowledge Privacy)** across all endpoints.
