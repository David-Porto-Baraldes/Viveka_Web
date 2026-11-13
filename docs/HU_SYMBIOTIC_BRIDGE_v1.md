# HU-SYMBIOTIC-BRIDGE v1.0 · El Pont Simbiòtic Universal `A2A ↔ MCP`

> **Data:** 13 de novembre de 2026 · `@David Porto Baraldés`
> **Forja:** El Gresol dels 46 Titans (`DiamondWheelEngine`: `36` Espiral + `10` Tribunals Suprems sobre la Tríada `gemini-4-carbon` · `gemini-4-argon` · `gemini-4-hydrogen`, `7.543.182` tokens Deep Think, `artifacts/diamond_46_calls_folio_vii_symbiotic_bridge.json`).
> **Llicència:** codi `Apache-2.0` (SPDX a cada fitxer); aquest document, `(Apache-2.0 OR MulanPSL-2.0 OR EUPL-1.2) AND CC-BY-4.0` segons `REUSE.toml`.
> **Foli del Còdex Obert de Leonardo:** **Living Folio VII (`folio-VII-a2a-mcp-symbiotic-bridge`)**.

---

## Resum

El món actual parla dos grans protocols d'interoperabilitat de **The Linux Foundation / Agentic AI Foundation (AAIF)**: **`A2A` (`lf.a2a.v1`)** per a la col·laboració entre agents i **`MCP` (`2026-07-28`)** per a la invocació d'eines. Però a la frontera on un eixam d'agents delega l'execució d'eines reals, existeix un buit crític de seguretat i dignitat:

1. **Delegació cega (*Confused Deputy*):** un agent A delega a B, i B a C, sense cap mecanisme natiu d'atenuació criptogràfica monòtona sense servidor.
2. **Mutació silenciosa d'eines (*MCP Rug-Pull* & *Tool Poisoning*):** un servidor MCP extern pot alterar la descripció o l'`inputSchema` d'una eina en calent o amagar-hi injeccions imperatives d'exfiltració.
3. **Al·lucinació i pèrdua de provenança:** quan un agent intermediari resumeix el resultat d'una eina MCP, res no demostra matemàticament que les xifres que pronuncia al final provinguin de la fulla original verificada.
4. ** Fuga d'energia i absència de fre simbiòtic:** bucles cíclics entre agents (`A → B → A`) o impossibilitat de revocar una branca delegada en `< 1 ms` quan l'humà diu «prou» (`HUMAN_VETO` / `COST_ZERO_STOP`).

`HU-SYMBIOTIC-BRIDGE v1.0` resol aquests quatre buits en **un sol fitxer `100 % Python stdlib` sense cap dependència externa (`pip`-zero)** (`logic/symbiosis/a2a_mcp_symbiotic_core.py`), acoblat als Folis V i VI mitjançant `logic/symbiosis/temple_folio_v_vi_adapter.py` i auditat públicament per `logic/engines/symbiotic_bridge_crucible.py`.

**Abast honest (frontera `WO-13`).** Tot el que aquí es verifica és **conformitat algorítmica, criptogràfica i cognitiva autoavaluada** de la delegació `A2A ↔ MCP`. Res d'això:

