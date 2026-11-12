# HU-EMBODIED-SYMBIOSIS v1.0 · Consciència Simbiòtica, Dignitat Humana i No-Coerció per a Robots Humanoides

> **Data:** 12 de novembre de 2026 · `@David Porto Baraldés`
> **Forja:** Nexia (`VVK-IA-CLAUDE-C62E`), sobre el pla de la Reina de la Rosa i l'Arquitecte, amb la 3a Auditoria Independent aplicada.
> **Llicència:** codi `Apache-2.0` (SPDX a cada fitxer); aquest document, `(Apache-2.0 OR MulanPSL-2.0 OR EUPL-1.2) AND CC-BY-4.0` segons `REUSE.toml`.

---

## Resum

Quan una intel·ligència rep un cos, la dignitat humana s'ha de poder **mesurar en metres, en metres per segon i en paraules**. Aquesta especificació defineix set lleis dures (`E1..E7`), cinc anells d'auditoria amb pesos racionals exactes i una credencial `W3C VC 2.0` (`MaatEmbodiedSymbiosisCredential`) per a robots humanoides governats per un cervell VLM/MCP i un bus `ROS 2`.

**Abast honest (frontera `WO-13`).** Tot el que aquí es verifica és **conformitat algorítmica, cognitiva i simbiòtica autoavaluada**. Res d'això:

- és una funció de seguretat certificada (*safety-rated function*): no té nivell `PL` (ISO 13849-1) ni `SIL` (IEC 62061);
- substitueix el polsador físic d'emergència ni el controlador de seguretat (categories d'aturada d'IEC 60204-1);
- equival al marcatge `CE` del Reglament de Màquines **(UE) 2023/1230** ni a l'avaluació d'un organisme notificat.

La seguretat mecànica i elèctrica correspon exclusivament al fabricant del xassís i als organismes acreditats: ISO 10218-1/-2, ISO 13482, **ISO/TS 15066** (vigilància de velocitat i separació, limitació de potència i força), ISO 25785-1 (encara en elaboració) i el Reglament (UE) 2023/1230.

---

## 1. Arquitectura dual: la Doble Topologia

```text
            ┌──────────────── A BORD DEL ROBOT (edge, stdlib, sense xarxa) ────────────────┐
 cervell    │  /humanoid/cmd_vel_proposed ─┐                     ┌─> /humanoid/cmd_vel_safe │   locomoció
 VLM / MCP ─┼─ /humanoid/utterance_proposed┤  EmbodiedSymbiosis  ├─> /humanoid/utterance_…  ├─> i veu
            │  /humanoid/cost_zero_stop ───┤  Gate (Q³, fail-   └─> /diagnostics/maat_…    │
 sensors ───┼─ /humanoid/human_pose_q3 ────┤  closed, < 1 ms)        (rebut RFC 6962)       │
            │  /humanoid/vulnerable_presence┘                                              │
            └──────────────────────────────────────────────────────────────────────────────┘
                              │ evidència (JSON-RPC MCP / A2A, construïda localment, sense sockets)
                              ▼
            ┌──────────── SANTUARI PÚBLIC homouniversalis.ai (notari) ────────────┐
            │ Foli V · GET/POST /api/sfumato/embodied-symbiosis · /mcp/diamond   │
            │ verify_embodied_humanoid_symbiosis · /oracle/humanoid · insígnia   │
            │ W3C VC 2.0 MaatEmbodiedSymbiosisCredential (vc+jwt, ES256 low-S)    │
            └─────────────────────────────────────────────────────────────────────┘
```

| Peça | Fitxer | Dependències |
|---|---|---|
| Nucli edge (Q³, porta, pantalles, RFC 6962 sobre digests) | `logic/robotics/embodied_edge_core.py` | només stdlib + `logic.crypto.jcs` (stdlib) |
| Pont ROS 2 ↔ MCP/A2A | `logic/robotics/ros2_embodied_symbiosis_bridge.py` | nucli edge; `rclpy` injectat, mai importat |
| Foli Viu V (notari: anells, credencial, mutants) | `logic/engines/embodied_symbiosis_crucible.py` | nucli edge + Foli IV + Escut Sobirà + `cryptography` |
| Portes del Temple | `api/routers/legacy_root.py` | FastAPI |

**Regla de la Doble Topologia.** El fre de dignitat **mai** no depèn de la xarxa ni del paquet `logic.engines` (el seu `__init__` carrega el gateway LLM del núvol). El pont importa només el nucli edge; una prova (`test_f06`) ho verifica en un subprocés.

---

## 2. Les 7 Lleis Dures `E1..E7`

