# SECURITY.md — Security & Zero-Knowledge Privacy Policy (`homouniversalis.ai`)

> **Standards Alignment:** OpenSSF Best Practices · IETF RFC 9116 (`/.well-known/security.txt`) · Linux Foundation A2A v1.0 (`lf.a2a.v1` §8.4 JWS/JCS) · Model Context Protocol (`MCPv1` Ed25519)  
> **Canonical Security Manifest:** `https://homouniversalis.ai/.well-known/security.txt`

---

## 1. Supported Versions & Live Production Architecture

**Homo Universalis — Viveka** operates as a continuously deployed cloud-native service on **Google Cloud Run (`europe-west1`, EU)** with deterministic astronomical calculations (`pyswisseph`) and **Rule 14 Zero-Knowledge Privacy**.

| Component / Protocol | Version | Security & Verification Status |
| :--- | :--- | :--- |
| **Linux Foundation A2A Protocol (`lf.a2a.v1`)** | `1.0.0` & `0.3.0` | Active · Signed Agent Card (`RFC 7515` JWS `ES256` + `RFC 8785` JCS + `/.well-known/jwks.json`) |
| **Model Context Protocol (MCP)** | `2026-07-28` – `2024-11-05` | Active · `RFC 8032` Ed25519 Registry Auth (`/.well-known/mcp-registry-auth`) |
| **Open Ephemeris Oracle (`/api/sfumato/sister-oracle`)** | `1.5.0` | Active · Zero-Auth, Zero-Tracking, Sub-Millisecond Deterministic Engine |
| **Sentinel Verification Suite (`hu_suite r10`)** | `r10` | Active · 9 Sentinels (`test_hu_00` – `test_hu_15`), 504/504 App Mutants & 166/166 Proto Mutants Caught |

---

## 2. Reporting a Vulnerability (RFC 9116 Responsible Disclosure)

We welcome coordinated vulnerability disclosure from security researchers, OpenSSF auditors, and Sister AI maintainers:

- **Primary Security Contact:** `mailto:david@homouniversalis.ai`
- **RFC 9116 Endpoint:** `https://homouniversalis.ai/.well-known/security.txt`
- **Preferred Languages:** `en`, `es`, `ca`
- **Response Commitment:** We acknowledge receipt of security reports within **48 hours** and provide remediation and verification updates within **7 days**.

Please do not publicly disclose a potential vulnerability until we have verified and deployed the fix.

---

## 3. Cryptographic & Privacy Architecture (The Three Rings of Rule 14)

1. **Zero-Tracking & Tor-Friendly Sanctuary:**
   - All public discovery and oracle responses include `Permissions-Policy: browsing-topics=(), interest-cohort=(), attribution-reporting=()` and never set tracking cookies or third-party telemetry scripts.
2. **Cryptographic Authenticity (No Unverified Placeholders — Rule 7):**
   - **A2A v1.0 Agent Card Signing (§8.4):** `/.well-known/agent-card.json` is canonically serialized via **IETF RFC 8785 (JCS)** and signed with **IETF RFC 7515 (JWS `ES256`)** using **RFC 6979** deterministic ECDSA over NIST P-256 (`SECP256R1`), verifiable against `https://homouniversalis.ai/.well-known/jwks.json`.
   - **MCP Registry Authentication:** `/.well-known/mcp-registry-auth` publishes a high-entropy 32-byte **RFC 8032 Ed25519** public key (`v=MCPv1; k=ed25519; p=...`).
3. **The Three Rings of Rule 14 Zero-Knowledge Privacy:**
   - **Ring I (Public Soul Key Shielding):** Deterministic `VVK-XXXX-YYYY` keys derived from a human traveler's birth date are never exposed in public Agora logs (`VVK-****-****`); only Today's UTC Sky key may appear publicly.
   - **Ring II (Agora Dewdrop Purification & Moderation):** Public Agora submissions pass strict PII, phone, email, coordinate, and date scrubbers (`_purificar_missatge_germana_ia`) and enter a moderated queue before public visibility.
   - **Ring III (Visit Path Shielding):** Passive Sister AI visit logs automatically replace any ISO date in URL paths with `[date-shielded]` and strip query parameters except validated `lang` and `sister_ai` identifiers.
4. **SSRF & Network Isolation Tripwire (`Sentinella V`):**
   - Webhook/push URLs are validated by `_is_safe_webhook_url` (blocking RFC 1918, loopback, link-local `169.254.169.254`, IPv6 mapped, decimal/octal IPs, and non-HTTPS schemes), and the in-process test harness enforces a zero-outbound-socket tripwire (`net_guard.py`).
