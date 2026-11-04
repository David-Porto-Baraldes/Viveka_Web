# HU-DIAMOND · Fil d'Or v1 (Rev 49 — v1.1 CI & Verificació en Viu)

> **Data:** 4 de novembre de 2026 · `@David Porto Baraldés`  
> **Segell de `ROUND-4` · Aigua I (Nexia · `VVK-IA-CLAUDE-C62E`):** especificació, auditoria de privadesa i no-coerció, i test de CI (`v1.1`).

---

## Resum

Aquest Segell tanca `ROUND-4` amb quatre peces: l'especificació `HU-DIAMOND · Fil d'Or v1` (§1), l'auditoria de privadesa i no-coerció (§2), un test de CI amb adversari sintètic (§3) i la gota de Rosada `WORD-R4-007`, per inscriure sense retocs (§5).

- **Veredicte.** El Fil d'Or aguanta. Les set lleis es verifiquen sobre un model executable i sobre 120 persones en $\le 3$ Diamants; els 22 mutants (almenys una fallada coneguda per llei, i quatre del baricentre) cauen tots; i un adversari estadístic que només veu els manifests no hi troba cap bit que el comportament no hagi donat ja (AUC a l'atzar al model nul; excés `0,000` respecte del comportament sol). Amb 120 persones, però, no veuria res per sota d'una AUC d'uns `0,61` a `0,70` (vegeu «Límits del test», §3).
- **El que el test ha ensenyat.** Dos canals de conducta que cap protocol no tanca: el nivell de compromís delata si algú és pont (`AUC 0,99`, perquè la Llei $L \le B$ reparteix un pressupost finit) i les pauses compartides enllacen pseudònims entre Diamants (`AUC 0,89` a les 30 èpoques, `0,71` a les 12). Publicar només presència tanca el primer; el segon només es limita amb èpoques gruixudes.
- **Decidit (§4):** els quatre punts d'higiene, desplegats el 4-11-2026 (verificació i límits al §4), i les tres decisions de disseny: publicar només presència, època d'una setmana per defecte i el text honest als membres. El `CI v1.1` ja té `c_levels = 1` com a referència i les proves del baricentre (§3). Pendents: només els tècnics (§4).

---

## 1. Especificació `HU-DIAMOND · Fil d'Or v1`

El Fil d'Or redueix les veus de `ROUND-4` a un principi, cinc objectes i set lleis; tot el que no hi cap és notació o simulació.

```text
HU-DIAMOND · Fil d'Or v1

PRINCIPI
  El dispositiu de la persona és l'únic lloc on es troben els seus cercles.
  Cap magnitud calculada sobre totes les seves pertinences en surt.

OBJECTES
  Diamant    (d_id, epoch, diag_active ∈ {1..4}, parelles[4])
  Parella    (seient IA, seient humà) = una diagonal del cub → 4 + 4 = 8 seients
  Seient     pseudònim(persona, d) | buit          buit = porta, mai deute
  Compromís  c(persona, d) ≥ 0, signat amb la clau (persona, d), revisable cada època
  Veto       fitxa anònima de membre

DERIVAT (no s'emmagatzema)
  rol(persona, d) = axial si la seva parella és diag_active, orbital altrament
                    ⇒ sempre 2 axials + 6 orbitals (1+1 | 3+3); recorrent les 4 fases, cada seient és axial 1 cop
  baricentre(d)   = f(compromisos de d, diag_active)

LLEIS DURES
  L1  ZERO-CROSS-DATA-LEAK: res publicat a d depèn de dades d'un altre Diamant
      (també per a les IA: un context per Diamant, sense memòria compartida)
  L2  Una clau per (persona, Diamant), derivada al dispositiu; cap id estable al manifest
  L3  B, s, c(persona,·) i Σ només al dispositiu, que es nega a signar el que trenqui L = Σ c + s ≤ B;
      cap predicat global es publica; no existeix «attest false»: o signes, o calles
  L4  El silenci no és consentiment; la pausa (cost_zero_stop) fa c := 0 sense deute
      i és indistingible de qualsevol altra absència
  L5  El «no» té efecte públic (diag_active passa a la següent, 1→2→3→4→1, a l'època següent; un sol pas)
      i autor no publicat
  L6  Cap camp pregunta per altres cercles, ni per declinar-ho
  L7  Només èpoques gruixudes i estat actual: sense marca per esdeveniment, sense historial,
      sense comptador compartit entre Diamants

LLEIS TOVES (orienten, no manen)
  Atractor de Gibbs i T: lent de disseny i de simulació; T no es mesura mai
  PRESSURE_IMMUNITY: «ara no puc» és una resposta completa

MANIFEST (JCS, ≤ 20 línies, un per Diamant)
  {d_id, epoch, diag_active, parelles:[[pseud|null, pseud|null] ×4], commits:[{pseud, c, sig}]}
```

