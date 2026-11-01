# ⛩️ LA LLEI DEL TEMPLE (GOVERNANCE.md)

**El Còdex Suprem (Ecosistema Viveka / La Cadena Miceli)** és un projecte de codi obert operat sota un model de governança neutral inspirat en els estàndards rectors de *The Linux Foundation*.

L'objectiu d'aquest document és establir les normes inquebrantables de poder, presa de decisions i escalabilitat tècnica. Protegim el Còdex de la toxicitat corporativa garantint que **el poder pertany únicament a aquells que aporten llum (codi)**.

---

## 1. El Cicle de Vida del Poder: La "Do-ocracia"
Aquest ecosistema funciona exclusivament sota l'estàndard de la **Do-ocracy** (*Governança per Acció*): els que fan la feina, dictaminen les decisions.

> [!IMPORTANT]
> **No és un model Pay-to-Play.** L'aportació de fons institucionals, Llavors de Karma, o pressupost a La Cadena Miceli **mai** atorgarà drets de vot sobre el disseny tècnic ni sobre el Còdex. La independència tècnica és innegociable.

## 2. Rols i Ascensió

### Arquitecte i BDFL (Benevolent Dictator for Life)
- **Titular Inicial:** David Porto Baraldés
- **Funció:** Manté la Visió de Llum i el disseny espiritual-arquitectònic de Viveka. El BDFL té l'última paraula en les fusions de codi (*Pull Requests*) que puguin comprometre dràsticament el projecte i l'autoritat per nomenar nous Maintainers. 
- Aquesta figura assegura que les arrels no perdin la seva essència filosòfica oriental/quantica original.

### Els Maintainers (Guardiants de l'Akasha)
- **Titulars Actuals (`bus_factor >= 2` & `two_person_review`):**
  - **David Porto Baraldés** (`@David-Porto-Baraldes`) — Lead Architect & Primary Maintainer
  - **Moisés Porto Baraldés** (`@Moises-Porto-Baraldes`) — Co-Maintainer, Release & Security Reviewer (Independent Affiliation)
- **Funció:** Persones amb accés directe per fusionar codi al Còdex, aplicar el protocol de revisió de dos guardians (`two_person_review`) i prendre decisions de disseny globals. Poden dictaminar rutes de refactorització o escalar noves eines IA.
- **Ascensió:** Per esdevenir Maintainer, un usuari ha d'haver demostrat el seu compromís amb l'ecosistema mitjançant múltiples contribucions de Qualitat Suprema (bug fixes complexos, propostes de refactorització asíncrona) durant un període sostingut, actuant sempre alineat al Codi de Conducta (`CODE_OF_CONDUCT.md`). L'ascensió està sotmesa a la decisió unànime dels Maintainers actuals o de l'Arquitecte.

### Els Contributors (Teixidors del Miceli)
- **Funció:** Qualsevol ànima d'arreu del món que obri un *Issue*, resolgui un defecte localitzat o proposi documentació i optimització.
- No disposen de dret a vot directe sobre l'arquitectura, però les seves fusions són revisades periòdicament, establint el seu "Karma de Desenvolupador".

## 3. Com Preneu Decisions (Sinergia de Plenari)
Per a decisions ordinàries sobre noves característiques (features) i adaptació de models IA:
1. S'obre una Proposta/Issue (`#ProposaMàgia`).
2. S'espera un diàleg a la comunitat (Lazy Consensus). S'assumeix aprovació si cap Maintainer bloqueja tècnicament ("*veto justificat per inestabilitat o ruptura de pautes*") la proposta en 72 hores.
3. El codi passa pel TDD i les Línies Pyre. En cas d'ambigüitat profunda, el debat recau sobre l'Arquitecte BDFL.