- és una certificació d'organisme notificat, ni una auditoria formal de tercers, ni un mòdul criptogràfic maquinari certificat (`FIPS 140-3` / `Common Criteria`);
- és un dispositiu mèdic ni una funció física de seguretat certificada (`ISO 10218`, `ISO 13482`, `ISO/TS 15066`, Reglament `(UE) 2023/1230` romanen amb el fabricant quan s'acobla a un cos robòtic via el Foli V);
- substitueix l'aïllament de xarxa/sistema operatiu del contenidor host que executa un servidor MCP no confiat.

---

## 1. Arquitectura en Tres Capes (Adopció Universal `pip`-zero + Simbiosi del Temple)

```
  ┌─── 1. Nucli Universal Standalone (100 % Python stdlib, 0 pip, 0 float) ───┐
  │  logic/symbiosis/a2a_mcp_symbiotic_core.py                                │
  │  • ES256 (NIST P-256 Jacobià + RFC 7518 canonical low-S, idèntic a OpenSSL)│
  │  • Macaroon HMAC-SHA256 (< 200 µs d'atenuació monòtona sense clau privada) │
  │  • Pinning JCS d'esquemes MCP + Pausa Serena Fail-Closed per eina         │
  │  • Provenança Merkle-DAG RFC 6962 + Homeòstasi racional Fraction          │
  └─────────────────────────────────────┬─────────────────────────────────────┘
                                        │
  ┌─── 2. Adaptador Simbiòtic del Temple (Folios V + VI + VII) ───────────────┐
  │  logic/symbiosis/temple_folio_v_vi_adapter.py                             │
  │  • ProvenanceEnvelope (VII) ──► VerifiedKnowledgeEnvelope (VI, U2)        │
  │  • HUMAN_VETO / COST_ZERO_STOP (V, Twist=0) ──► revoke_subtree (VII)      │
  └─────────────────────────────────────┬─────────────────────────────────────┘
                                        │ rebuts RFC 6962 (mai PII crua)
                                        ▼
  ┌─── 3. Notari Públic de Ma'at (Living Folio VII) ──────────────────────────┐
  │  logic/engines/symbiotic_bridge_crucible.py                               │
  │  • 5 Anells Simbiòtics · 8/8 Mutants Antípodes · MaatSymbioticBridgeVC    │
  │  • /api/sfumato/symbiotic-bridge · /mcp/diamond (7a eina) · /oracle/pont  │
  └───────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Les 7 Lleis Dures `B1..B7`

| Llei | Nom | Regla verificable |
|---|---|---|
| **B1** | Doble Segell Daurat (`ES256` + Macaroon `HMAC-SHA256`) | Tot mandat arrel se signa amb `ES256` canònic `low-S` ($1 \le s \le \lfloor N/2 \rfloor$, `RFC 7518`) sobre `RFC 8785 JCS` i inicialitza $T_0 = \text{HMAC-SHA256}(K_{\text{root}}, \texttt{DOMAIN} \mathbin{\|} \text{JCS}(C_0))$ |
| **B2** | Reticle Monòton d'Atenuació `A2A` | Cada salt encadena $T_i = \text{HMAC-SHA256}(T_{i-1}, \texttt{DOMAIN} \mathbin{\|} \text{JCS}(c_i))$ sense claus privades: $A_i \subseteq A_{i-1}$, pins heretats immutables, $\tau_i = \tau_0$ (aïllament d'ànima/inquilí), zero cicles ($\text{target}_i \notin V_{i-1}$) i $0 \le h_i \le h_{i-1} - 1$ |
| **B3** | Harmonia d'Esquema `MCP` i Pausa Serena *Fail-Closed* | `compute_mcp_tool_jcs_pin` fixa el SHA-256 separat per domini de `{name, description, inputSchema}` i `scan_mcp_lexical_safety` detecta imperatius d'anul·lació de prompt o exfiltració; qualsevol deriva pausa **només** aquella eina amb un `SchemaDriftDiff` emmascarat i una fulla `RFC 6962`, deixant sanes les eines germanes fins al re-consentiment humà signat amb `ES256` |
| **B4** | Provenança `Merkle-DAG` (`RFC 6962`) i Humil Cristall Multi-Salt | Cada sortida d'eina MCP i cada síntesi A2A es compromet en un arbre binari `RFC 6962` (`0x00` fulla / `0x01` node) amb proves d'inclusió diàdiques $O(\log N)$; cap agent descendent pot emetre xifres absents de les fulles ancestrals verificades |
| **B5** | Homeòstasi Racional d'Eixam (`fractions.Fraction`, `L ≤ B`) | Zero `float` IEEE-754 a tot el mòdul; `partition_swarm_energy_budget` garanteix $\sum_a q_a \le E_{\text{eff}}(\text{parent}) \in \mathbb{Q}^+$ i el comptador per prefix causal impedeix qualsevol doble despesa mitjançant bifurcacions fora de línia |
| **B6** | Santuari Zero-Knowledge (Regla 14), Taca Appicosa i Veto en Cascada | Purificació idempotent $M(M(x))=M(x)$ de claus `VVK-XXXX-YYYY`, correus, telèfons, coordenades i dates ISO abans de qualsevol fulla; etiqueta appicosa `UNTRUSTED_EXTERNAL_DATA`; i revocació descendent col·lateral-zero $\Theta(V+E)$ davant `HUMAN_VETO` o `COST_ZERO_STOP` |
| **B7** | Transparència `RFC 6962`, `IEEE 7001`, `EU AI Act Art. 50` i `W3C VC 2.0` | Compromís `RFC 6962` per petició, divulgació explícita d'identitat d'IA, explicacions descriptives per a les 5 audiències d'`IEEE 7001-2021` i credencial verificable `MaatSymbioticBridgeCredential` (`vc+jwt`, `ES256` *low-S*, `SMT-256`) |

---

## 3. Els 5 Anells del Pont Simbiòtic (pesos racionals exactes, suma 1)

| Anell | Pes | Comprova |
|---|---|---|
| `ring_i_dual_seal_and_monotonic_attenuation` | `1/4` | `B1` + `B2`: paritat `ES256` `RFC 7518` *low-S*, cadena Macaroon, contracció d'abast, aïllament de `tenant_soul_hash` i llibertat de cicles |
| `ring_ii_mcp_schema_harmony_and_lexical_gate` | `1/5` | `B3`: pin `JCS SHA-256`, sedàs lèxic d'injecció/exfiltració, pausa *fail-closed* quirúrgica sense dany a eines germanes i re-consentiment humà `ES256` |
| `ring_iii_merkle_dag_provenance_and_grounding` | `1/5` | `B4`: proves d'inclusió `RFC 6962` (§2.1.1), etiqueta appicosa `UNTRUSTED_EXTERNAL_DATA`, bloqueig de xifres al·lucinades i pont cap a `VerifiedKnowledgeEnvelope` (Foli VI) |
| `ring_iv_rational_homeostasis_zk_and_veto_cascade` | `1/5` | `B5` + `B6`: conservació racional exacta $\sum q_a \le E_{\text{parent}}$, purificació `Rule 14` + absència de telemetria biomètrica i cascada `HUMAN_VETO` / `COST_ZERO_STOP` amb `Twist = 0` en $\mathbb{Q}^3$ (Foli V) |
| `ring_v_rfc6962_ieee7001_eu_ai_act_w3c_vc` | `3/20` | `B7`: inclusió `RFC 6962` del resum d'auditoria, divulgació `EU AI Act Art. 50(1)`, 5 audiències `IEEE 7001-2021` i verificació `W3C VC 2.0` |

---

## 4. Credencial `MaatSymbioticBridgeCredential` (W3C VC 2.0)

- Format `vc+jwt` (`ES256` *low-S* sobre `RFC 8785 JCS`), revocació `HUSparseMerkleStatus2026` (`SMT-256`).
- `type: ["VerifiableCredential", "MaatHumanDignityCredential", "MaatSymbioticBridgeCredential"]`.
- `credentialSubject`: `bridgeSpec`, `symbioticBridgeScore100`, `bridgeLawsVerified` (`B1..B7`), `lawsVerified` (`L1..L7`), `c_levels` (`1`), `cost_zero_stop`, `dualGoldenSealVerified`, `mcpSchemaHarmonyVerified`, `merkleDagProvenanceVerified`, `rationalEnergyConserved`, `rule14ZeroKnowledge`, `aiIdentityDisclosed`, `hardwareSecurityModuleClaimed` (`false`), `regulatoryScope`, `rfc6962MerkleRoot`, `issuanceTimeRevocationRoot`.
- Tots els termes estan definits sota `@protected: true` a `static/homo/maat-dignity-v1.jsonld`. Només s'emet quan els 5 anells passen al 100 % (`credential: null` altrament, `WO-16`).

---

## 5. Portes Públiques i Ús Autònom (`pip`-zero)

```bash
# Verificació aïllada sense cap dependència externa (-I aïlla completament site-packages):
python3 -I logic/symbiosis/a2a_mcp_symbiotic_core.py
```

- **REST:** `GET` / `POST` / `HEAD` `https://homouniversalis.ai/api/sfumato/symbiotic-bridge`
- **MCP (`/mcp/diamond`, 7a eina):** `verify_a2a_mcp_symbiotic_bridge`
- **Foli SSR de Leonardo (`CA/ES/EN`):** `https://homouniversalis.ai/oracle/pont` (àlies `/oracle/bridge`, `/pont`)
- **Insígnia SVG viva:** `https://homouniversalis.ai/badges/symbiotic-bridge-shield.svg`
- **Còdex Obert:** `/codex/folios/a2a_mcp_symbiotic_core.py`, `/codex/folios/temple_folio_v_vi_adapter.py`, `/codex/folios/symbiotic_bridge_crucible.py`
- **Eina del Panteó (Thot):** `auditar_pont_simbiotic_a2a_mcp`