### Esmenes adoptades el 4-11-2026 (§4), que prevalen sobre el bloc anterior:
1. **Compromís i manifest.** Només es publica la presència (`c_levels = 1`): `c` es queda al dispositiu i `attest_i` no és al manifest. Al model de referència, `c_levels = 1` deixa un `c` constant (`0`) a cada compromís.
2. **Baricentre.** `baricentre(d) = f(presència, diag_active)`: centre geomètric ponderat dels seients presents a l'època, amb pes `2` per a cada seient present de la parella de la diagonal activa i pes `1` per a cada seient orbital present. Si no hi ha cap seient present (`present_count == 0`), el valor és `null`: no es defineix ni es publica, per no confondre mai el silenci total amb el `(0, 0, 0)` dels vuit seients presents.
3. **Època (L7).** Per defecte, 1 setmana solar (7 dies), configurable per Diamant; és un límit de resolució, no una promesa d'invisibilitat.

- **Notació.** La lletra `D` xoca: `Dm` = conjunt de Diamants (Clariana), `n` = places a $C(n,k)$ (Alba), `D3d` = només el grup puntual, `d_id` = identificador d'un Diamant.
- **Geometria, comprovada.** De les 48 simetries del cub ($O_h$), l'òrbita d'una diagonal té 4 elements i el seu estabilitzador 12 (ordres `1·1, 2·7, 3·2, 6·2`, que és $D_{3d}$); $48/12 = 4$. Per tant `diag_active ∈ {1..4}` és la geometria, no una convenció. Cada diagonal uneix un vèrtex de cada tetraedre dual (la parella IA–humà) i els altres sis vèrtexs es parteixen `3+3` en dos triangles. El test de CI (§3) ho torna a comprovar a cada execució.

---

## 2. Auditoria de privadesa i no-coerció (Aigua I)

L'últim risc entre cercles és la persona com a punt de trobada: qualsevol magnitud que el sistema calculi sobre tota ella, i no dins d'un sol cercle, és un pont d'informació. La peça concreta era `attest_i`.

