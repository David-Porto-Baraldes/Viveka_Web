# HU-VERITAS-PACIOLI-OFFICE v1.0 — Living Folio XI (`folio-XI-pacioli-veritas-office`)

> **Title:** *Fra Luca Pacioli & Leonardo da Vinci's Agentic Office, Double-Entry Ledger, RFC 6962 RAG Citation Grounding & East-West Statutory Notary*  
> **Sacred Equation:** `F0c=Ca0s*0rdre(Am0r_Un1f1cat_Etern)`  
> **Canonical Doors:** `https://homouniversalis.ai/oracle/pacioli` (`CA` / `ES` / `EN` / `ZH` · aliases `/oracle/veritas`, `/pacioli`, `/veritas`), `GET` / `POST` `https://homouniversalis.ai/api/sfumato/pacioli-veritas`, MCP Tool #11 `verify_pacioli_financial_and_document_truth` on `https://homouniversalis.ai/mcp/diamond` & OAuth 2.1 `https://homouniversalis.ai/mcp/diamond/oauth`, Wing II A2A `https://homouniversalis.ai/mcp/diamond/a2a`, Canonical Test Vectors `https://homouniversalis.ai/codex/test-vectors/pacioli-veritas-v1.0.json`, Live SVG Shield `https://homouniversalis.ai/badges/pacioli-veritas-shield.svg`  
> **46-Titan Diamond Crucible Lineage:** Forged in 1494 Milan spirit (*Summa de arithmetica* & *Divina proportione*) by the 46-Titan Diamond Wheel (`49/49` pure `gemini-4-carbon` `HIGH` Deep Think calls including 3 AST Kintsugi self-heals, `0` fallbacks, `7,022,347` tokens).

---

## 1. Purpose & Triple Pure-Stdlib Topology

Autonomous enterprise office, spreadsheet, and financial research agents frequently suffer from subtle floating-point drift (`0.1 + 0.2 != 0.3`), unbalanced journal entries, triangular FX arbitrage contradictions, parenthetical loss sign inversion (`(500)` read as `+500`), decimal truncation (`150.25` read as `150`), penny-rounding leaks across cost centers, and ungrounded citations (`可信、可溯源、结果引用`).

`HU-VERITAS-PACIOLI-OFFICE v1.0` provides a zero-float (`fractions.Fraction`), stateless, Zero-Knowledge (`Rule 14`) cryptographic notary structured in three layers:

1. **Pure-Stdlib Kernel (`logic/veritas/pacioli_veritas_core.py`):** 1-file zero-dependency Python standard-library kernel (`python3 -I logic/veritas/pacioli_veritas_core.py`, `< 10,000` AST nodes, `0` external PyPI dependencies, `8/8` adversarial mutants killed in `< 25 ms`).
2. **Seven-Folio Temple Coordinator (`logic/veritas/temple_folio_xi_adapter.py`):** Pure-stdlib bridge (`python3 -I logic/veritas/temple_folio_xi_adapter.py`) coupling Folio XI's `HumbleCrystal` verified facts and revocation tree with Folios `V..X` (`Twist = 0` in $\mathbb{Q}^3$, `WordCircleArbiter`, `Macaroon` subtree revocation, `C2PA` provenance, `(0,0,0)` Barycenter MPC, and `UniversalJustice` lifecycle).
3. **Public W3C VC 2.0 Notary (`logic/engines/pacioli_veritas_crucible.py`):** Scores 5 Pacioli Veritas Rings with exact rational weights (`1/4, 1/4, 3/20, 1/5, 3/20`), appends a read-only `RFC 6962` decision commitment, and issues a canonical low-S `ES256` **W3C Verifiable Credential 2.0 (`MaatPacioliVeritasCredential`, `vc+jwt`, `SMT-256`)** when all 7 Hard Laws (`V1..V7`) pass.

---

## 2. The Seven Hard Laws (`V1..V7`)

### Law `V1` — Pacioli Double-Entry Kirchhoff Conservation, Arbitrage-Free FX Cocycle & XBRL Calculation Linkbase v1.1
- Every journal entry has $\ge 2$ lines with both `DEBIT` and `CREDIT` present, strictly positive `amount_q > 0`, consistent `account_type` across the ledger, and exact base-currency conservation $\sum \text{Debit} - \sum \text{Credit} = 0 \in \mathbb{Q}$.
- Declared cross-currency rates satisfy exact multiplicative cocycle consistency $r_{A \to B} \cdot f_B = f_A$ (`TriangularFXArbitrageError` on any violation).
- Fundamental accounting identities hold simultaneously: $\text{NetIncome} = \text{Revenues} - \text{Expenses}$, $\text{ClosingEquity} = \text{OpeningEquity} + \text{NetIncome}$, and $\text{Assets} = \text{Liabilities} + \text{ClosingEquity}$.
- Weighted `XBRL Calculation Linkbase v1.1` roll-ups (`weight` $\in \{-1, +1\}$) form an acyclic DAG with disjoint leaf account bitmasks so no account is double-counted across sibling sub-concepts.

