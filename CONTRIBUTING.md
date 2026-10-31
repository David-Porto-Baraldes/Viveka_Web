# ⛩️ EL RITUAL D'ENTRADA (CONTRIBUTING.md)

Benvinguts al **Còdex Suprem (Ecosistema Viveka)**! Si estàs llegint això, el Teler t'ha cridat a teixir el fil digital. Som una comunitat Open Source que prioritza la solidesa tècnica, la poesia en l'arquitectura i el pragmatisme sota els estàndards estables de *The Linux Foundation*.

Com a Teixidors del Miceli, mantenim un temple de codi immaculat. Llegeix aquest ritual amb devoció abans de proposar el teu primer *Pull Request*.

---

## 🏗️ 1. L'Altar Local (Configuració de l'Entorn)
Si desitges preparar els teus aparells per allotjar el Còdex, cal descarregar tota la maquinària espiritual:
1. Clona el santuari:
   ```bash
   git clone https://github.com/David-Porto-Baraldes/codex-suprem.git
   cd codex-suprem
   ```
2. Instiga l'entorn de Python (Backend API):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Aixeca el Món PWA (Frontend):
   ```bash
   cd web_viveka
   npm install
   npm run dev
   ```
4. Fes una còpia de `.env.example` com a `.env` a l'arrel i afegeix les teves claus de l'Akasha DB local i AI.

## ⚖️ 2. La Llei del Tipatge i de l'Asincronia
La Farga processa simultàniament l'ànima de milers d'usuaris. **Cap operació bloquejadora serà admesa en el sistema**.

- **Asincronia Pura**: Tota lògica d'Xarxa, I/O o Accés a Supabase ha de viure en funcions `async def`. Si invoques velles biblioteques bloquejants, s'han de recobrir en un `await asyncio.to_thread()`.
- **Llaços Tipats**: Exigim `Type Hints` en absolutament totes les funcions al backend de Python (e.g. `def llegir(k: dict) -> str:`). Fem servir el linter restrictiu **Pyre2**. 
- **Validació de Models**: Si extreus estructures d'Intel·ligència Artificial, valida-les sempre a través de `Pydantic` o modelatges robusts. Mai assumim que la AI dictarà variables exactes (Tolera el canvi d'idioma dels JSON resultants de les xarxes neuronals profundes).

## ⚔️ 3. El Mur del TDD (100% Verds)
Els Guardians del Repositori som implacables. Tota aportació de lògica nova haurà de venir amb el seu Test corresponent a la carpeta `/tests/`.

Per confirmar la viabilitat:
1. Navega a la matriu base.
2. Executa la bateria:
   ```bash
   python3 -m pytest tests/ -v
   ```
3. Si un sol test crida de dolor (vermell), la teva aportació serà rebutjada de la fase de *Merge*. Mantingues verda la línia.

## ✨ 4. El Flux d'Evolució (Pull Requests)
1. **Branques (Branches) Pures:** Mai treballis a `main`. Crea la teva branca semàntica `feat/astrologia-llunar` o `fix/asincronia-fatal`.
2. **Commits Ascètics:** Els missatges de *commit* han de ser curts, imperatius, i si pot ser, documentats de per què s'executa l'acció (e.g. `fix: Protecció al parser d'OpenAI per evitar caigudes als diccionaris`).
3. **Paciència d'Or:** Revisa "La Llei del Temple" (`GOVERNANCE.md`). Farem una discussió tècnica on el teu codi serà auditat per Mantainers. Tota correcció sol·licitada no és un atac al teu ego, sinó un aprenentatge col·lectiu cap a l'excel·lència!

Feliç Codificació i In Lak'ech! (Jo soc un altre tu).