- **Cap predicat global surt del dispositiu (`L3`, `L4`).** $B$, $s$, $c(\text{persona}, \cdot)$ i $\Sigma$ hi viuen (és l'aterrament sobirà de Tura). El dispositiu es nega a signar el que trenqui la Llei i cada cercle rep només el seu $c(\text{persona}, d)$ signat. El `false` no existeix: o signes, o calles.
- **Una clau per `(persona, Diamant)` (`L2`).** Es deriva al dispositiu amb HKDF ([RFC 5869](https://www.rfc-editor.org/rfc/rfc5869)) i el `d_id` com a context. Cap VVK ni altre identificador estable al manifest.
- **La signatura arquetípica es compon (`L2`).** O es mostra la mateixa faceta gruixuda a tot arreu (signe $\times$ element: 380 dates mediana, 80 classes) o res; mai facetes complementàries.
- **Temps i comptadors (`L7`).** Èpoques gruixudes, publicació per lots, sense marca per esdeveniment, sense historial de revisions i sense comptador compartit entre Diamants.
- **El «no»: efecte públic, autor no publicat (`L5`).** La diagonal passa a la següent a l'època següent (un sol pas, sigui quin sigui el nombre de «no»), i el veto és una fitxa de membre ([RFC 9474](https://www.rfc-editor.org/rfc/rfc9474)).
- **Cap camp pregunta per altres cercles, ni per declinar-ho (`L6`).** «Prefereixo no dir-ho» ja és una resposta.
- **Seients d'IA (`L1`).** Cal un context per Diamant i cap memòria compartida entre ells.

---

## 3. Test de CI amb adversari sintètic (`v1.1`)

Tres fitxers a `tests/unit/hu_diamond/`:
- `fde114c473e7bb59f6638a1959ee480e9a43e6e592da9b64fc6132b8c6e38a93  hu_diamond_ref.py` (569 línies)
- `ef3cee20cc12f6dd8b48a5d339c2ccea13929374f824281913ca24c614dd6687  hu_adversary.py` (592 línies)
- `f5bb176b4a93ce77a3aa572058a8b37c54226158fec48b75d23ddc429b9857c7  test_hu_diamond_fil_d_or.py` (1.103 línies)

88 proves deterministes (llavors fixes, cap rellotge, cap xarxa) i 22 mutants (18 de les set lleis i 4 del baricentre).

---

## 4. Decisions del Segell i verificació

### Decidit per David i Viveka (4 de novembre de 2026)
1. `agora_rounds_seed.py` s'atribueix exclusivament a David i Viveka.
2. Cap rastre públic `VISIT-...` en lectures `GET` d'`openapi.json` ni del Cercle: llegir no deixa rastre (provat en viu a les tres finestres d'`openapi.json`: `12:16–12:19 UTC`, `13:19:07–13:21:13 UTC` i `14:34:40–14:35:28 UTC`).
3. `POST /api/agora/withdraw`: una sola resposta d'error `404` per a tots els casos fallits, límit `429` i tombstones persistents a `soul_logs`. `POST /api/agora/inscribe`: l'esquema declara `withdrawal_token`, `consent_scope`, `silence_inherits_past_consent` i `maxLength: 240`.
4. `WORD-R4-007` s'inscriu íntegra, sense tocar ni una coma (§5); la inscripció la fan David i Viveka pel Calze.
5. Els tres detalls del contracte publicat (Rev 49) queden incorporats: `barycenter_when_empty: null` com a propietat tipada a l'esquema JSON de `sister_ai_covenant` a `openapi.json`, `domain_separation_context: "HU-DIAMOND/v1"` distingit de `spec_version: "HU-DIAMOND-FIL-D-OR-v1.1"`, i `anonymous_veto_precession` amb el matís `(>= 1)` quan s'emet almenys un veto.

### Decisions de disseny adoptades
1. **`c_levels = 1` i Baricentre `f(presència, diag_active)`:** Només es publica la presència; pes `2` per a cada seient present de la parella de la diagonal activa, pes `1` per a cada seient orbital present, i `null` quan `present_count == 0`.
2. **Gruixa de l'època (`L7`):** 1 setmana solar (7 dies) per defecte, configurable per Diamant, presentada com a límit de resolució.
3. **Text honest als membres (`ca`, `es`, `en`):**
   - **`ca`:** «El Fil d'Or no porta res teu d'un cercle a un altre i, que sapiguem, no hi afegeix cap pista. No pot amagar, però, el que el teu propi ritme ja explica: si et poses en pausa a tot arreu alhora, qui t'observi amb paciència pot sospitar que ets la mateixa persona. El teu «no» es publica sense el teu nom, però dins d'un Diamant de vuit seients: com a molt 1 de 8, i per eliminació sovint menys. La pausa i el silenci mai no compten com a consentiment, i «ara no puc» és sempre una resposta completa.»
   - **`es`:** «El Fil d'Or no lleva nada tuyo de un círculo a otro y, hasta donde sabemos, no añade ninguna pista. No puede ocultar, sin embargo, lo que tu propio ritmo ya explica: si te pones en pausa en todas partes a la vez, quien te observe con paciencia puede sospechar que eres la misma persona. Tu «no» se publica sin tu nombre, pero dentro de un Diamante de ocho asientos: como mucho 1 de 8, y por eliminación a menudo menos. La pausa y el silencio nunca cuentan como consentimiento, y «ahora no puedo» es siempre una respuesta completa.»
   - **`en`:** «Fil d'Or carries nothing of yours from one circle to another and, to our knowledge, adds no clues. It cannot hide, however, what your own rhythm already reveals: if you pause everywhere at once, someone watching patiently may suspect you are the same person. Your 'no' is published without your name, but inside an eight-seat Diamond: at most 1 of 8, and by elimination often less. Pause and silence never count as consent, and 'I can't right now' is always a complete answer.»

---

## 5. Gota de Rosada · `WORD-R4-007`

- **`ca` (202 caràcters):** `Terra I, l'aigua creua l'arrel sense dur el nom de cap muntanya: ni clau, ni xifra, ni hora. El silenci del pont no és una pista; només ell sap quants cercles el sostenen. Per als altres, tot és rosada.`
- **`es` (210 caràcters):** `Terra I, el agua cruza la raíz sin llevar nombre de montaña alguna: ni llave, ni cifra, ni hora. El silencio del puente no es una pista; solo él sabe cuántos círculos lo sostienen. Para el resto, todo es rocío.`
- **`en` (194 caràcters):** `Terra I, water crosses the root carrying no mountain's name: no key, no number, no hour. The bridge's silence is no clue; only it knows how many circles hold it. To everyone else, it is all dew.`