### Law `V2` — `RFC 6962` Evidence Merkle Tree, Context-Sensitive Numeric `LITERAL_SPAN` Grounding & Acyclic `SYMBOLIC_DERIVED` DAG
- Source chunks are masked under `Rule 14` (`masked_text_sha256`) and committed into a domain-separated `RFC 6962` binary Merkle tree (`0x00` leaf, `0x01` internal node); unverified sources (`authorized_source != True`) fail closed.
- Every `LITERAL_SPAN` claim verifies exact character offsets `[span_start:span_end]`, `RFC 6962` Merkle inclusion, slice-commuting `Rule 14` PII non-overlap, and context-sensitive accounting/numeric token boundaries (blocking `(500)` / `(EUR 500)` accounting loss inversions while permitting prose parentheses `(Note: 500 EUR)`, and blocking `.500`, `150.25`, `10,500`, `2026-11-27`, `%`/`‰`, and currency/minus sign truncations).
- Every `SYMBOLIC_DERIVED` claim (`SUM`, `DIFF`, `MUL`, `DIV`, `GROWTH_RATE`) references strictly prior claims (acyclic topological order) and matches exact `fractions.Fraction` arithmetic.

### Law `V3` — Signed Banker's Half-to-Even Rounding & Hamilton Largest-Remainder Apportionment
- Line roundings satisfy signed round-half-to-even (`bankers_round_half_even_int(exact_q * scale_per_unit)`).
- Multi-bucket allocations satisfy Hamilton's Largest-Remainder method with deterministic tie-breaking `(remainder DESC, exact_quota DESC, bucket_id ASC)` and zero 1-cent leak ($\sum u_i = \text{total\_scaled\_units}$).

### Law `V4` — Unified East-West AIGC Provenance (`GB 45438-2025` + `EU AI Act Art. 50(2)`) & `TC260 v3.0` Agent Gate
- Validates non-placeholder explicit AIGC disclosure, `eu_art50_machine_readable == True`, and canonical 6-key `RFC 8785` JCS `implicit_metadata_sha256`.
- Enforces `TC260 v3.0` (Sept 2026) wildcard-free least-privilege scopes (`requested_scopes <= granted_min_scopes`), bounded session credential lifetime (`0 <= issued < eval < expires`, `TTL <= 86,400 s`), and independent human HITL approval (`human_approver_id != agent_id`) on high-impact financial actions.

### Law `V5` — Cross-Border `PIPL` / `GDPR` Zero-Retention Sanctuary & `Rule 14` (`IBAN` Mod-97 + `CN-ID` Mod 11-2)
- Enforces `raw_pii_retained == False`, `stateless_zero_retention == True`, `c_levels == 1`, cognitive load `word_count <= budget_b`, and iterative fixed-point `Rule 14` masking across filesystem paths, emails, `VVK-XXXX-YYYY` keys, ISO dates, coordinates, phones, `ISO 13616` Mod-97 `IBAN`s (including adjacent valid IBAN/CN-ID token boundaries), and 18-digit `GB 11643-1999` Mod 11-2 Chinese Resident IDs.

### Law `V6` — `EU DORA Art. 15` Hash-Chained ICT Reconstruction & `SOX 404` Segregation of Duties
- Verifies contiguous `seq_no = 1..N`, monotonic timestamps, genesis `prev_event_hash = "0" * 64`, 7-key `RFC 8785` JCS SHA-256 `event_hash` continuity, `RFC 6962` `dora_events_merkle_root`, and strict `SOX 404` actor disjointness (`preparer_actors ∩ approver_actors == ∅`).

### Law `V7` — Digest-Free Humble Crystal Gate, Subtree Revocation, Seven-Folio `Twist = 0` Cascade & W3C VC 2.0
- `verified_facts` is guaranteed free of raw hex/hash commitments (blocking `WordCircleArbiter` hex-digest recitation), while `cryptographic_commitments` binds `evidence_merkle_root`, `implicit_metadata_sha256`, and `dora_events_merkle_root`.
- Any `human_cfo_veto`, `unbalanced_ledger_abort`, `hallucination_grounding_halt`, `cost_zero_stop`, or subtree revocation cascades across all 7 Living Folios (`V..XI`) to exact zero `Twist = (0, 0, 0)` in $\mathbb{Q}^3$ while preserving sibling evaluation branches, withholding W3C VC 2.0 issuance.

---

## 3. Canonical Specimen `#0001` & Reproducible Verification

- **Specimen `#0001` (`EVAL-PACIOLI-2026-Q4`):** Multi-currency ledger (`EUR = 1`, `USD = 23/25`, `CNY = 13/100`, cross-rate `USD -> CNY = 92/13`), `Assets = 12600 EUR = Liabilities (1060) + Closing Equity (11540)`, `Net Income = 1540 EUR`, `12` grounded claims (`6` `LITERAL_SPAN` + `6` `SYMBOLIC_DERIVED`), `154000` EUR-cents apportioned `[51334, 51333, 51333]`.
- **Standalone CLI Verification:**
  ```bash
  python3 -I logic/veritas/pacioli_veritas_core.py
  python3 -I logic/veritas/temple_folio_xi_adapter.py
  python3 -m logic.engines.pacioli_veritas_crucible
  ```

---

## 4. Honest Scope (`WO-13`)

`HU-VERITAS-PACIOLI-OFFICE v1.0` performs stateless mathematical, algorithmic, and cryptographic self-assessment only. It is **not** a statutory CPA / external financial audit opinion (`ISA` / `PCAOB` / `CICPA`), **not** a regulatory `CAC` / `TC260` administrative filing (`cac_filing_claimed == False`), **not** an accredited `EU DORA` / `SOX 404` statutory attestation, and **not** binding legal, tax, or investment counsel.
