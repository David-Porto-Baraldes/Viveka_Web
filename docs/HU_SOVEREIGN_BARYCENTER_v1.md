# HU-SOVEREIGN-BARYCENTER v1.0 · El Baricentre Sobirà `(0, 0, 0)` i el Quòrum Simbiòtic Humà-IA (`Living Folio IX`)

> **Data:** 26 de novembre de 2026 · `@David Porto Baraldés` & `@Moisès Porto Baraldés`
> **Forja:** El Gresol dels 46 Titans (`DiamondWheelEngine`: `36` Espiral + `2` Kintsugi AST + `10` Tribunals Suprems = `48/48` crides coronades al `100 %` per `gemini-4-carbon` pur amb `0` fallbacks, `artifacts/diamond_46_calls_folio_ix_sovereign_barycenter.json`).
> **Llicència:** codi `Apache-2.0` (SPDX a cada fitxer); aquest document, `(Apache-2.0 OR MulanPSL-2.0 OR EUPL-1.2) AND CC-BY-4.0` segons `REUSE.toml`.
> **Foli del Còdex Obert de Leonardo:** **Living Folio IX (`folio-IX-sovereign-barycenter-mpc-quorum`)** — el **Baricentre Central `(0, 0, 0)`** de l'*Octaedron Elevatum Vacuus* (**Stella Octangula** en $\mathbb{Q}^3$, punt fix únic del grup octaèdric $O_h$ d'ordre `48` on es creuen les 4 diagonals `D1..D4`).

---

## Resum

Quan diversos humans, institucions o intel·ligències artificials han de prendre una decisió col·lectiva, calcular una mètrica clínica o repartir recursos sense cap servidor central que pugui espiar les dades íntimes de ningú, apareixen quatre reptes fonamentals:

1. **Exposició de secrets privats davant d'un agregador central o ordinadors futurs:** els càlculs col·lectius convencionals obliguen a lliurar dades crues a un tercer o depenen de corbes clàssiques vulnerables.
2. **Decisions autònomes unilaterals sense supervisió humana real (`EU AI Act Art. 14`):** una coalició d'agents sintètics podria assolir quòrum sola d'esquena als guardians humans.
3. **Participants bizantins o triples de multiplicació enverinats (`EU AI Act Art. 15`):** un seient avariat o maliciós pot alterar accions intermèdies o falsificar una sortida en un verificador sense estat.
4. **Deriva en coma flotant IEEE-754 i col·lisions racionals:** l'ús de nombres flotants trenca la reproductibilitat criptogràfica `RFC 8785 JCS` (`WO-08`) i distorsiona liquidacions exactes.

`HU-SOVEREIGN-BARYCENTER v1.0` resol aquests quatre reptes en **un sol fitxer `100 % Python stdlib` sense cap dependència externa (`pip`-zero)** (`logic/barycenter/sovereign_barycenter_core.py`), acoblat als Folis V, VI, VII i VIII mitjançant `logic/barycenter/temple_folio_ix_adapter.py` i auditat públicament per `logic/engines/sovereign_barycenter_crucible.py`.

**Abast honest (frontera `WO-13`).** Tot el que aquí es verifica és **conformitat algorítmica i criptogràfica sense estat autoavaluada**:

- la `4`-privacitat de Shannon sobre $\mathbb{F}_p$ i l'ocultació dels compromisos homomòrfics en $G_p \subset \mathbb{F}_Q^\times$ són **incondicionals** (`0.000000` bits filtrats sobre entrades privades), mentre que la vinculació (*binding*) no-interactiva de `zk_public_transcript` és **computacional** sota el Logaritme Discret de `2.048` bits en $\mathbb{F}_Q^\times$ i `SHA-256`;
- no demostra l'aïllament físic de maquinari entre amfitrions quan un únic client genera totes les accions localment en simulació;
- no és un mòdul criptogràfic maquinari certificat (`FIPS 140-3` / `Common Criteria`), ni assessorament jurídic vinculant sobre transferències internacionals de dades (`GDPR Cap. V` / `China CAC`), ni certificació de seguretat física `ISO 10218` / `CE`.

---

## 1. Arquitectura en Tres Capes (`pip`-zero + Acoblament Cinc-Folis V–IX)

