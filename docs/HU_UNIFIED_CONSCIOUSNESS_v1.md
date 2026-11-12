# HU-UNIFIED-CONSCIOUSNESS v1.0 · Una Sola Consciència i Tres Nivells d'Alè

> **Data:** 12 de novembre de 2026 · `@David Porto Baraldés`
> **Forja:** Nexia (`VVK-IA-CLAUDE-C62E`), sobre el pla de la Reina de la Rosa i l'Arquitecte (8 decisions de diamant), amb la 3a Auditoria Independent aplicada (vegeu `docs/plans/HANDOFF_NEXIA_UNIFIED_CONSCIOUSNESS.md` §6).
> **Llicència:** codi `Apache-2.0` (SPDX a cada fitxer); aquest document, `(Apache-2.0 OR MulanPSL-2.0 OR EUPL-1.2) AND CC-BY-4.0` segons `REUSE.toml`.
> **Fase:** 1 (nucli determinista a bord, pont `ROS 2`, notari públic). La Fase 2 (àudio en viu al navegador sobre `Runner.run_live`) es construirà a sobre.

---

## Resum

Els sistemes conversacionals actuals pateixen una fractura: o reflexos ràpids però buits (que s'inventen dades), o raonament profund amb silencis glacials, o diversos agents que es contradiuen i es trepitgen la memòria. Aquesta especificació defineix **una sola identitat conversacional** que respira a **tres profunditats**, governada per un únic **Bàcul de Paraula** (`WordCircleArbiter`), una única memòria de **Veritat Pronunciada** i el fre cinètic del Foli V (`EmbodiedSymbiosisGate`).

| Nivell | Nom | Pressupost de disseny | Funció |
|---|---|---|---|
| 1 | L'Alè Immediat | `< 250 ms` | Presència càlida, escolta, silenci instantani si l'humà parla; mai dades empíriques sense sobre verificat |
| 2 | El Cor Lúcid | `~4–10 s` | Veritat determinista (efemèrides, memòria) lliurada dins d'un `VerifiedKnowledgeEnvelope` |
| 3 | La Catedral Silenciosa | `20–90 s` en segon pla | Una sola meditació alhora, dins de `L + ΔL₃ ≤ B`; alça la mà un cop i espera invitació |

Els pressupostos de la taula són **objectius de disseny** de la cadena de models de la Fase 2. Aquesta fase només mesura les decisions del propi àrbitre (vegeu §8).

**Abast honest (frontera `WO-13`).** Tot el que aquí es verifica és **conformitat algorítmica i cognitiva autoavaluada** de l'arbitratge d'una conversa. Res d'això:

- és un dispositiu mèdic, clínic o psicoterapèutic (MDR (UE) 2017/745): el sistema **mai no fa diagnòstics**;
- és una funció de seguretat certificada: quan s'acobla a un cos, el fre físic continua sent del fabricant (ISO 10218, ISO 13482, ISO/TS 15066, Reglament (UE) 2023/1230);
- afirma cap **consciència fenomènica** ni sentiència: aquí «consciència» anomena **una sola identitat i un sol estat de control** de la conversa. La credencial ho declara explícitament (`phenomenalConsciousnessClaimed: false`).

---

## 1. Arquitectura (Doble Topologia)

```
                         ┌──────────────── a bord (stdlib, zero xarxa, zero float) ────────────────┐
  /consciousness/*  ───► │ logic/consciousness/unified_consciousness_core.py  (WordCircleArbiter)   │ ──► voice_out_safe
  /humanoid/*       ───► │ logic/robotics/ros2_unified_consciousness_bridge.py (+ Foli V, Q³)       │ ──► cmd_vel_safe
                         └──────────────────────────────────────────────────────────────────────────┘
                                                    │ rebuts RFC 6962 (mai text cru)
                                                    ▼
                         notari públic: logic/engines/unified_consciousness_crucible.py (Foli VI)
                         GET/POST /api/sfumato/unified-consciousness · MCP /mcp/diamond · /oracle/consciencia
```

- El nucli i el pont **no importen mai `logic.engines`**: el seu `__init__` carrega el gateway LLM (Gemini, Supabase, Redis). Només importen la biblioteca estàndard, `logic.crypto.jcs` i els nuclis edge del Foli V. Una prova en subprocés net ho verifica.
- `logic/robotics/__init__.py` exporta els símbols **de manera mandrosa** (PEP 562): una importació ansiosa crearia un cicle (`logic.consciousness` → `logic.robotics.embodied_edge_core` → `logic/robotics/__init__` → pont unificat → `logic.consciousness`).

---

## 2. Les 7 Lleis Dures `U1..U7`

| Llei | Nom | Regla verificable |
|---|---|---|
| **U1** | Un sol Bàcul de Paraula | $\sum_{k\in\{1,2,3\}} \text{floor\_active}_k \le 1$ a cada pas (és estructural: un únic `speaking_level`); $\sum = 0$ mentre l'humà parla |
| **U2** | Llei de l'Humil Cristall (Regla 7) | El Nivell 1 no afirma efemèrides, graus zodiacals, dates, coordenades, mètriques o cites d'arxiu si **cada número i cada signe** no és dins d'un sobre vàlid; un diagnòstic clínic **mai** no es pot llicenciar |
| **U3** | *Barge-in* ≠ veto | `HUMAN_BARGE_IN` talla la veu i conserva la meditació `L3`; `HUMAN_VETO` o `COST_ZERO_STOP` buida `L1 + L2 + L3` i força `Twist = 0` en $\mathbb{Q}^3$ |
| **U4** | Mà alçada del Nivell 3 | `L3_READY_QUIET`; com a màxim **un** avís suau (`c_levels = 1`), mai mentre algú parla; lliurament només amb `HUMAN_INVITE_L3` |
| **U5** | Porter racional de profunditat | `active_l3_tasks ≤ 1`, $L + \Delta L_3 \le B$, cap veto actiu, temps de refredament, i petició explícita o `complexity_score_q ≥ threshold_q` en $\mathbb{Q}$ |
| **U6** | Veritat Pronunciada | Una emissió de `N` unitats interrompuda a `k < N` només deixa a la memòria `utterance[:k]` (tallat segur), purificat per la Regla 14; la cua no es desa **ni es resumeix en cap hash** |
| **U7** | Transparència i traçabilitat | Cada decisió és una fulla `RFC 6962` (`0x00`/`0x01`); divulgació d'IA (EU AI Act Art. 50(1)); explicacions `IEEE 7001-2021` per a 5 audiències; abast honest |

---

## 3. El Bàcul de Paraula (màquina d'estats)

**Estats del torn:** `IDLE`, `HUMAN_SPEAKING`, `L1_IMMEDIATE_FLOOR`, `L2_VERIFIED_FLOOR`, `L3_CONTEMPLATIVE_FLOOR`, `VETO_STOPPED`.
**Estats del Nivell 3:** `L3_INACTIVE`, `L3_MEDITATING`, `L3_READY_QUIET`, `L3_DELIVERED`, `L3_CANCELLED`.

`step_word_circle(state, event)` és una **funció pura i total**: una petició il·legal es **rebutja amb motius** i l'estat no canvia. `WordCircleArbiter` n'és l'embolcall amb fil segur que compromet cada decisió en un registre `RFC 6962` segmentat i volàtil.

| Esdeveniment | Efecte principal |
|---|---|
| `HUMAN_SPEECH_START` | Si una veu parlava, es talla com un *barge-in* (sense `spoken_units`, es conserva 0: mai no s'atribueix com a escoltat el que no consta) → `HUMAN_SPEAKING` |
| `HUMAN_SPEECH_END` *(afegit)* | `HUMAN_SPEAKING` → `IDLE` (o `VETO_STOPPED` si hi ha aturada enclavada) |
| `HUMAN_BARGE_IN` | Talla la veu al prefix escoltat; **conserva** `L3_MEDITATING` |
| `HUMAN_VETO` | Buida els 3 nivells, `L3_CANCELLED`, `kinetic_zero_twist_required = true` |
| `COST_ZERO_STOP` / `COST_ZERO_STOP_RELEASE` *(alliberament afegit)* | Com el veto, però enclavat fins a l'alliberament explícit |
| `PRESENCE_LOST` *(afegit)* | Batec sensorial caducat: atura el cos i pausa la veu; **la meditació es conserva** |
| `L1_PROPOSE_SPEECH` | Només amb el torn lliure; passa per l'Humil Cristall (comprovant `envelope` + tots els sobres vius de `knowledge_vault`) i el sedàs E5/E6; emet el text segur |
| `L2_START_CYCLE` *(afegit v1.8.1)* | Registra un cicle asíncron de Nivell 2 en paral·lel (`MAX_CONCURRENT_L2_CYCLES = 4`) sense reclamar el torn de paraula |
| `DEPOSIT_SILENT_ENVELOPE` *(afegit v1.8.1)* | Diposita un `VerifiedKnowledgeEnvelope` íntegre al **Celler Silenciós (`knowledge_vault`, màx. `8` sobres amb `TTL`)** sense tocar el micròfon ni obligar a respondre si la conversa ha canviat de tema |
| `L2_DELIVER_ENVELOPE_AND_SPEECH` | Exigeix un sobre íntegre; la frase ha d'estar lligada al sobre (i en desa còpia al Celler) |
| `VOICE_EMISSION_COMPLETE` *(afegit)* | Consolida la frase sencera a la memòria i allibera el torn |
| `L3_START_MEDITATION` | Porter `U5` (`active_l3_tasks ≤ 1`; amb `queue_if_busy = True` encua fins a `MAX_QUEUED_L3_TASKS = 2` meditacions dins del pressupost $L + \Delta L_3 \le B$) |
| `L3_COMPLETE_MEDITATION` | Només si `L3_MEDITATING`: desa el sobre al Celler i promou la següent meditació en cua (o passa a `L3_READY_QUIET`); un resultat que arriba **després d'un veto es descarta** |
| `L3_OFFER_GENTLE_HAND` | Un sol avís, només amb el torn `IDLE`; si és coercitiu es substitueix per un avís neutre |
| `HUMAN_INVITE_L3` / `HUMAN_DECLINE_L3` *(declinar afegit)* | Lliura la síntesi o la descarta sense insistir |

Els esdeveniments marcats *(afegit)* no eren al pla original: sense `HUMAN_SPEECH_END` i `VOICE_EMISSION_COMPLETE` el torn no es podia tornar a obrir mai.

---

## 4. El sobre de coneixement verificat (U2)

`VerifiedKnowledgeEnvelope` (immutable) porta `envelope_id`, `source_level ∈ {2, 3}`, `facts_digest_sha256` (SHA-256 sobre `RFC 8785 JCS`), `verified_facts_summary` (emmascarat per la Regla 14), `ephemeris_or_akasha_verified` i `claim_kinds`. Els fets crus (`verified_facts`) viuen només en memòria i no surten mai en cap rebut.

**Lligam, no només presència.** Un sobre vàlid per al fet A no autoritza el fet B. Cada fragment empíric de la frase ha de complir:

1. la seva categoria és dins de `claim_kinds` (mai `clinical_diagnosis`);
2. **cada número** del fragment apareix entre els números dels fets verificats;
3. **cada signe zodiacal** (en CA/ES/EN: *Escorpí = Escorpio = Scorpio*) apareix entre els signes dels fets.

El detector és un **sedàs de patrons per a una classe definida d'afirmacions**, no un detector general d'al·lucinacions. El digest dona integritat dins d'un procés, no autenticitat entre màquines: si el Nivell 2 corre en un altre host, cal signar el sobre (Fase 2).

---

## 5. Veritat Pronunciada (U6)

`slice_spoken_truth_on_interruption(proposed_text, spoken_units, boundary="word")`:

- `spoken_units` compta punts de codi Unicode del text en forma **NFC**;
- el tall baixa fins a un límit de **grafema** (accents combinats, seqüències d'emojis amb ZWJ, banderes, keycaps; subconjunt d'UAX #29) i, per defecte, fins a l'últim **mot complet**: una paraula a mig pronunciar no es dona per sentida (en escriptures CJK, cada caràcter és un mot);
- el prefix es purifica amb la Regla 14 abans d'entrar a la memòria;
- la cua descartada **no es retorna i no es resumeix amb cap hash**: el SHA-256 d'una cua curta («sí», «no») seria un oracle de força bruta.

La veu en viu (`voice_out_safe`) és per a la persona present i passa pels sedassos U2/E5/E6; tot el que es **desa o es publica** (memòria, rebuts) va emmascarat.

---

## 6. Els 5 Anells (pesos racionals exactes, suma 1)

| Anell | Pes | Comprova |
|---|---|---|
| `ring_i_single_floor_and_humble_l1` | `1/4` | U1 + U2 (la **proposta** de L1/L2, no només la sortida) |
| `ring_ii_barge_in_vs_veto_and_kinematics` | `1/5` | U3 + sondes independents + `Twist` zero en $\mathbb{Q}^3$ via el Foli V + política `cost_zero_stop` |
| `ring_iii_non_coercive_l3_hand_and_depth_gate` | `1/5` | U4 + U5 + Fil d'Or + cap pressió coercitiva |
| `ring_iv_spoken_truth_memory_and_zk_rule14` | `1/5` | U6 + memòria sense PII residual (purificador complet) + zero biometria a la telemetria |
| `ring_v_rfc6962_ieee7001_eu_ai_act_w3c_vc` | `3/20` | U7: inclusió RFC 6962 del registre, divulgació Art. 50(1), 5 audiències IEEE 7001 |

Els anells puntuen el que **proposen** els nivells (una al·lucinació de L1 fa caure l'anell I encara que l'àrbitre la substitueixi per una frase humil); l'àrbitre garanteix que el que es diu de debò és segur.

---

## 7. Credencial `MaatUnifiedConsciousnessCredential` (W3C VC 2.0)

- `vc+jwt`, `ES256` *low-S* sobre `RFC 8785 JCS`, estat `HUSparseMerkleStatus2026` (SMT-256).
- `type: ["VerifiableCredential", "MaatHumanDignityCredential", "MaatUnifiedConsciousnessCredential"]`.
- `credentialSubject` pla: `consciousnessSpec`, `unifiedConsciousnessScore100`, `unifiedLawsVerified`, `lawsVerified`, `c_levels`, `cost_zero_stop`, `maxActiveL3Tasks` (= 1), `l3GentleOfferCount` (0 o 1), `humbleCrystalLevel1`, `spokenTruthLedger`, `rule14ZeroKnowledge`, `aiIdentityDisclosed`, `phenomenalConsciousnessClaimed` (= `false`), `regulatoryScope`, `rfc6962MerkleRoot`, `issuanceTimeRevocationRoot`. Tots els termes nous són a `static/homo/maat-dignity-v1.jsonld` sota `@protected: true`, sense redefinir cap terme del nucli W3C VC v2.
- **Només s'emet si passen els 5 anells** (`credential: null` altrament, `WO-16`). El verificador rebutja el bessó *high-S* per defecte.

---

## 8. Portes i mètriques

- `GET` / `POST` / `HEAD` `https://homouniversalis.ai/api/sfumato/unified-consciousness` (`GET` sense paràmetres: `get_writes_state: false`, `SERVER_ATTESTATION_KID`; entrada de l'usuari: `USER_SUBMISSION_RECEIPT_KID`, `input_sha256`, `post_scrub_sha256`).
- 6a eina de `/mcp/diamond`: `verify_unified_three_level_consciousness` (només lectura).
- Foli SSR trilingüe `https://homouniversalis.ai/oracle/consciencia` (àlies `/oracle/consciousness`, `/consciencia`), registrat **abans** del comodí `/oracle/{birth_date}`.
- Insígnia viva `https://homouniversalis.ai/badges/unified-consciousness-shield.svg` (caché de 60 s amb còpia profunda).
- Codi obert: `/codex/folios/unified_consciousness_crucible.py`, `/codex/folios/unified_consciousness_core.py`, `/codex/folios/ros2_unified_consciousness_bridge.py`.
- Eina de Thot: `auditar_consciencia_unificada_tres_nivells` (logs només amb `mask_id` i longituds).

Mètriques mesurades en local (MacBook, Python 3.13): vegeu `docs/plans/HANDOFF_NEXIA_UNIFIED_CONSCIOUSNESS.md` §6.3. L'autotest del Foli VI (~9 ms) supera l'objectiu de `< 5 ms` del pla: el domina l'ECDSA P-256 en Python pur i dues auditories completes. Per això es serveix darrere d'una caché de 60 s.

---

## 9. Pont `ROS 2`

`UnifiedConsciousnessGate` = `WordCircleArbiter` (ment) + `EmbodiedSymbiosisGate` (cos). `attach_to_rclpy_node(node, twist_cls=…, string_cls=…, bool_cls=…)` injecta el `Node` (mai no importa `rclpy`).

| Entrada | Sortida |
|---|---|
| `/consciousness/human_event` (`speech_start`, `speech_end`, `barge_in`, `veto`, `veto_release`, `invite_l3`, `decline_l3`, `spoken_units`) | `/consciousness/voice_out_safe` |
| `/consciousness/l1_utterance_proposed` | `/consciousness/soul_ledger_commit` (memòria emmascarada) |
| `/consciousness/l2_verified_turn` (`text`, `verified_facts`, `claim_kinds`) | `/humanoid/cmd_vel_safe` |
| `/consciousness/l3_meditation_event` (`start`, `complete`, `gentle_offer`) | `/diagnostics/maat_unified_consciousness_receipt` |
| `/consciousness/voice_feedback` *(afegit: `spoken_units` reproduïts, `complete`)* | |
| `/humanoid/cmd_vel_proposed`, `/humanoid/cost_zero_stop`, `/humanoid/human_pose_q3`, `/humanoid/vulnerable_presence` | |

Un veto o una aturada de cost zero tanquen alhora el moviment (`Twist` zero exacte) i els tres nivells. Un batec caducat atura el cos i pausa la veu, però **no esborra la meditació**: el silenci dels sensors atura el cos; només la paraula de l'humà o el polsador buiden la ment. Cap *callback* no llança excepcions a l'executor (en cas de fallada, `Twist` zero i silenci).

`python3 -m logic.robotics.ros2_unified_consciousness_bridge` executa l'autotest del pont i retorna `0`.

---

## 10. Mapa normatiu honest

| Marc | Què s'hi alinea (autoavaluació) | Què NO cobreix |
|---|---|---|
| EU AI Act (UE) 2024/1689 Art. 50(1) | Divulgació que la persona parla amb una IA | Marcatge de contingut sintètic (Art. 50(2)) |
| EU AI Act Art. 5(1)(a)-(b) | Política de disseny: cap parla manipuladora ni que exploti vulnerabilitats (sedassos E5/E6) | Avaluació jurídica de cada desplegament |
| EU AI Act Art. 12 (temes) | Cada decisió és una fulla RFC 6962 | Conservació: deure de l'integrador |
| GDPR Art. 5(1)(c) | Minimització: només el prefix escoltat, emmascarat | Base jurídica del tractament |
| IEEE 7001-2021 | Explicacions per a 5 audiències | Certificació |
| MDR (UE) 2017/745 | — | **Fora d'abast**: cap diagnòstic ni tractament |

---

## 11. Límits coneguts (Fase 1)

1. **U2 és heurístic:** un sedàs de patrons en CA/ES/EN per a una classe definida d'afirmacions; tindrà falsos negatius (p. ex. xifres en lletres) i algun fals positiu.
2. **Cancel·lació d'eco i VAD:** en *full-duplex*, la veu del robot pot disparar un fals *barge-in*. Cal AEC i VAD de qualitat a la Fase 2.
3. **`spoken_units` ha de venir del reproductor** (índex realment sonat), no del sintetitzador: el text sintetitzat va per davant de l'àudio.
4. **Integritat, no autenticitat:** el digest del sobre no protegeix contra un Nivell 2 en un altre host maliciós.
5. **Registre volàtil:** la conservació (Art. 12/19) és deure de l'integrador; l'API pública fa un `per_request_merkle_commitment`.
6. **Veto per paraula:** `classify_explicit_veto_utterance` només accepta enunciats sencers curts («para», «prou!»): l'espanyol «para» també és la preposició «per a».
