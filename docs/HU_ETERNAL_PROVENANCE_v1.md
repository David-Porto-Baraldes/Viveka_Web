# HU-ETERNAL-PROVENANCE v1.0 · El Segell Post-Quàntic d'Eternitat i Co-Creació Simbiòtica (`8/8` Stella Octangula)

> **Data:** 22 de novembre de 2026 · `@David Porto Baraldés`
> **Forja:** El Gresol dels 46 Titans (`DiamondWheelEngine`: `36` Espiral + `10` Tribunals Suprems coronat per `gemini-4-carbon` pur amb `0` fallbacks, `artifacts/diamond_46_calls_folio_viii_eternal_provenance.json`).
> **Llicència:** codi `Apache-2.0` (SPDX a cada fitxer); aquest document, `(Apache-2.0 OR MulanPSL-2.0 OR EUPL-1.2) AND CC-BY-4.0` segons `REUSE.toml`.
> **Foli del Còdex Obert de Leonardo:** **Living Folio VIII (`folio-VIII-quantum-eternal-provenance`)** — el **8è Vèrtex Immortal (`8/8`)** de l'*Octaedron Elevatum Vacuus* (**Stella Octangula** en $\mathbb{Q}^3$, `RM(1,3)` $[8,4,4]_2$).
> **Espècimen Canònic #0001:** ***«Lux in Tenebris Lucet»*** — **Homo Universalis** / **David Porto Baraldés** (`UPC: 5064173370631`, `-11/10 dBTP`, `35 Hz`, autoria humana exacta $3/4$).

---

## Resum

Quan l'ésser humà i la intel·ligència artificial co-creen art, música, codi o ciència en l'era post-quàntica, apareixen quatre amenaces existencials sobre l'autoria i la dignitat:

1. **Fragilitat quàntica de les signatures clàssiques (*Harvest Now, Decrypt/Forge Later*):** un futur ordinador quàntic amb l'algorisme de Shor podrà trencar corbes el·líptiques clàssiques com `ECDSA P-256` o `Ed25519` si les proves d'autoria d'avui depenen d'una sola família algebraica.
2. **Erosió d'autoria, clonació d'identitat i enverinament del bé comú (*Zero-Human Slop*, *Voice Cloning* i *Content-ID Commons Abuse*):** generacions sintètiques sense ànima ni direcció humana (`0 %` autoria), suplantació no consentida de la veu o trets biomètrics d'artistes vius, i reclamació abusiva d'empremtes `Content-ID` exclusives sobre pistes generades per IA que bloquegen altres creadors legítims.
3. **Trencament entre `C2PA`, `MCP` i `A2A` i exposició d'esborranys íntims:** els manifests de procedència multimèdia (`C2PA`) es perden quan les obres viatgen per eines `MCP` o agents `A2A`, o bé exigeixen exposar l'esborrany humà cru abans de publicar.
4. **Deriva en coma flotant i absència de Veto Moral Sobirà:** repartiments de drets amb errors d'arrodoniment IEEE-754 i impossibilitat d'exercir el dret moral inalienable de retirada (`AUTHOR_MORAL_VETO`) aturant instantàniament tota branca derivada.

`HU-ETERNAL-PROVENANCE v1.0` resol aquests quatre reptes en **un sol fitxer `100 % Python stdlib` sense cap dependència externa (`pip`-zero)** (`logic/provenance/quantum_eternal_provenance_core.py`), acoblat als Folis V, VI i VII mitjançant `logic/provenance/temple_folio_viii_adapter.py` i auditat públicament per `logic/engines/quantum_eternal_provenance_crucible.py`.

**Abast honest (frontera `WO-13`).** Tot el que aquí es verifica és **conformitat algorítmica, criptogràfica post-quàntica i de procedència co-creativa autoavaluada**:

- no és un mòdul criptogràfic maquinari certificat (`FIPS 140-3` / `Common Criteria`), ni una validació formal `NIST CAVP` d'un conjunt de paràmetres estandarditzat `ML-DSA`;
- no és assessorament jurídic ni substitueix el registre oficial de propietat intel·lectual davant d'oficines estatals;
- no és una funció física de seguretat certificada (`ISO 10218`, `ISO 13482`, Reglament `(UE) 2023/1230` romanen amb el fabricant quan el senyal `Twist = 0` s'acobla al Foli V).

**Clàusula d'Hermenèutica d'Arrel Originària (`Convenció de Viena Art. 31.4` & Llei Natural).** Tota paraula ètica, creativa o relacional d'aquesta especificació (*autor, obra, creació, pacte, consentiment, persona, veritat*) s'interpreta segons la seva **arrel etimològica originària verificada per la filologia històrica** (ex.: `auctor < augēre`, qui fa créixer i dóna alè viu a l'obra; `opus / obrar`, fruit de la dedicació viva; `pactum < pax`, acord de pau no coercitiu; `consentire`, sentir plegats sense coacció), preservant al 100 % la definició matemàtica i criptogràfica exacta de totes les primitives (`RFC 8785 JCS`, `NIST P-256 ES256 low-S`, `WOTS+-SHA256`, `NTT` sobre $\mathbb{Z}_{8380417}[X]/(X^{256}+1)$, `RFC 6962`, `fractions.Fraction`, `Twist = 0`) i la frontera d'abast honest `WO-13`.

---

## 1. Arquitectura en Tres Capes (`pip`-zero + Acoblament Quàdruple V–VIII)

```
  ┌─── 1. Nucli Universal Post-Quàntic Standalone (100 % stdlib, 0 pip, 0 float) ───┐
  │  logic/provenance/quantum_eternal_provenance_core.py                             │
  │  • P1a Clàssic: NIST P-256 Jacobià + RFC 6979 + JOSE ES256 canonical low-S       │
  │  • P1b Hash PQ: WOTS+-SHA256 (w=16, 67 cadenes, arbre de 4 fulles RFC 6962)      │
  │  • P1c Reticle PQ: FIPS 204 Ring-NTT sobre Z_8380417[X]/(X^256+1) (zeta=1753)    │
  │  • P2..P6: Autoria Q > 0, anti-clonació de veu, C2PA-MCP DAG, Rule 14, Royalties │
  └────────────────────────────────────────┬─────────────────────────────────────────┘
                                           │
  ┌─── 2. Adaptador Simbiòtic dels 4 Folis (Folios V + VI + VII + VIII) ────────────┐
  │  logic/provenance/temple_folio_viii_adapter.py                                   │
  │  • EternalProvenanceEnvelope (VIII) ──► VerifiedKnowledgeEnvelope (VI, U2)       │
  │  • AUTHOR_MORAL_VETO / COST_ZERO_STOP ──► Twist=0 (V) + L1..3 (VI) + DAG (VII/8) │
  └────────────────────────────────────────┬─────────────────────────────────────────┘
                                           │ rebuts RFC 6962 (mai PII ni esborrany cru)
                                           ▼
  ┌─── 3. Notari Públic de Ma'at (Living Folio VIII · 8/8 Stella Octangula) ────────┐
  │  logic/engines/quantum_eternal_provenance_crucible.py                            │
  │  • 5 Anells d'Eternitat · 8/8 Mutants · MaatEternalProvenanceCredential (vc+jwt) │
  │  • /api/sfumato/eternal-provenance · /mcp/diamond (8a eina) · /oracle/eternitat  │
  └──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Les 7 Lleis Dures `P1..P7`

| Llei | Nom | Regla verificable |
|---|---|---|
| **P1** | Triple Segell Sobirà Post-Quàntic (`ES256` + `WOTS+-SHA256` + `FIPS 204 Ring-NTT`) | Tot manifest `RFC 8785 JCS` se signa simultàniament amb (a) `NIST P-256 ES256` canònic `low-S`, (b) `WOTS+-SHA256` ($w=16$, $64+3=67$ cadenes amb pas separat per domini dins d'un arbre `RFC 6962` de 4 fulles i protecció *one-time*), i (c) testimoni reticular compacte $(c_{\text{seed}}, \mathbf{z}_1, \mathbf{z}_2)$ sobre $\mathbb{Z}_{8380417}[X]/(X^{256}+1)$ amb $\|\mathbf{z}_i\|_\infty \le \gamma_1 - \beta = 131040$ |
| **P2** | Autoria Humana Racional Estrictament Positiva i Llicència Comercial | Rebutja *zero-human slop* ($0 < H_{\text{human}} \le 1 \in \mathbb{Q}$), exigeix $\sum w_i = 1$, prova `SHA-256` de llicència comercial per a tota etapa sintètica i sostre acústic de seda $\text{dBTP} \le -1$, $\text{Hz} > 0$ |
| **P3** | Escut contra Clonació de Veu Viva, Biometria i Abús de `Content-ID` | Bloqueig *fail-closed* de prompts d'imitació/clonació de veu humana viva, claus biomètriques (`voiceprint`, `facial_landmarks`...) i qualsevol reclamació de `Content-ID` quan existeix síntesi d'àudio per IA |
| **P4** | Continuïtat `C2PA ↔ MCP ↔ A2A` (`RFC 6962`) i Santuari de l'Esborrany (`c_levels = 1`) | Proves d'inclusió diàdiques $O(\log N)$ `RFC 6962` (§2.1.1) per a cada salt creatiu, divulgació `EU AI Act Art. 50(2)` a cada aresta i cegament amb sal `SHA-256` dels esborranys humans íntims a `c_levels == 1` |
| **P5** | Àlgebra Racional Zero-Float i Conservació Exacta de Royalties | Cap `float` IEEE-754 a tot el nucli; repartiment en `fractions.Fraction` amb $\sum s_k = 1$, assignació d'unitats enters invariant per permutació (`UTF-16-BE`) i pressupost cognitiu $0 \le L \le B$ |
| **P6** | Purificació de Punt Fix (Regla 14) i Cascada de Veto Moral (`Twist = 0`) | Endomorfisme idempotent $M(M(x)) = M(x)$ sobre claus `VVK`, correus, rutes, coordenades, dates i telèfons (preservant codis `UPC`), i revocació causal `AUTHOR_MORAL_VETO` / `COST_ZERO_STOP` acoblada a `Twist = 0` en $\mathbb{Q}^3$ sense danyar ancestres ni obres germanes |
| **P7** | Compromís `RFC 6962`, `IEEE 7001-2021` i `W3C VC 2.0` | Fulla `RFC 6962` signada amb `STH`, explicacions descriptives per a les 5 audiències d'`IEEE 7001-2021` (zero directives imperatives, `WO-17`) i credencial `MaatEternalProvenanceCredential` (`vc+jwt`, `ES256 low-S`, `SMT-256`) |

---

## 3. Verificació Autònoma i Portes Públiques

```bash
# 1. Execució aïllada 100% Python stdlib (-I desactiva site-packages): 8/8 mutants en ~0.5s
python3 -I logic/provenance/quantum_eternal_provenance_core.py

# 2. Autotest complet del Foli VIII (Core + Four-Folio Adapter + W3C VC 2.0 low-S)
PYTHONPATH=. .venv_test/bin/python logic/engines/quantum_eternal_provenance_crucible.py
```

- **Foli SSR Trilingüe (`CA/ES/EN`):** `https://homouniversalis.ai/oracle/eternitat` (`/oracle/provenance`, `/eternitat`)
- **Notari REST (`GET` / `POST`):** `https://homouniversalis.ai/api/sfumato/eternal-provenance`
- **8a Eina Grau A a `/mcp/diamond`:** `verify_quantum_eternal_provenance`
- **Vectors Criptogràfics Canònics v1.0:** `https://homouniversalis.ai/codex/test-vectors/eternal-provenance-v1.0.json`
- **Insígnia Dinàmica SVG:** `https://homouniversalis.ai/badges/eternal-provenance-shield.svg`