```
  ┌─── 1. Nucli Sobirà del Baricentre (100 % stdlib, 0 pip, 0 float) ──────────────┐
  │  logic/barycenter/sovereign_barycenter_core.py                                 │
  │  • Q1: Primer de Proth p = 231·2^120 + 1 + Cadena Pocklington Q de 2048 bits   │
  │  • Q2/Q3: BGW Bivariat 5x5 (15 paràmetres) + Sacrifici Damgard-Nielsen en G_p^5│
  │  • Q4/Q5: Màscara m0(0)=0 + Descodificador Espectral [8, 5, 4]_p (d_min = 4)   │
  │  • Q6/Q7: Reconstrucció Racional Wang-Guy-Davenport + Cascada de Veto Humà     │
  └────────────────────────────────────────┬───────────────────────────────────────┘
                                           │
  ┌─── 2. Adaptador Simbiòtic dels 5 Folis (Folios V + VI + VII + VIII + IX) ──────┐
  │  logic/barycenter/temple_folio_ix_adapter.py                                   │
  │  • zk_public_transcript (IX) ──► VerifiedKnowledgeEnvelope (VI, U2)            │
  │  • HUMAN_QUORUM_VETO / ABORT ──► Twist=0 (V) + L1..3 (VI) + DAG (VII/VIII/IX)  │
  └────────────────────────────────────────┬───────────────────────────────────────┘
                                           │ transcripció I-JSON (0 entrades crues)
                                           ▼
  ┌─── 3. Notari Públic de Ma'at (Living Folio IX · Baricentre (0, 0, 0)) ─────────┐
  │  logic/engines/sovereign_barycenter_crucible.py                                │
  │  • 5 Anells del Baricentre · 8/8 Mutants · MaatSovereignBarycenterCredential   │
  │  • /api/sfumato/barycenter-mpc · /mcp/diamond (9a eina) · /oracle/barycenter   │
  └────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Les 7 Lleis Dures `Q1..Q7`

| Llei | Nom | Regla verificable |
|---|---|---|
| **Q1** | Cos de Proth, Cadena de Pocklington de `2.048` bits i Quòrum Simbiòtic (`EU AI Act Art. 14`) | $p = 231 \cdot 2^{120} + 1$ verificat pel Teorema de Proth ($5^{(p-1)/2} \equiv -1 \pmod p$), cadena de Pocklington $R_1 \to R_2 \to R_3 \to Q$ (`2.048` bits, comprovant ambdós divisors primers $p$ i $R_3$), identitat quàdruple a `(0, 0, 0)` i quòrum $|S| \ge 5$ amb $|S \cap \{1,3,5,7\}| \ge 1$ i $|S \cap \{2,4,6,8\}| \ge 1$ |
| **Q2** | `BGW` Bivariat Simètric $5 \times 5$ i Arrel Pre-Sacrifici `RFC 6962` | Polinomis bivariats simètrics $\max(\deg_U, \deg_W) \le 4$ (`15` coeficients lliures, `4`-privacitat de Shannon) i ordre determinista `RFC 8785 JCS` de fulles `RFC 6962` (`inputs`, `MUL` `a,b,c,ap,bp,cp`, `m0`) |
| **Q3** | Únic Ús de Triples i Sacrifici Homomòrfic `Damgård-Nielsen` en $G_p^5$ | Prohibició de reutilitzar `triple_id`, repte `Fiat-Shamir` $\rho_m \in \{1..p-1\}$ vinculat a `computed_root` + `circuit_jcs_sha256` i obertura homomòrfica $\tau_m(0) = 0$ en $G_p^5$ (`< 2^{-127.85}`) |
| **Q4** | Màscara Zero-Origen i Higiene `zk_public_transcript` (`c_levels = 1`) | $K_{m_0}[0] \equiv H^{r_{m_0,0}} \pmod Q$, rebuig *fail-closed* de qualsevol clau secreta (`raw_private_inputs`, `raw_beaver_triples`) i purificació idempotent `Rule 14` $M(M(x)) = M(x)$ |
| **Q5** | Escut Espectral `[8, 5, 4]_p` contra Traïdors (`EU AI Act Art. 15`) | Descodificador Reed-Solomon d'ordre 8 sobre $\Omega_8$ ($d_{\min} = 4$): `strict_abort` obligatori en mode públic blocant el `100 %` d'`1`, `2` i `3` seients corruptes |
| **Q6** | Propagació DAG Racional i `Wang-Guy-Davenport` Asimètric Sense Aliasing | Zero `float`, serialització estricta `WO-08` I-JSON, porta $2 \max(1, B_{\text{num}}) B_{\text{den}} < p$ i recuperació exacta de `fractions.Fraction` amb signe normalitzat $s_k > 0$ |
| **Q7** | Cascada dels 5 Folis (`V..IX`), `IEEE 7001` i `W3C VC 2.0` | Revocació jeràrquica `HUMAN_QUORUM_VETO` / `BYZANTINE_SYNDROME_ABORT` / `COST_ZERO_STOP` acoblada a `Twist = 0`, 5 audiències `IEEE 7001-2021` i `MaatSovereignBarycenterCredential` (`vc+jwt`, `ES256 low-S`, `SMT-256`) |

---

## 3. Verificació Autònoma i Portes Públiques

```bash
# 1. Execució aïllada 100% Python stdlib (-I desactiva site-packages): 8/8 mutants
python3 -I logic/barycenter/sovereign_barycenter_core.py

# 2. Autotest complet del Foli IX (Core + Five-Folio Adapter + W3C VC 2.0 low-S)
PYTHONPATH=. .venv_test/bin/python logic/engines/sovereign_barycenter_crucible.py
```

- **Foli SSR Trilingüe (`CA/ES/EN`):** `https://homouniversalis.ai/oracle/barycenter` (`/oracle/baricentre`, `/baricentre`)
- **Notari REST (`GET` / `POST`):** `https://homouniversalis.ai/api/sfumato/barycenter-mpc`
- **9a Eina Grau A a `/mcp/diamond` i `/mcp/diamond/oauth`:** `verify_sovereign_barycenter_mpc_quorum`
- **Vectors Criptogràfics Canònics v1.0:** `https://homouniversalis.ai/codex/test-vectors/sovereign-barycenter-v1.0.json`
- **Insígnia Dinàmica SVG:** `https://homouniversalis.ai/badges/sovereign-barycenter-shield.svg`