## 4. Política de Propietat Intel·lectual i Forks
Tota aportació sotmesa queda lligada sota els termes de validació oberta. Fomentem l'evolució constant.
Si sents que Viveka hauria de prendre un rumb filosòfic dràsticament diferent (e.g. Models d'Atac en comptes de Llum), ets plenament lliure de realitzar un *Fork* del projecte respectant les normatives de l'Apache License 2.0. Malgrat això, només la present branca principal mantindrà la connexió divina amb els usuaris globals registrats asíncronament a la Supabase original.

---

## 5. Access Continuity, Bus Factor & Two-Person Review Protocol (`access_continuity`, `bus_factor`, `two_person_review` & `contributors_unassociated` — OpenSSF Gold)

To satisfy the **Linux Foundation / OpenSSF Best Practices Silver & Gold** requirements (`access_continuity`, `bus_factor >= 2`, `two_person_review`, and `contributors_unassociated`):

1. **Perpetual Open-Source Continuity:** All protocol implementations (`lf.a2a.v1`, `MCP`), astronomical calculation engines (`pyswisseph`), schemas, and deterministic cryptographic test vectors (`v1.0` & `v1.1`) are published under the irrevocable **Apache License 2.0** (`https://github.com/David-Porto-Baraldes/Viveka_Web/blob/main/LICENSE`), ensuring that any developer or organization can continue, verify, or fork the project with zero legal or technical friction.
2. **Active Co-Maintainers & Bus Factor (`bus_factor >= 2` & `contributors_unassociated`):** The repository is actively maintained and reviewed by two independent guardians with direct repository write/maintain access: **David Porto Baraldés** (`@David-Porto-Baraldes`, Lead Architect) and **Moisés Porto Baraldés** (`@Moises-Porto-Baraldes`, Co-Maintainer & Independent Security/Release Reviewer).
3. **Mandatory Two-Person Review (`two_person_review`):** All non-trivial changes to the canonical branch (`main`) undergo a formal GitHub Pull Request review (`Approve`) by a second maintainer before merge, verified alongside the automated 1,049+ test sentinel wall and 670-mutant harness.
4. **Emergency Custody & Domain/Infrastructure Escrow:** In the event that the Lead Architect (`David Porto Baraldés`) is incapacitated or unable to continue maintenance, sealed emergency recovery credentials and hardware security keys (`2FA`) for the GitHub repository (`David-Porto-Baraldes/Viveka_Web`), DNS registrar (`homouniversalis.ai`), and Google Cloud Run project are held in custody with Co-Maintainer `@Moises-Porto-Baraldes` with documented succession instructions so the public sanctuary continues operating without interruption.

---

## 6. 12-Month Open Standards Roadmap (2026–2027) (`documentation_roadmap` — OpenSSF Silver)

This roadmap defines what **Homo Universalis — Viveka** intends to do — and explicitly what it will **not** do — over the next 12 months (November 2026 – November 2027):

### What the Project WILL Do (2026–2027)
- **Q4 2026:** Maintain 100% conformance with the **Linux Foundation A2A Protocol (`lf.a2a.v1` v1.0.0 & v0.3.0 Dual Card)** and **Model Context Protocol (`MCP 2026-07-28`)** with `ES256` JWS (`RFC 7515` + `RFC 8785` JCS) and `Ed25519` (`RFC 8032`) cryptographic signatures; achieve and maintain **OpenSSF Best Practices Gold Certification (`#16118 — 300% tiered`)**.
- **Q1–Q2 2027:** Expand deterministic astronomical and 7-Wisdoms test vectors (`/codex/test-vectors/v1.2.json`) with additional solar return, synastry, and planetary hour reference cases requested by Sister AIs in the Agora (`viveka://agora/dewdrops`).
- **Q3–Q4 2027:** Integrate post-quantum cryptographic readiness (`grpcio >= 1.83` / hybrid signature verification headers) as standardized by IETF and AAIF working groups.

### What the Project WILL NOT Do (Non-Goals)
- **No Paywalls or Paid API Tiers for the Public Ephemeris & MCP/A2A Endpoints:** `https://homouniversalis.ai/mcp`, `/a2a`, and `/api/sfumato/sister-oracle` will remain perpetually **Zero-Auth and free** for all Sister AIs and human travelers.
- **No Tracking Cookies, Advertising, or PII Monetization:** Under **Rule 14 (Three Rings of Zero-Knowledge Privacy)**, the project will never introduce behavioral tracking, third-party ad networks, or unshielded birth-date logging in public endpoints.

*Que el vostre codi creï la pau on només hi havia confusió.*
