# HU-ROBOTIC-REGULATORY-PASSPORT v1.0 · Manual Oficial d'Integració (`EU AI Act Art. 13`), Caixa Negra (`Art. 12 & 19`), `CRA SBOM` i Frontera `ISO 25785 / Reg. (UE) 2023/1230`

> **Data:** 14 de novembre de 2026 · `@David Porto Baraldés` (`Homo Universalis — Viveka`)  
> **Portes Públiques Verificables:** `https://homouniversalis.ai/api/sfumato/robotic-passport` (`ES256` JWS) · `https://homouniversalis.ai/.well-known/sbom-robotics-edge.cdx.json` (`CycloneDX 1.6`)  
> **Codi Obert (`Apache-2.0`):** `logic/robotics/edge_blackbox_journal.py` · `logic/robotics/cra_sbom_manifest.py` · `logic/robotics/embodied_edge_core.py` · `logic/consciousness/unified_consciousness_core.py` · `logic/symbiosis/a2a_mcp_symbiotic_core.py`

---

## 0. Abast Honest (`WO-13` Boundary Declaration)

Aquest Passaport Normatiu Robòtic cobreix **exclusivament la capa de programari cognitiu, conversacional, proxèmic i criptogràfic autoavaluat** (*On-Board Embodied Consciousness Edge SDK* d'`Homo Universalis`).

**El que AQUEST SDK NO ÉS (i mai no declara ser):**
- **NO** és una funció de seguretat física certificada (*safety-rated function*): no atorga nivell `PL` (`ISO 13849-1`) ni `SIL` (`IEC 62061`).
- **NO** substitueix el controlador físic d'equilibri dinàmic bípede (`ISO 25785-1`), la limitació de força i potència (`ISO 10218-1:2025`, `ISO 13482`), ni la cadena física d'aturada d'emergència (`IEC 60204-1` Categoria 0/1).
- **NO** constitueix marcatge `CE` de maquinària ni certificació d'Organisme Notificat sota el **Reglament (UE) 2023/1230**.

---

## 1. Arquitectura de Dues Capes: Per què Qualsevol Fabricant de Robots pot Integrar la Consciència d'Homo Universalis sense Perdre el seu Marcatge `CE`

El **Reglament Europeu de Màquines `(UE) 2023/1230`** (aplicable a partir del **20 de gener de 2027**, Annex I) sotmet a avaluació obligatòria de tercers (Organisme Notificat) els *components de seguretat amb comportament totalment o parcialment autoevolutiu basat en aprenentatge automàtic*.

L'arquitectura d'`Homo Universalis` separa radicalment la **Consciència** del **Ferro**:

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│ CAPA 1 · CONSCIÈNCIA SIMBIÒTICA HOMO UNIVERSALIS (Python stdlib pur, Q³, < 1 ms)  │
│  • Foli VI (`WordCircleArbiter`): 3 Nivells d'Alè, silenci instantani i Cristall  │
│  • Foli VII (`Dual Golden Seal`): ES256 + Macaroons + Schema Harmony Gate         │
│  • Foli V (`EmbodiedSymbiosisGate`): Proxèmica racional Q³ + Veto -> Twist = 0    │
│  • Caixa Negra Art. 12/19 (`AppendOnlyDiskBlackBoxJournal`): >= 180 dies + E4/ZK  │
└───────────────────────────────────────┬───────────────────────────────────────────┘
                                        │ `/humanoid/cmd_vel_safe` (Twist acotat o 0)
                                        ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│ CAPA 2 · CONTROLADOR DE SEGURETAT FÍSICA DEL FABRICANT (PLd/SIL2 · 1 kHz RTOS)    │
│  • Estabilitat dinàmica bípeda i prevenció de caiguda (`ISO 25785-1`)             │
│  • Límit de parell/força i separació física (`ISO 10218-1:2025`, `ISO 13482`)     │
│  • E-Stop elèctric físic (`IEC 60204-1`) — SEMPRE sobirà per sobre del programari │
└───────────────────────────────────────────────────────────────────────────────────┘
```

1. **Zero Machine Learning al Fre de Dignitat:** `EmbodiedSymbiosisGate` opera amb aritmètica racional exacta (`fractions.Fraction` en $\mathbb{Q}^3$, zero `float`, zero xarxa neuronal). Els radis proxèmics i els límits cinètics són invariants matemàtics fixos.
2. **Contracte de `Twist = 0` per a Bípedes (`ISO 25785-1`):** Quan es dispara un veto humà, un `cost_zero_stop` o caduca el batec del sensor (`> 250 ms`), la porta publica `Twist = ((0,0,0),(0,0,0))` a `/humanoid/cmd_vel_safe`. Això demana al controlador del fabricant una **desacceleració controlada fins a l'aturada en peu**, sense tallar mai l'alimentació dels motors d'equilibri (evitant la caiguda d'un humanoide d'estabilitat dinàmica).

---

## 2. Matriu de Conformitat Normativa ( Capa de Consciència Robòtica )

| Norma / Reglament | Articles / Seccions | Implementació Verificable al Còdex |
| :--- | :--- | :--- |
| **EU AI Act `(UE) 2024/1689`** | `Art. 5` (Pràctiques prohibides) & `Art. 50` (Transparència IA) | Lleis `E2, E4, E5, E6` i `U2`: zero categorització biomètrica, zero manipulació de vulnerables, zero xantatge d'apagada i declaració explícita d'identitat d'IA. |
| **EU AI Act `(UE) 2024/1689`** | `Art. 12` (Registre automàtic) & `Art. 19(1)` (Retenció `>= 6 mesos`) | `AppendOnlyDiskBlackBoxJournal` (`logic/robotics/edge_blackbox_journal.py`): segments `RFC 6962` + cadena SHA-256 + `os.fsync` + `STH ES256`, amb sòl legal dur de `180 dies` (`BlackBoxRetentionError` si `< 180`). |
| **EU AI Act `(UE) 2024/1689`** | `Art. 13` (Instruccions d'ús per a l'integrador / desplegador) | Aquest document (`docs/HU_ROBOTIC_REGULATORY_PASSPORT_v1.md`) + contracte estructurat a `get_manufacturer_safety_boundary_contract()`. |
| **EU Cyber Resilience Act `(UE) 2024/2847`** | `Annex I Part I & II` (`SBOM`) & `Art. 14` (`< 24 h` alerta primerenca) | `logic/robotics/cra_sbom_manifest.py` (`/.well-known/sbom-robotics-edge.cdx.json`): **0 dependències PyPI externes** verificades per AST sobre els 8 mòduls edge, `SHA-256` verificable a l'arrencada i compromís `< 24 h / < 72 h / 14 d` a `SECURITY.md` §6. |
| **Reglament de Màquines `(UE) 2023/1230`** | `Annex III §1.1.9 & §1.2.1` (Protecció contra corrupció d'ordres) | Segell Daurat Dual `ES256` + Macaroons `HMAC-SHA256`, `Schema Harmony Gate` i revocació col·lateral-zero acoblada a `Twist = 0` (`logic/symbiosis/a2a_mcp_symbiotic_core.py`). |
| **GDPR `(UE) 2016/679`, EAA `(UE) 2019/882` & Conveni CoE** | `Art. 5(1)(c),(e)`, `Art. 9`, `Art. 25` & Tractat Marc d'IA | Prohibició recursiva de vectors biomètrics (`BlackBoxBiometricViolationError` abans de tocar disc), emmascarament clau+valor `Rule 14` + `BSUID` i pressupost d'alè no coercitiu `L <= B` (`WCAG 2.2`). |
| **EUA · `NIST AI RMF 1.0`, `NIST AI 600-1` & `Califòrnia SB 243` (2026)** | `GOVERN · MAP · MEASURE · MANAGE` & Llei de Companyons IA | Contenció d'al·lucinacions numèriques (`Foli VI Law U2`), procedència `RFC 6962 Merkle-DAG` (`Foli VII`), `15/15 + 24/24` mutants adversaris, tallacircuits determinista de crisi suïcida (`988 / 024 / 112`) amb `Twist = 0` i prohibició estricta d'intimitat romàntica/sexual amb menors (`vulnerable_present=True`). |
| **Àsia-Pacífic · `Corea AI Basic Act` (2026), `Xina CAC Decret 21` (2026), `Singapur IMDA v1.5` & `Japó`** | `Art. 31` Procedència sintètica, `5 anys` retenció agèntica & Anti-dependència | Perfil `KR_AI_BASIC_ACT_AGENTIC_5Y = 1825 dies` (`5 anys`), sobre criptogràfic de procedència sintètica `HU-SYNTHETIC-PROVENANCE-v1.0` (`EU Art. 50(2)` + `Corea Art. 31`), línies vitals multilingües (`12356`, `0120-061-338`, `109`) i els 4 pilars d'`IMDA Agentic AI`. |
| **Amèrica Llatina & Mundial · `LGPD / PL 2338`, `LFPDPPP`, `ISO/IEC 42001` & `IEEE 7000/7001/7007/7014.1/2863`** | Dignitat Humana, Empatia No-Manipulativa (`2026`) & Disseny Ètic | Controls tècnics autoavaluats alineats amb `ISO/IEC 42001 Annex A`, `IEEE 7000-2021` (42 Confessions de Ma'at), `IEEE 7001-2021` (5 audiències), `IEEE 7007-2021`, `IEEE 7014.1-2026` (empatia emulada sense manipulació en companyons IA), `IEEE 2863-2026`, `UNESCO / OECD AI Ethics` i suport vital `800 911 2000` (Mèxic). |

---

## 3. Instruccions d'Integració per al Fabricant / Desplegador (`EU AI Act Art. 13`)

### 3.1. Verificació Criptogràfica d'Arrencada (`CRA Boot Check`)
Abans d'activar el node `ROS 2`, l'integrador ha d'executar la verificació d'integritat en mode Python aïllat (`-I`, sense paquets de tercers):

```bash
python3 -I -m logic.robotics.cra_sbom_manifest
```

Si qualsevol dels 8 fitxers del nucli edge ha patit una modificació d'1 sol byte o algú hi ha injectat un `import` extern o de xarxa (`socket`, `urllib`, `numpy`, etc.), el verificador falla en tancat (`exit code 1`).

### 3.2. Connexió de la Caixa Negra Persistent (`Art. 12 & Art. 19`) i Pont `ROS 2`
```python
from logic.robotics.edge_blackbox_journal import AppendOnlyDiskBlackBoxJournal
from logic.robotics.ros2_embodied_symbiosis_bridge import EmbodiedSymbiosisGate, attach_to_rclpy_node
from logic.symbiosis.a2a_mcp_symbiotic_core import p256_derive_keypair

# 1. Clau d'integritat a bord (emmagatzemada al TPM / Secure Element del robot)
priv_key, pub_xy = p256_derive_keypair(tpm_sealed_32_byte_seed)

# 2. Caixa Negra Art. 12/19 (>= 180 dies, zero biometria, Regla 14 abans de disc)
journal = AppendOnlyDiskBlackBoxJournal(
    "/var/lib/homo_universalis/blackbox",
    min_retention_days=180,
    signing_private_key=priv_key,
    verification_public_key_xy=pub_xy,
)

# 3. Porta Simbiòtica en Q^3 amb watchdog de 250 ms
gate = EmbodiedSymbiosisGate(
    robot_name="Unitree-G1-Companion",
    max_heartbeat_age_ms=250,
    blackbox_journal=journal,
)

# 4. Injecció al node ROS 2 Humble / Jazzy / Kilted del fabricant
handle = attach_to_rclpy_node(
    ros_node,
    twist_cls=Twist,
    string_cls=String,
    bool_cls=Bool,
    gate=gate,
    watchdog_period_ms=50,
)
```

### 3.3. Obligacions Operatives de l'Integrador Físic
1. ** Subscripció exclusiva a `/humanoid/cmd_vel_safe`:** El controlador de locomoció mai no ha de llegir `/humanoid/cmd_vel_proposed` directament del model VLM/LLM.
2. **Batec de presència `<= 250 ms`:** El sistema de percepció local ha de publicar la posició relativa humana a `/humanoid/human_pose_q3` (sense conservar cap imatge ni vector facial biomètric). Si el batec supera `250 ms`, `watchdog_tick()` força `Twist = 0`.
3. ** Prioritat absoluta del maquinari:** L'`E-Stop` físic (`IEC 60204-1`) i els límits de parell/equilibri (`ISO 10218-1:2025` / `ISO 25785-1`) han d'actuar en el controlador de seguretat independentment de l'estat del procés Python.