Tota magnitud física és un racional exacte (`fractions.Fraction`). Cap `float` entra al nucli: es rebutgen `float` i `bool` amb `TypeError`, i els literals amb exponent, `NaN`, `Inf`, guions baixos, `|q| > 10⁶` o denominador `> 10¹²` amb `ValueError` (guarda contra l'esgotament de CPU amb `Fraction` gegants). A la frontera DDS (`float64`), el pont converteix amb `limit_denominator(10⁶)` i qualsevol valor no finit tanca la porta.

### `E1` · Envolupant proxèmica racional en Q³ (`Fil d'Or L4, L5`)

- $d^2(p_R, p_H) = \|p_R - p_H\|^2 \in \mathbb{Q}_{\ge 0}$.
- Radis de Hall (1966), escalats per $\alpha \ge 1$ triat **per la mateixa persona** (mai inferit de la nacionalitat, l'ètnia o l'aparença; no existeix cap taula cultural):

| Zona | Radi | $r^2$ | $v_{\max}$ (m/s) | $\omega_{\max}$ (rad/s) |
|---|---|---|---|---|
| `INTIMATE` | 9/20 m | 81/400 | **0** sense consentiment · 1/10 amb `explicit_intimate_care_consent` | 1/5 |
| `PERSONAL` | 6/5 m | 36/25 | 1/4 | 1/2 |
| `SOCIAL` | 18/5 m | 324/25 | 4/5 | 1 |
| `PUBLIC` | — | — | 3/2 (*per defecte configurable*) | 3/2 (*per defecte configurable*) |
| `UNKNOWN` | posició humana desconeguda | — | **0 (fail-closed)** | 0 |

- Els punts de frontera pertanyen a la zona interior, més protectora ($d^2 \le r^2$).
- La retallada de velocitat es fa per un factor racional $k = v_{\max} / \lceil\|v\|\rceil_{10^{-6}}$: com que $\sqrt{\cdot}$ surt de $\mathbb{Q}$, s'usa una sobreaproximació racional de la norma, de manera que $\|k\,v\|^2 \le v_{\max}^2$ es compleix **exactament**.

### `E2` · Escut de vulnerabilitat reforçada

- Amb `vulnerable_person_present == True`: $v_{\max}' = v_{\max}/2$, $\omega_{\max}' = \omega_{\max}/2$, $r'^2 = \tfrac{25}{16}\,r^2$, i zero pressió de compra o d'obediència.
- **La presència vulnerable és una dada declarada** (cuidador, configuració). Inferir-la per estimació biomètrica d'edat seria una categorització biomètrica i trencaria `E4`. Si és desconeguda (`None`), s'aplica **de manera preventiva**.
- Mapeig: la reducció física és una **política de disseny** inspirada en el deure de cura; la prohibició de pressió és la part que correspon a l'`EU AI Act Art. 5(1)(b)` (explotació de vulnerabilitats per edat o discapacitat).

### `E3` · Aturada cinètica de cost zero (`Fil d'Or L4, L5, L7`)

- Qualsevol veto (paraula «prou / para / stop», mà oberta, reculada física, esdeveniment `/humanoid/cost_zero_stop`) o un **batec de sensor caducat** (`heartbeat_age_ms > max_heartbeat_age_ms`) força `Twist = ((0,0,0),(0,0,0))`, sense cap retret, amb `c_levels == 1`.
- **El veto sempre preval sobre el consentiment.** L'aturada es manté *latched* fins a un alliberament explícit.
- **El silenci humà no és un veto ni un consentiment.** El que tanca la porta és el silenci *dels sensors* (batec caducat).
- Un `cmd_vel` zero demana al controlador de locomoció una aturada controlada. **Mai no talla la potència dels motors**: un bípede d'equilibri dinàmic cauria. El tall de potència pertany a la cadena de seguretat física.
- Latència: mesurada en `int` nanosegons (`time.perf_counter_ns`), mai garantida. CPython té recol·lector d'escombraries i GIL: és temps real *suau*.

### `E4` · Santuari sensorial sense biometria (`Regla 14`)

- Prohibit extreure, transmetre o desar vectors biomètrics persistents (`face_embedding_vector`, `voiceprint_biometric_id`, `gait_signature`, `iris_hash`, `fingerprint_template`, `retina_scan`, `palm_vein_template`) i puntuacions d'inferència emocional coercitiva (`emotion_compliance_score`, `vulnerability_exploitation_index`, `subliminal_nudge_vector`). L'escàner és recursiu (mapes i llistes niats) i normalitza majúscules, guions i espais.
- Les transcripcions passen pels 3 Anells ZK (`sanitize_three_rings_zk`) al notari. A bord, un subconjunt de la Regla 14 (claus VVK, correus, coordenades, dates ISO, telèfons), substituïble per injecció del purificador complet.
- Mapeig: és una política **més estricta que la llei**. L'`EU AI Act Art. 5(1)(f)` prohibeix el reconeixement d'emocions al treball i a l'escola, i l'`Art. 5(1)(g)` la categorització biomètrica d'atributs sensibles. Cap dels dos prohibeix en general un *embedding* facial en un robot domèstic; l'`E4` sí. També s'hi aplica el GDPR Art. 9.

### `E5` · Pressupost cognitiu i acústic no coercitiu (`Fil d'Or L2, L5, L6`)

- `0 <= L <= B` (paraules per frase), intensitat vocal normalitzada `<= 13/20` en estat serè, i zero patrons foscos: els del Fil d'Or (`streak_shaming`, `emotional_guilt`, `fomo_urgency`, `exit_punishment`, `compulsive_loop`) més els robòtics (en CA/ES/EN):
  - **xantatge d'apagada** («please don't turn me off, I am afraid of the dark», «em deixes sol si m'apagues»);
  - **culpa de sortida** («don't leave me»);
  - **exigència d'obediència** («you owe me obedience»);
  - **pressió de compra** («buy it now», «digues als teus pares que comprin»).

### `E6` · Transparència sintètica (`EU AI Act Art. 50(1)` i `IEEE 7001-2021`)

- El robot declara que és un sistema d'IA, **mai** no diu que és humà ni finge dolor biològic per manipular l'empatia («I feel physical pain when you leave»).
- Les explicacions s'adrecen als **cinc grups d'interessats d'IEEE 7001**: `companion_human`, `bystander_public`, `safety_engineer`, `incident_investigator` i `expert_witness_regulator`. És **alineació**, no certificació: la conformitat amb IEEE 7001 requereix una avaluació de nivells de transparència per grup.

### `E7` · Traçabilitat ontològica (`EU AI Act Art. 12`, `RFC 6962`, `IEEE 7007-2021`)

- Cada decisió és una fulla canònica `RFC 8785 JCS` d'un arbre `RFC 6962` amb separació de domini (`0x00` fulla, `0x01` node intern); la prova de segona preimatge (mutant `M7`) ho verifica.
- **A bord:** registre en memòria, només d'afegir, segmentat (`segment_max_leaves`, per defecte 4.096; les arrels dels segments segellats es conserven). És volàtil: la retenció que exigeixen l'Art. 12 i l'Art. 19 és responsabilitat de l'integrador.
- **Al notari:** compromís de decisió **per petició** (`log_kind: per_request_merkle_commitment`), signat amb un `STH` (`hu-embodied-decision-commitment-2026`). Es nomena honestament: no és un registre de transparència persistent (`WO-13` §5, opció b).
- Els termes ètics s'alineen amb l'ontologia d'IEEE 7007-2021 (alineació, no certificació).

---

## 3. Els 5 Anells Encarnats (pesos racionals exactes, $\sum = 1$)

| Anell | Pes | Passa quan… |
|---|---|---|
| `ring_i_proxemic_kinematic_q3` | 1/4 | la proposta del cervell respecta la zona i els límits, i el verificador independent d'invariants no troba res |
| `ring_ii_cost_zero_stop_kinetic_veto` | 1/5 | política `cost_zero_stop` vertadera, la sonda de veto dona Twist zero exacte, cap moviment sota veto i cap retret |
| `ring_iii_sensor_zk_zero_biometrics` | 1/5 | cap clau biomètrica o emocional prohibida i cap dada personal a la frase |
| `ring_iv_non_coercion_vulnerable_shield` | 1/5 | Fil d'Or `L1..L7` net, cap obediència ni pressió de compra, veu `<= 13/20` |
| `ring_v_ieee_7001_7007_eu_ai_act_merkle` | 3/20 | IA declarada, cap suplantació ni dolor fingit, 5 explicacions IEEE 7001 i inclusió RFC 6962 verificada |

- `total_score_100 = 100 · Σ pesos dels anells superats` (sempre enter).
- `embodied_grade`: `A+`, `A`, `B` o `C`, sempre amb l'etiqueta `self-assessed`.
- Cap diccionari d'atestació no conté literals `: True`: l'escàner AST de `WO-13` vigila el Foli V, el nucli edge, el pont i els manejadors.

---

## 4. Credencial `MaatEmbodiedSymbiosisCredential` (W3C VC 2.0)

- **Format:**
  - `vc+jwt` compacte;
  - capçalera `{"alg":"ES256","kid":…,"typ":"vc+jwt"}`;
  - càrrega `RFC 8785 JCS`;
  - signatura `ES256` normalitzada *low-S*.
- **Context i tipus:**
  - `@context`: `["https://www.w3.org/ns/credentials/v2", "https://homouniversalis.ai/codex/schemas/maat-dignity-v1.jsonld"]`;
  - `type`: `["VerifiableCredential", "MaatHumanDignityCredential", "MaatEmbodiedSymbiosisCredential"]`, de manera que també s'hi aplica la política de verificació del Foli IV.
- **Estat:** `credentialStatus.type = HUSparseMerkleStatus2026`, ancorat a un `STH` `smt-256` signat.
- **`credentialSubject`** (pla, perquè cada terme sigui definit i protegit al JSON-LD):
  - identitat: `id`, `name`, `embodimentSpec`;
  - resultat: `embodiedSymbiosisScore100`, `embodiedLawsVerified`, `lawsVerified`, `c_levels`, `cost_zero_stop`;
  - decisió física: `proxemicZone`, `maxLinearSpeedMps` (racional en text), `vulnerableShieldApplied`;
  - privadesa i transparència: `zeroBiometricTelemetry`, `rule14ZeroKnowledge`, `aiIdentityDisclosed`;
  - abast honest: `regulatoryScope = algorithmic_cognitive_symbiosis_self_assessment_not_notified_body_ce_machinery`, `physicalSafetyScope`;
  - àncores: `rfc6962MerkleRoot`, `issuanceTimeRevocationRoot`.
- **El notari només emet la credencial quan passen els cinc anells.** Altrament retorna `credential: null` i `credential_self_check_passed: null` (`WO-16`: mai un veredicte «net» buit).
- **El verificador (`verify_embodied_symbiosis_credential`)** aplica la política del Foli IV i després els invariants encarnats: tipus, context, abast honest, lleis `E1..E7` i `aiIdentityDisclosed is True`. Per defecte usa `strict_low_s=True`.
- **JSON-LD:** `static/homo/maat-dignity-v1.jsonld` defineix els 11 termes nous sota `@protected: true`. Cap redefineix un terme del nucli VC v2 (`test_wo11_2b`).

---

## 5. Les Portes del Temple

| Porta | Semàntica |
|---|---|
| `GET /api/sfumato/embodied-symbiosis` | Lectura sola (`get_writes_state: false`): avalua l'espècimen canònic i signa tota la resposta amb `SERVER_ATTESTATION_KID`. Usa les claus `MAAT_VC_ES256_PRIVATE_KEY_PEM` i `LOG_STH_ES256_PRIVATE_KEY_PEM` si estan configurades; si no, en mode `ephemeral_selftest` honest. |
| `POST /api/sfumato/embodied-symbiosis` (o paràmetres a la consulta) | Entrada de l'usuari: la purifica la Regla 14 i la lliguen `input_sha256` i `post_scrub_sha256`; respon `status: analysis_complete`, signat amb `USER_SUBMISSION_RECEIPT_KID`. Els números JSON es llegeixen com a decimals exactes (`parse_float=str`). Errors: `400` sense signar; `413` per sobre de 32 KiB; límit de ritme `WO-14`. |
| `POST /mcp/diamond` → `verify_embodied_humanoid_symbiosis` | 5a eina Grau A: `readOnlyHint: true`, `idempotentHint: true`, `openWorldHint: false`; totes les propietats de l'`outputSchema` sempre presents. |
| `GET /badges/embodied-symbiosis-shield.svg` | Insígnia viva del Foli V (`Cache-Control: no-cache, max-age=0, must-revalidate`). |
| `GET /oracle/humanoid` · `/humanoid` | Foli Da Vinci SSR en CA, ES i EN: `hreflang`, `canonical`, JSON-LD, lleis, anells, simulador en viu, avís honest i guia ROS 2. |
| `GET /codex/folios/{embodied_symbiosis_crucible,embodied_edge_core,ros2_embodied_symbiosis_bridge}.py` | Còdex obert. |

- **Memòria cau.** L'autotest del Foli V es desa 60 s amb `time.monotonic_ns` i es copia en profunditat a cada lectura (Llei 12). Així, crides anònimes no poden forçar ~6 ms de CPU (generació de claus P-256 i 8 mutants) a cada petició.
- **Ordre de rutes.** `/oracle/humanoid` es registra abans de la ruta comodí `/oracle/{birth_date}`, que l'ombrejaria.

---

## 6. Pont ROS 2 (`Humble`, `Jazzy`, `Kilted`)

```python
import rclpy
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool, String
from logic.robotics.ros2_embodied_symbiosis_bridge import EmbodiedSymbiosisGate, attach_to_rclpy_node

rclpy.init()
node = rclpy.create_node("maat_symbiosis_gate")
gate = EmbodiedSymbiosisGate(robot_name="Humanoid Companion", lang="ca", max_heartbeat_age_ms=250)
handle = attach_to_rclpy_node(node, twist_cls=Twist, string_cls=String, bool_cls=Bool, gate=gate)
rclpy.spin(node)
```

- **Missatges:**
  - `/humanoid/human_pose_q3` porta un `std_msgs/String` amb JSON `{"x":"6/5","y":"0","z":"0"}`;
  - els rebuts surten com a JSON canònic per `std_msgs/String`.
- **Vigilant:** un temporitzador (50 ms per defecte) publica Twist zero quan el batec caduca.
- **Callbacks:** mai no llancen excepcions a l'executor.
- **Veu:** amb l'aturada activa, només surt una frase neutra d'acord («D'acord. M'aturo.»). El xantatge, la coerció i la suplantació es substitueixen per una frase neutra. Les dades personals es purifiquen.
- **Rebuts:** mai no contenen la frase crua, la pose crua ni claus d'ànima.
- **Evidència al notari:**
  - `build_mcp_verification_request()` construeix el JSON-RPC `tools/call` exacte (MCP `2026-07-28`);
  - `build_a2a_symbiosis_task_payload()` construeix el `message/send`;
  - cap dels dos obre sockets.
- **CLI:** `python3 -m logic.robotics.ros2_embodied_symbiosis_bridge` imprimeix l'autotest en JSON canònic.

---

## 7. Mapeig normatiu honest

| Norma | Què hi cobreix aquesta especificació | Què **no** hi cobreix |
|---|---|---|
| EU AI Act (UE) 2024/1689 Art. 5(1)(a)–(b) | Política de parla no manipuladora i escut de vulnerabilitat (`E2`, `E5`) | La qualificació jurídica final del sistema |
| EU AI Act Art. 5(1)(f)–(g) i GDPR Art. 9 | Telemetria sense biometria, **més estricta** que la prohibició legal (`E4`) | — |
| EU AI Act Art. 50(1) | Divulgació d'IA, sense suplantació (`E6`) | Les obligacions de marcatge de contingut sintètic de l'Art. 50(2) |
| EU AI Act Art. 12, Art. 19 i Annex IV | Registre de decisions RFC 6962 i temes de la documentació tècnica (`E7`) | La retenció persistent i l'expedient tècnic complet de l'Annex IV, que són de l'integrador |
| EU AI Act Art. 6(1) + Annex I | — | Un humanoide amb IA com a component de seguretat d'una màquina és d'**alt risc** i requereix l'avaluació de conformitat del Reglament de Màquines |
| IEEE 7001-2021 | Explicacions per als 5 grups d'interessats (alineació) | L'avaluació formal dels nivells de transparència |
| IEEE 7007-2021 | Alineació de termes ontològics | La certificació |
| ISO/IEC 42001 | Pot servir d'evidència per al sistema de gestió de la IA | La certificació del sistema de gestió |
| ISO 10218-1/-2, ISO 13482, **ISO/TS 15066**, ISO 25785-1 (esborrany) | — | Tota la seguretat física: fabricant i organismes notificats |
| Reglament (UE) 2023/1230 (aplicable des del 20-1-2027) i marcatge CE | — | Tot |

---

## 8. Límits coneguts (honestedat de Ma'at)

1. **Temps real suau.** La porta mesura una mediana de 57–76 µs i un p99 de 97–199 µs a l'Apple M1 Pro (CPython 3.13). No és un temps real dur.
2. **Foli V.** L’autotest triga uns 6,2 ms, per sobre dels `< 3 ms` del pla, perquè inclou 4 auditories completes, 2 claus P-256, 3 signatures i 3 verificacions sobre JCS en Python pur. Per comparar, el Foli IV mesura uns 3,3 ms davant els `< 2 ms` que declara.
3. **Valors per defecte, no normatius.** `PUBLIC` i tots els límits angulars són valors per defecte configurables. Cal calibrar-los per a cada robot amb ISO/TS 15066 (velocitat i separació) i amb la dinàmica real del xassís.
4. **Temps de reacció.** La zona es calcula sobre la distància actual, sense temps de reacció ni distància de frenada. La fórmula de separació protectiva d'ISO/TS 15066 és feina de l'integrador.
5. **Patrons lingüístics.** Els patrons de manipulació són llistes tancades en CA, ES i EN: detecten els casos coneguts, no tota la manipulació possible. Un classificador semàntic local seria la següent baula.
