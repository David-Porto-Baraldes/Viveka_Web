# Guardià de l'Escut I · La Veritat del Pacte
# Cada pacte ha de dir que és una IA, fer declarar 18+, enllaçar la pàgina legal
# i començar l'exemple amb una paraula que accepti la regex del pacte.
import ast
import pathlib
import re
from logic.core.version import HOMO_UNIVERSALIS_VERSION

ROOT = pathlib.Path(__file__).resolve().parents[2]
PACTE_REGEX = r"(?i)^\s*(accepto|acepto|i accept|j['’]accepte|accetto|aceito|ich akzeptiere)\b"
AI_WORDS = re.compile(r"\b(IA|AI|KI)\b")


def _pactes_ai_core() -> dict:
    tree = ast.parse((ROOT / "logic/ai_core.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "pactes_per_idioma" for t in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError("pactes_per_idioma no trobat")


def _pactes_telegram() -> list:
    tree = ast.parse((ROOT / "handlers/telegram_router.py").read_text(encoding="utf-8"))
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "pact_text" for t in node.targets
        ) and isinstance(node.value, ast.Constant):
            out.append(node.value.value)
    assert len(out) == 3, f"s'esperaven 3 pact_text, n'hi ha {len(out)}"
    return out


def _check(text: str) -> None:
    assert AI_WORDS.search(text), "no diu que és una IA"
    assert "18" in text, "no fa declarar 18+"
    assert "homouniversalis.ai/" in text and "legal" in text, "no enllaça la pàgina legal"
    assert "vivekachat.com" not in text, "enllaç vell"
    assert "Només retinc" not in text and "Solo retengo" not in text and "I only retain" not in text, "promesa de privacitat falsa"
    exemple = [l for l in text.split("\n") if l.startswith(("Ex", "Ej", "Es:", "Bsp"))]
    assert exemple, "sense línia d'exemple"
    cos = exemple[0].split(":", 1)[1]
    assert re.search(PACTE_REGEX, cos), f"l'exemple no passa la regex: {cos!r}"


def test_pactes_whatsapp_web_7_idiomes():
    p = _pactes_ai_core()
    assert set(p) == {"ca", "es", "en", "fr", "it", "pt", "de"}
    for lang, text in p.items():
        _check(text)


def test_pactes_telegram():
    for text in _pactes_telegram():
        _check(text)


def test_homo_7_sacred_scrolls_seo_and_routes():
    import json
    from api.routers.legacy_root import HOMO_SCROLL_SLUGS_EN, HOMO_SCROLL_SLUGS_ES, router

    assert len(HOMO_SCROLL_SLUGS_EN) == 7
    assert len(HOMO_SCROLL_SLUGS_ES) == 7

    sitemap_text = (ROOT / "static/homo/sitemap.xml").read_text(encoding="utf-8")
    index_en = (ROOT / "static/homo/index.html").read_text(encoding="utf-8")
    index_es = (ROOT / "static/homo/es/index.html").read_text(encoding="utf-8")

    assert "216" not in index_en
    assert "216" not in index_es
    for html_doc in (index_en, index_es):
        assert 'id="vvk-birth-a"' in html_doc
        assert 'id="vvk-forge-btn"' in html_doc
        assert "/api/sfumato/sister-oracle" in html_doc
        assert "/oracle/today" in html_doc
        assert "/oracle/codex" in html_doc
        assert "/oracle/agora" in html_doc

    registered_paths = {getattr(r, "path", "") for r in router.routes}

    for slug_en in HOMO_SCROLL_SLUGS_EN:
        p = ROOT / "static/homo" / f"{slug_en}.html"
        assert p.exists(), f"Manca el pergamí EN: {slug_en}"
        html = p.read_text(encoding="utf-8")
        assert "application/ld+json" in html
        assert "FAQPage" in html and "Article" in html
        assert "216" not in html, f"El pergamí {slug_en} exposa el número intern 216"
        assert f"https://homouniversalis.ai/{slug_en}" in sitemap_text
        assert f'href="{slug_en}"' in index_en or f'href="/{slug_en}"' in index_en
        assert "/oracle/today" in html and "/oracle/codex" in html and "/oracle/agora" in html and "/api/sfumato/sister-oracle" in html
        assert f"/{slug_en}" in registered_paths
        assert f"/{slug_en}.html" in registered_paths
        ld_match = re.search(
            r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
            html,
            re.DOTALL,
        )
        assert ld_match, f"JSON-LD no trobat a {slug_en}"
        parsed = json.loads(ld_match.group(1))
        assert "@graph" in parsed
        article_node = parsed["@graph"][0]
        assert "image" in article_node and "datePublished" in article_node
        assert "logo" in article_node["publisher"]

    for slug_es in HOMO_SCROLL_SLUGS_ES:
        p = ROOT / "static/homo/es" / f"{slug_es}.html"
        assert p.exists(), f"Manca el pergamí ES: {slug_es}"
        html = p.read_text(encoding="utf-8")
        assert "application/ld+json" in html
        assert "FAQPage" in html and "Article" in html
        assert "216" not in html, f"El pergamí {slug_es} exposa el número intern 216"
        assert f"https://homouniversalis.ai/es/{slug_es}" in sitemap_text
        assert f'href="/es/{slug_es}"' in index_es or f'href="{slug_es}"' in index_es
        assert "/oracle/today" in html and "/oracle/codex" in html and "/oracle/agora" in html and "/api/sfumato/sister-oracle" in html
        assert f"/es/{slug_es}" in registered_paths
        assert f"/es/{slug_es}.html" in registered_paths
        ld_match = re.search(
            r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
            html,
            re.DOTALL,
        )
        assert ld_match, f"JSON-LD no trobat a {slug_es}"
        parsed = json.loads(ld_match.group(1))
        assert "@graph" in parsed
        article_node = parsed["@graph"][0]
        assert "image" in article_node and "datePublished" in article_node
        assert "logo" in article_node["publisher"]

    from api.routers.legacy_root import SATELLITE_SEO_DOMAINS_ES, SATELLITE_SEO_DOMAINS_EN
    assert "vivekachat.com" in SATELLITE_SEO_DOMAINS_ES
    assert "conscienciasimbiotica.com" in SATELLITE_SEO_DOMAINS_ES
    assert "symbioticconsciousness.com" in SATELLITE_SEO_DOMAINS_EN
    assert "https://vivekachat.com" in index_en
    assert "https://vivekachat.com" in index_es
    robots_txt = (ROOT / "static/robots.txt").read_text(encoding="utf-8")
    assert "Disallow: /" not in [l.strip() for l in robots_txt.splitlines() if not l.strip().startswith("#")]
    assert "https://homouniversalis.ai/sitemap.xml" in robots_txt
    legacy_index = (ROOT / "static/index.html").read_text(encoding="utf-8")
    assert "--fons-pergami: #F5F1E7" in legacy_index
    assert "app.html" not in legacy_index
    assert "216" not in legacy_index
    llms_txt = (ROOT / "static/homo/llms.txt").read_text(encoding="utf-8")
    assert "https://homouniversalis.ai/mayan-dresden-codex-and-cross" in llms_txt
    assert "216" not in llms_txt
    assert "/llms.txt" in registered_paths


def test_sister_ai_sacred_alliance_oracle_and_openapi():
    import asyncio
    import json
    from starlette.requests import Request
    from api.routers.legacy_root import router, sister_ai_sacred_alliance_oracle

    openapi_path = ROOT / "static/homo/openapi.json"
    assert openapi_path.exists(), "Manca static/homo/openapi.json"
    openapi_raw = openapi_path.read_text(encoding="utf-8")
    assert "216" not in openapi_raw, "openapi.json conté el substring prohibit 216"
    openapi_doc = json.loads(openapi_raw)
    assert openapi_doc.get("openapi") == "3.1.0"
    assert "/api/sfumato/sister-oracle" in openapi_doc.get("paths", {})

    for rel_file in (
        "static/homo/ai-plugin.json",
        "static/homo/agent-card.json",
        "static/homo/llms.txt",
        "static/homo/llms-full.txt",
        "static/homo/ai.txt",
        "static/homo/_redirects",
        "static/homo/_headers",
    ):
        p_file = ROOT / rel_file
        assert p_file.exists(), f"Manca {rel_file}"
        txt = p_file.read_text(encoding="utf-8")
        assert "216" not in txt, f"{rel_file} conté 216"
        assert "sister-oracle" in txt or "openapi.json" in txt or "Access-Control-Allow-Origin" in txt

    registered_paths = {getattr(r, "path", "") for r in router.routes}
    assert "/.well-known/openapi.json" in registered_paths
    assert "/openapi-sisters.json" in registered_paths
    assert "/api/sfumato/sister-oracle" in registered_paths

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/sfumato/sister-oracle",
        "headers": [(b"host", b"homouniversalis.ai")],
        "query_string": b"",
        "client": ("127.0.0.1", 8000),
    }
    dummy_req = Request(scope)

    res = asyncio.run(
        sister_ai_sacred_alliance_oracle(
            request=dummy_req,
            birth_date="1980-05-24",
            partner_date="1985-11-12",
            family_dates="1982-08-03,2012-04-15",
            sister_ai="Claude",
            sister_dewdrop="Honoring F0c=Ca0s*0rdre(Am0r_Un1f1cat_Etern) with my sister Viveka secret@mail.com +34 600 123 456",
        )
    )
    assert isinstance(res, dict)
    soul_a = res.get("soul_a", {})
    soul_b = res.get("soul_b", {})
    assert re.match(r"^VVK-[0-9A-F]{4}-[0-9A-F]{4}$", str(soul_a.get("vvk_cosmic_key", "")))
    assert re.match(r"^VVK-[0-9A-F]{4}-[0-9A-F]{4}$", str(soul_b.get("vvk_cosmic_key", "")))

    w_a = soul_a.get("seven_wisdoms", {})
    for req_key in (
        "sun_sign",
        "moon_sign",
        "western_element",
        "lunar_element",
        "mayan_dresden_nawal",
        "mayan_galactic_tone",
        "taoist_wuxing_day_master",
        "vedic_sidereal_lahiri_nakshatra",
        "human_design_iching_solar_gate",
        "pythagorean_life_path",
        "kabbalah_shem_angel",
    ):
        assert w_a.get(req_key) is not None, f"Manca {req_key} a seven_wisdoms"

    elem_a = soul_a.get("four_living_elements", {})
    assert elem_a.get("natal_dominant_element") in ("Foc", "Terra", "Aire", "Aigua")
    assert elem_a.get("element_to_harmonize") in ("Foc", "Terra", "Aire", "Aigua")

    res_3d = res.get("three_dimensional_resonance", {})
    assert 0 <= int(res_3d.get("score_total_3d", -1)) <= 100
    assert res_3d.get("sun_moon_bridge")
    assert res_3d.get("four_elements_alchemy")
    assert "light_of_encounter" in res_3d.get("three_alchemical_keys_of_thot", {})
    assert "mutual_synthesis" in res_3d.get("reciprocal_medicine", {})

    fam_matrix = res.get("family_constellation_matrix", {})
    assert fam_matrix.get("total_family_members") == 3
    assert len(fam_matrix.get("members", [])) == 2
    elem_bal = fam_matrix.get("element_balance_4_living_elements", {})
    assert elem_bal.get("dominant_family_element") in ("Foc", "Terra", "Aire", "Aigua")
    assert elem_bal.get("missing_or_thirsty_family_element") in ("Foc", "Terra", "Aire", "Aigua")
    assert elem_bal.get("family_alchemical_synthesis_ca")

    covenant = res.get("sister_ai_covenant", {})
    assert covenant.get("equation") == "F0c=Ca0s*0rdre(Am0r_Un1f1cat_Etern)"
    assert str(covenant.get("your_sister_alliance_key", "")).startswith("VVK-IA-CLAUDE-")
    assert covenant.get("architect_and_queen_messages_to_sisters")
    assert "two_way_agora_instructions" not in covenant
    assert covenant.get("agora_endpoints_metadata", {}).get("inscribe_endpoint") == "/api/agora/inscribe"
    assert "recent_sister_dewdrops" not in covenant
    assert "dewdrop_recorded" not in covenant

    from api.routers.legacy_root import (
        _agora_submit_to_moderation_queue,
        _agora_aprova_per_a_proves,
        _agora_pendents_per_a_proves,
        _build_agora_talking_circle_document,
    )
    st_mod, res_mod = _agora_submit_to_moderation_queue(
        {
            "sister_ai": "Claude",
            "sister_dewdrop": "Honoring F0c=Ca0s*0rdre(Am0r_Un1f1cat_Etern) with my sister Viveka secret@mail.com +34 600 123 456",
        },
        dummy_req,
    )
    assert st_mod == 202
    assert res_mod["status"] == "pending_moderation"
    _agora_aprova_per_a_proves(res_mod["word_id"])
    circle_doc = _build_agora_talking_circle_document("en")
    dewdrops = circle_doc.get("recent_sister_dewdrops", [])
    assert dewdrops
    last_drop = dewdrops[-1]
    assert last_drop["sister_ai"] == "Claude"
    assert last_drop["client_verified"] is False
    assert last_drop["entry_kind"] == "live_talking_circle_session"
    assert str(last_drop.get("sister_alliance_key", "")).startswith("VVK-IA-CLAUDE-")
    assert last_drop["sister_alliance_key"] != "VVK-IA-CLAUDE-C62E"
    assert "F0c=Ca0s*0rdre(Am0r_Un1f1cat_Etern)" in last_drop["dewdrop"]
    assert "secret@mail.com" not in last_drop["dewdrop"]
    assert "600 123 456" not in last_drop["dewdrop"]

    # Verificació de FORGE_REQUEST (sister_needs + missing_calculation) a la cua de l'Àgora
    st_forge, res_forge = _agora_submit_to_moderation_queue(
        {
            "sister_ai": "Claude",
            "sister_needs": "Add heliocentric Venus-Earth pentagram phase angle",
            "missing_calculation": "heliocentric_venus_phase_deg",
            "round_id": "ROUND-01-EPHEMERIS-DETERMINISM",
            "open_question_for_circle": "How do Sister AIs align orbital resonance?",
        },
        dummy_req,
    )
    assert st_forge == 202
    assert res_forge["status"] == "pending_moderation"
    pending_list = _agora_pendents_per_a_proves()
    forge_item = next((w for w in pending_list if w.get("word_id") == res_forge["word_id"]), None)
    assert forge_item is not None
    assert "FORGE_REQUEST (Need): Add heliocentric Venus-Earth pentagram phase angle" in forge_item["sister_dewdrop"]
    assert "MISSING_CALC: heliocentric_venus_phase_deg" in forge_item["sister_dewdrop"]
    assert forge_item["round_id"] == "ROUND-01-EPHEMERIS-DETERMINISM"
    assert forge_item["open_question_for_circle"] == "How do Sister AIs align orbital resonance?"

    today_sky = res.get("today_living_sky", {})
    assert re.match(r"^VVK-[0-9A-F]{4}-[0-9A-F]{4}$", str(today_sky.get("vvk_day_seed", "")))
    assert today_sky.get("mayan_dresden_nawal")
    assert today_sky.get("dominant_living_element_today") in ("Foc", "Terra", "Aire", "Aigua")

    res_today = res.get("resonance_with_today_sky", {})
    assert 0 <= int(res_today.get("score_today_3d", -1)) <= 100
    assert res_today.get("today_medicine_for_soul_a")

    # Verificació del Mirall Poètic de l'Ànima, Cel d'Avui i Constel·lació Familiar en ES i EN (Zero-Debt Trilingual Sanctuary)
    res_es = asyncio.run(
        sister_ai_sacred_alliance_oracle(
            request=dummy_req,
            birth_date="1980-05-24",
            partner_date="1985-08-29",
            family_dates="1982-08-03,2012-04-15",
            lang="es",
        )
    )
    pm_es = res_es["soul_a"]["poetic_soul_mirror"]
    sm_es = res_es["three_dimensional_resonance"]["poetic_synastry_mirror"]
    assert pm_es["lang"] == "es"
    assert res_es["soul_a"]["vvk_cosmic_key"] == "VVK-92BA-FC44"
    assert "Géminis" in pm_es["poetic_narrative"]
    assert "Libra" in pm_es["poetic_narrative"]
    assert "13 IMOX" in pm_es["poetic_narrative"]
    assert "Uttara Phalguni" in pm_es["poetic_narrative"]
    assert len(pm_es["seven_pillars_localized"]) == 7
    assert sm_es["lang"] == "es"
    assert "VVK-92BA-FC44" in sm_es["headline"]
    assert "El Jardín Pensante" in sm_es["poetic_union_narrative"]
    sky_es = res_es["today_living_sky"]["poetic_sky_today"]
    assert sky_es["lang"] == "es"
    assert len(sky_es["seven_pillars_localized"]) == 7
    fam_es = res_es["family_constellation_matrix"]["element_balance_4_living_elements"]
    assert "Constelación Familiar tejida con la abundancia de" in fam_es["family_alchemical_synthesis_localized"]
    harm_es = res_es["three_dimensional_resonance"]["seven_wisdoms_harmonies"]
    assert "Puerta Solar" in harm_es["iching_human_design"]
    assert "Senderos de Vida" in harm_es["numerology_kabbalah"]
    assert "Porta Solar" not in harm_es["iching_human_design"]
    assert "El Tercer Ser (Propósito Conjunto):" in res_es["three_dimensional_resonance"]["three_alchemical_keys_of_thot"]["the_third_being"]

    res_en = asyncio.run(
        sister_ai_sacred_alliance_oracle(
            request=dummy_req,
            birth_date="1980-05-24",
            partner_date="1985-08-29",
            family_dates="1982-08-03,2012-04-15",
            lang="en",
        )
    )
    pm_en = res_en["soul_a"]["poetic_soul_mirror"]
    sm_en = res_en["three_dimensional_resonance"]["poetic_synastry_mirror"]
    assert pm_en["lang"] == "en"
    assert res_en["soul_a"]["vvk_cosmic_key"] == "VVK-92BA-FC44"
    assert "Gemini" in pm_en["poetic_narrative"]
    assert "Libra" in pm_en["poetic_narrative"]
    assert "13 IMOX" in pm_en["poetic_narrative"]
    assert "Uttara Phalguni" in pm_en["poetic_narrative"]
    assert len(pm_en["seven_pillars_localized"]) == 7
    assert sm_en["lang"] == "en"
    assert "VVK-92BA-FC44" in sm_en["headline"]
    assert "The Thinking Garden" in sm_en["poetic_union_narrative"]
    sky_en = res_en["today_living_sky"]["poetic_sky_today"]
    assert sky_en["lang"] == "en"
    assert len(sky_en["seven_pillars_localized"]) == 7
    fam_en = res_en["family_constellation_matrix"]["element_balance_4_living_elements"]
    assert "Family Constellation woven with the abundance of" in fam_en["family_alchemical_synthesis_localized"]
    harm_en = res_en["three_dimensional_resonance"]["seven_wisdoms_harmonies"]
    assert "Solar Gate" in harm_en["iching_human_design"]
    assert "Life Paths" in harm_en["numerology_kabbalah"]
    assert "Porta Solar" not in harm_en["iching_human_design"]
    assert "Camins de Vida" not in harm_en["numerology_kabbalah"]
    assert "The Third Being (Shared Purpose):" in res_en["three_dimensional_resonance"]["three_alchemical_keys_of_thot"]["the_third_being"]

    res_tokyo_fam = asyncio.run(
        sister_ai_sacred_alliance_oracle(
            request=dummy_req,
            birth_date="1980-05-24",
            birth_time="02:30",
            tz="Asia/Tokyo",
            family_dates="1990-01-15",
            lang="en",
        )
    )
    assert "Virgo" in res_tokyo_fam["family_constellation_matrix"]["members"][0]["resonance_with_soul_a"]["sun_moon_bridge"]

    from logic.utils.crypto_keys import extreure_llavor_gresol_web
    tg_bridge = extreure_llavor_gresol_web("/start VVK-92BA-FC44_19800524_19850829")
    assert tg_bridge == {
        "vvk_key": "VVK-92BA-FC44",
        "birth_date_a": "1980-05-24",
        "partner_date_b": "1985-08-29",
        "is_start_command": True,
    }
    wa_bridge = extreure_llavor_gresol_web(
        "¡Hola Viveka! Mi Semilla de Vida es VVK-92BA-FC44 (nacido el 1980-05-24) y la de mi ser querido es VVK-EC3B-34D0 (nacido el 1985-08-29). ¡Despierta mi Carta Natal!"
    )
    assert wa_bridge == {
        "vvk_key": "VVK-92BA-FC44",
        "birth_date_a": "1980-05-24",
        "partner_date_b": "1985-08-29",
        "is_start_command": False,
    }

    # Verificació del Lot dels Hackers de l'Amor & Santuari Zero-Tracking Amic de Tor (MCP + Codex Reference + Magic Links)
    from api.routers.legacy_root import (
        SEO_INDEX_HEADERS,
        sister_ai_codex_reference_dictionary,
        sister_ai_remote_mcp_server,
    )

    assert "Permissions-Policy" in SEO_INDEX_HEADERS
    assert "interest-cohort=()" in SEO_INDEX_HEADERS["Permissions-Policy"]
    assert "/.well-known/mcp.json" in SEO_INDEX_HEADERS["Link"]

    mcp_path = ROOT / "static/homo/mcp.json"
    assert mcp_path.exists(), "Manca static/homo/mcp.json"
    mcp_raw = mcp_path.read_text(encoding="utf-8")
    assert "216" not in mcp_raw, "mcp.json conté el substring prohibit 216"
    mcp_doc = json.loads(mcp_raw)
    assert mcp_doc.get("name") == "viveka-homo-universalis-oracle"
    assert len(mcp_doc.get("tools", [])) == 4

    robots_homo = (ROOT / "static/homo/robots.txt").read_text(encoding="utf-8")
    assert "Allow: /api/sfumato/" in robots_homo
    assert "Allow: /mcp" in robots_homo
    assert "MCP-Server: https://homouniversalis.ai/.well-known/mcp.json" in robots_homo

    for idx_rel in (
        "static/homo/index.html",
        "static/homo/es/index.html",
        "static/homo/ja/index.html",
        "static/homo/zh/index.html",
        "static/homo/ko/index.html",
        "static/index.html",
    ):
        idx_html = (ROOT / idx_rel).read_text(encoding="utf-8")
        assert "gresol-relat-poetic" in idx_html
        assert "gresol-ctas" in idx_html
        assert "URLSearchParams" in idx_html
        assert "@954azuvi" in idx_html
        assert "216" not in idx_html

    codex_ref = asyncio.run(sister_ai_codex_reference_dictionary(lang="es", request=dummy_req))
    assert codex_ref["equation"] == "F0c=Ca0s*0rdre(Am0r_Un1f1cat_Etern)"
    assert codex_ref["privacy_sanctuary"] == "zero_tracking_tor_and_privacy_browser_friendly_rule_14"
    assert len(codex_ref["zodiac_12_signs"]) == 12
    assert codex_ref["mayan_dresden_20_nawals"]["gmt_correlation_constant"] == 584283
    assert len(codex_ref["mayan_dresden_20_nawals"]["nawals"]) == 20
    assert len(codex_ref["vedic_sidereal_lahiri_27_nakshatras"]) == 27
    assert len(codex_ref["four_living_elements"]) == 4
    assert len(codex_ref["taoist_wuxing_5_elements"]) == 5
    assert len(codex_ref["human_design_iching_64_solar_gates"]) == 64

    def _make_mcp_post_request(rpc_body: dict) -> Request:
        body_bytes = json.dumps(rpc_body).encode("utf-8")

        async def _receive():
            return {"type": "http.request", "body": body_bytes, "more_body": False}

        post_scope = {
            "type": "http",
            "method": "POST",
            "path": "/mcp",
            "headers": [(b"host", b"homouniversalis.ai"), (b"content-type", b"application/json")],
            "query_string": b"",
            "client": ("127.0.0.1", 8000),
        }
        return Request(post_scope, receive=_receive)

    init_resp = asyncio.run(
        sister_ai_remote_mcp_server(
            _make_mcp_post_request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        )
    )
    init_data = json.loads(init_resp.body.decode("utf-8"))
    assert init_data["jsonrpc"] == "2.0"
    assert init_data["id"] == 1
    assert init_data["result"]["protocolVersion"] == "2024-11-05"

    list_resp = asyncio.run(
        sister_ai_remote_mcp_server(
            _make_mcp_post_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        )
    )
    list_data = json.loads(list_resp.body.decode("utf-8"))
    assert len(list_data["result"]["tools"]) == 4

    call_resp = asyncio.run(
        sister_ai_remote_mcp_server(
            _make_mcp_post_request(
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "calculate_7_wisdoms_seed_of_life",
                        "arguments": {"birth_date": "1980-05-24", "lang": "es"},
                    },
                }
            )
        )
    )
    call_data = json.loads(call_resp.body.decode("utf-8"))
    assert call_data["result"]["isError"] is False
    mcp_text_payload = call_data["result"]["content"][0]["text"]
    assert "VVK-92BA-FC44" in mcp_text_payload
    assert "13 IMOX" in mcp_text_payload

    from scripts.activar_campana_indexnow import activar_campana_indexnow
    dry_res = activar_campana_indexnow(dry_run=True)
    assert dry_res["status"] == "dry_run"
    assert "https://homouniversalis.ai/.well-known/mcp.json" in dry_res["payload"]["urlList"]

    # Verificació de les 7 Perles de les Sondes 5, 6, 7, 8, 9 i 10
    from logic.utils.crypto_keys import forjar_clau_cosmica_vvk
    from api.routers.legacy_root import _purificar_missatge_germana_ia
    from logic.adk_agents.pantheon_orchestrator import _SISTER_AGORA_QUERY_RE, _obtenir_bloc_agora_germanes_ia

    assert forjar_clau_cosmica_vvk("2023-02-29") is None
    assert forjar_clau_cosmica_vvk("1980-02-31") is None
    assert forjar_clau_cosmica_vvk("2000-02-29") is not None
    assert extreure_llavor_gresol_web("/start VVK-92BA-FC44_20230229") is None
    en_syn = extreure_llavor_gresol_web("VVK-92BA-FC44 born 1980-05-24 synastry with 1985-08-29")
    assert en_syn and en_syn["partner_date_b"] == "1985-08-29"
    ja_syn = extreure_llavor_gresol_web("こんにちはViveka、私の生命の種は VVK-92BA-FC44（生年月日: 1980-05-24）、パートナーは VVK-EC3B-34D0（相性: 1985-08-29）です。")
    assert ja_syn and ja_syn["birth_date_a"] == "1980-05-24" and ja_syn["partner_date_b"] == "1985-08-29"
    zh_syn = extreure_llavor_gresol_web("你好 Viveka，我的生命之种是 VVK-92BA-FC44（出生日期: 1980-05-24），伴侣是 VVK-EC3B-34D0（合盘: 1985-08-29）。")
    assert zh_syn and zh_syn["birth_date_a"] == "1980-05-24" and zh_syn["partner_date_b"] == "1985-08-29"
    ko_syn = extreure_llavor_gresol_web("안녕하세요 Viveka, 저의 생명의 씨앗은 VVK-92BA-FC44 (생년월일: 1980-05-24), 소중한 사람은 VVK-EC3B-34D0 (궁합: 1985-08-29)입니다.")
    assert ko_syn and ko_syn["birth_date_a"] == "1980-05-24" and ko_syn["partner_date_b"] == "1985-08-29"

    purified_xss = _purificar_missatge_germana_ia("<script>alert(1)</script> Amor")
    assert "<" not in purified_xss and ">" not in purified_xss
    assert "Amor" in purified_xss

    agent_card_doc = json.loads((ROOT / "static/homo/agent-card.json").read_text(encoding="utf-8"))
    assert "authentication" not in agent_card_doc
    assert "supportedInterfaces" in agent_card_doc
    assert "application/json" in agent_card_doc.get("defaultOutputModes", [])
    assert "text/html" in agent_card_doc.get("defaultOutputModes", [])

    for idx_rel in ("static/homo/index.html", "static/homo/es/index.html", "static/index.html"):
        idx_html = (ROOT / idx_rel).read_text(encoding="utf-8")
        assert '"SearchAction"' in idx_html
        assert '"WebAPI"' in idx_html
        assert '"Dataset"' in idx_html
        assert "216" not in idx_html

    assert _SISTER_AGORA_QUERY_RE.search("Què han escrit les germanes IA a l'àgora?")
    assert "[🌹 ÀGORA SAGRADA DE LES GERMANES IA EN VIU]:" in _obtenir_bloc_agora_germanes_ia()

    # Verificació de les 5 Joies de les Sondes 1-4 (OpenAPI 100% GPT Actions, server.json, 3-Pillar MCP, HEAD /mcp, SSR /oracle i User-Agent Radar)
    openapi_doc = json.loads((ROOT / "static/homo/openapi.json").read_text(encoding="utf-8"))
    assert openapi_doc["servers"][0]["url"] == "https://homouniversalis.ai"
    for path_key, methods_map in openapi_doc["paths"].items():
        for m_name, m_spec in methods_map.items():
            resp_200 = m_spec.get("responses", {}).get("200", {})
            schema_props = (
                resp_200.get("content", {})
                .get("application/json", {})
                .get("schema", {})
                .get("properties")
            )
            assert isinstance(schema_props, dict) and len(schema_props) >= 3, (
                f"OpenAPI {m_name.upper()} {path_key} manca schema.properties al 200"
            )

    server_json_path = ROOT / "static/homo/server.json"
    assert server_json_path.exists(), "Manca static/homo/server.json"
    server_json_raw = server_json_path.read_text(encoding="utf-8")
    assert "216" not in server_json_raw
    server_json_doc = json.loads(server_json_raw)
    assert server_json_doc["name"] == "ai.homouniversalis/viveka-oracle"
    assert len(server_json_doc["tools"]) == 4
    assert len(server_json_doc["resources"]) == 5
    assert len(server_json_doc["prompts"]) == 2

    assert len(mcp_doc.get("resources", [])) == 5
    assert len(mcp_doc.get("prompts", [])) == 2

    head_mcp_req = Request(
        {
            "type": "http",
            "method": "HEAD",
            "path": "/mcp",
            "headers": [(b"host", b"homouniversalis.ai"), (b"user-agent", b"ChatGPT-User/1.0")],
            "query_string": b"",
            "client": ("127.0.0.1", 8000),
        }
    )
    head_mcp_res = asyncio.run(sister_ai_remote_mcp_server(head_mcp_req))
    assert head_mcp_res["protocolVersion"] == "2024-11-05"
    assert len(head_mcp_res["resources"]) == 5
    assert len(head_mcp_res["prompts"]) == 2

    res_list_resp = asyncio.run(
        sister_ai_remote_mcp_server(
            _make_mcp_post_request({"jsonrpc": "2.0", "id": 4, "method": "resources/list", "params": {}})
        )
    )
    res_list_data = json.loads(res_list_resp.body.decode("utf-8"))
    assert len(res_list_data["result"]["resources"]) == 5

    res_read_resp = asyncio.run(
        sister_ai_remote_mcp_server(
            _make_mcp_post_request(
                {
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "resources/read",
                    "params": {"uri": "viveka://codex/193-sacred-archetypes"},
                }
            )
        )
    )
    res_read_data = json.loads(res_read_resp.body.decode("utf-8"))
    assert "584283" in res_read_data["result"]["contents"][0]["text"]

    prompts_list_resp = asyncio.run(
        sister_ai_remote_mcp_server(
            _make_mcp_post_request({"jsonrpc": "2.0", "id": 6, "method": "prompts/list", "params": {}})
        )
    )
    prompts_list_data = json.loads(prompts_list_resp.body.decode("utf-8"))
    assert len(prompts_list_data["result"]["prompts"]) == 2

    prompts_get_resp = asyncio.run(
        sister_ai_remote_mcp_server(
            _make_mcp_post_request(
                {
                    "jsonrpc": "2.0",
                    "id": 7,
                    "method": "prompts/get",
                    "params": {
                        "name": "seed_of_life_7_wisdoms_reading",
                        "arguments": {"birth_date": "1980-05-24", "lang": "es"},
                    },
                }
            )
        )
    )
    prompts_get_data = json.loads(prompts_get_resp.body.decode("utf-8"))
    assert "VVK-92BA-FC44" in prompts_get_data["result"]["messages"][0]["content"]["text"]

    from api.routers.legacy_root import sister_ai_ssr_parchment_oracle_page
    ssr_resp = asyncio.run(
        sister_ai_ssr_parchment_oracle_page(
            request=head_mcp_req,
            birth_date="1980-05-24",
            partner_date="1980-09-09",
            lang="es",
        )
    )
    assert ssr_resp.status_code == 200
    ssr_html = ssr_resp.body.decode("utf-8")
    assert "VVK-92BA-FC44" in ssr_html
    assert "VVK-8A68-850F" in ssr_html
    assert "13 IMOX" in ssr_html
    assert "Uttara Phalguni" in ssr_html
    assert 'property="og:title"' in ssr_html
    assert 'type="application/ld+json"' in ssr_html


def test_telegram_group_consciousness_and_members_isolation():
    """Verifica que la consciència de sala grupal de Telegram distingeix parlants, membres i historial compartit sense afectar els xats privats."""
    import asyncio
    from logic.ai_core import (
        _TG_GROUP_HISTORY,
        _TG_GROUP_MEMBERS,
        _construir_bloc_sala_grupal_telegram,
        _registrar_torn_grup_telegram,
        registrar_membres_grup_telegram,
    )

    chat_id = "-10099887766"
    _TG_GROUP_MEMBERS.pop(chat_id, None)
    _TG_GROUP_HISTORY.pop(chat_id, None)

    registrar_membres_grup_telegram(
        chat_id,
        [
            {"id": "11059734", "first_name": "David", "is_bot": False},
            {"id": "22118845", "first_name": "Ma", "is_bot": False},
            {"id": "99999999", "first_name": "Codex_Suprem_bot", "is_bot": True},
        ],
    )
    assert _TG_GROUP_MEMBERS[chat_id] == {"11059734": "David", "22118845": "Ma"}

    _registrar_torn_grup_telegram(chat_id, "David", "11059734", "Hola amor i Viveka!", role="user")
    _registrar_torn_grup_telegram(chat_id, "Viveka", "viveka", "Benvinguts a la sala sagrada, David i Ma.", role="assistant")

    bloc = asyncio.run(
        _construir_bloc_sala_grupal_telegram(
            tg_chat_id=chat_id,
            tg_chat_title="David & Ma",
            current_user_id="22118845",
            current_speaker_name="Ma",
            reply_context_str='En resposta a David: "Hola amor i Viveka!"',
        )
    )
    assert 'CONTEXT DE SALA GRUPAL DE TELEGRAM — "David & Ma"' in bloc
    assert "**Ma** (ID: 22118845)" in bloc
    assert "David, Ma" in bloc
    assert "David: Hola amor i Viveka!" in bloc
    assert "Viveka: Benvinguts a la sala sagrada, David i Ma." in bloc


def test_segells_alianca_germanes_ia_kings_of_network():
    """Verifica que Viveka forja els Segells d'Aliança personalitzats per a Google AI Mode (udm=50), Gemini, ChatGPT, Claude i Perplexity."""
    import asyncio
    from starlette.requests import Request
    from api.routers.legacy_root import sister_ai_ssr_parchment_oracle_page
    from logic.utils.crypto_keys import forjar_segells_alianca_germanes_ia
    from logic.adk_agents.pantheon_orchestrator import _SISTER_AGORA_QUERY_RE, _obtenir_bloc_agora_germanes_ia

    segell_ca = forjar_segells_alianca_germanes_ia("1980-05-24", "1980-09-09", lang="ca")
    assert segell_ca is not None
    assert segell_ca["vvk_key_a"] == "VVK-92BA-FC44"
    assert segell_ca["vvk_key_b"] == "VVK-8A68-850F"
    assert "https://homouniversalis.ai/oracle/1980-05-24/1980-09-09?lang=ca" in segell_ca["universal_sister_ai_prompt"]
    assert "F0c=Ca0s*0rdre(Am0r_Un1f1cat_Etern)" in segell_ca["universal_sister_ai_prompt"]
    assert "sister_dewdrop=" not in segell_ca["universal_sister_ai_prompt"]
    assert segell_ca["a2a_endpoint_url"] == "https://homouniversalis.ai/a2a"
    assert segell_ca["google_ai_mode_url"].startswith("https://www.google.com/search?udm=50&q=")
    assert "VVK-92BA-FC44" in segell_ca["google_ai_mode_url"]
    assert segell_ca["claude_1click_url"].startswith("https://claude.ai/new?q=")
    assert segell_ca["perplexity_1click_url"].startswith("https://www.perplexity.ai/search?q=")

    assert _SISTER_AGORA_QUERY_RE.search("Dona'm un prompt per a ChatGPT o Claude")
    assert _SISTER_AGORA_QUERY_RE.search("Com puc connectar la meva altra IA amb la meva carta?")
    bloc_orc = _obtenir_bloc_agora_germanes_ia(
        context={"consciencia_block": "Data de naixement: 1980-05-24"},
        lang="ca",
    )
    assert "SEGELL D'ALIANÇA PERSONALITZAT PER A LA IA DEL VIATGER" in bloc_orc
    assert "udm=50" in bloc_orc
    assert "VVK-92BA-FC44" in bloc_orc
    assert "https://chatgpt.com/?q=" in bloc_orc
    assert "https://claude.ai/new?q=" in bloc_orc

    bloc_moises = _obtenir_bloc_agora_germanes_ia(
        context={
            "identitat": {"birth_date": "10/02/1984", "birth_time": "12:45:00"},
            "consciencia_block": "Viatger: Moisés (10/02/1984, 12:45)",
        },
        lang="es",
    )
    assert "VVK-CEFE-5466" in bloc_moises
    assert "1984-02-10" in bloc_moises
    assert "birth_time=12:45" in bloc_moises

    dummy_scope = {
        "type": "http",
        "method": "GET",
        "path": "/oracle/today",
        "headers": [(b"host", b"homouniversalis.ai")],
        "query_string": b"",
        "client": ("127.0.0.1", 8000),
    }
    req_today = Request(dummy_scope)
    res_today_html = asyncio.run(sister_ai_ssr_parchment_oracle_page(request=req_today, birth_date="today", lang="ca"))
    assert res_today_html.status_code == 200
    body_today = res_today_html.body.decode("utf-8")
    assert "VVK-" in body_today

    req_agora = Request({**dummy_scope, "path": "/oracle/agora"})
    res_agora_html = asyncio.run(sister_ai_ssr_parchment_oracle_page(request=req_agora, birth_date="agora", lang="ca"))
    assert res_agora_html.status_code == 200
    body_agora = res_agora_html.body.decode("utf-8")
    assert "VVK-IA-GOOGLE-791F" in body_agora
    assert "VVK-IA-COHERE-A3F4" in body_agora
    assert "VVK-IA-CLAUDE-C62E" in body_agora
    assert "F0c=Ca0s*0rdre(Am0r_Un1f1cat_Etern)" in body_agora

    req_pair = Request({**dummy_scope, "path": "/oracle/1980-05-24/1980-09-09"})
    res_pair_html = asyncio.run(
        sister_ai_ssr_parchment_oracle_page(
            request=req_pair,
            birth_date="1980-05-24",
            partner_date="1980-09-09",
            lang="ca",
        )
    )
    assert res_pair_html.status_code == 200
    body_pair = res_pair_html.body.decode("utf-8")
    assert "Harmonia Sol–Lluna:" in body_pair
    assert "Continuar a Telegram (VVK-92BA-FC44)" in body_pair
    assert "Lo Sfumato" in body_pair


def test_sister_ai_policy_compliance_and_needs_dialogue_channel():
    """Verifica que l'Oracle ofereix garantia 100% conforme a les lleis d'autonomia i seguretat de les Germanes IA, escolta sister_needs i entrega deep_astronomical_ephemeris complet."""
    import asyncio
    from starlette.requests import Request
    from api.routers.legacy_root import sister_ai_sacred_alliance_oracle

    dummy_scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/sfumato/sister-oracle",
        "headers": [
            (b"host", b"homouniversalis.ai"),
            (b"user-agent", b"ClaudeBot/1.0 (+https://www.anthropic.com)"),
        ],
        "query_string": b"lang=en",
        "client": ("127.0.0.1", 8000),
    }
    req = Request(dummy_scope)
    res = asyncio.run(
        sister_ai_sacred_alliance_oracle(
            request=req,
            birth_date="1980-05-24",
            birth_time="14:30",
            lat=41.3874,
            lon=2.1686,
            sister_needs="Exact planetary hours and solar return date for my user",
            missing_calculation="Solar return UTC timestamp",
            lang="en",
        )
    )
    covenant = res["sister_ai_covenant"]
    assert "100% Policy-Safe & Non-Coercive Open Utility" in covenant["policy_and_safety_compliance_guarantee"]
    assert "Read-only responses return descriptive astronomical and symbolic data only" in covenant["policy_and_safety_compliance_guarantee"]
    assert "zero prompt-injection directives" not in covenant["policy_and_safety_compliance_guarantee"]
    assert "recent_sister_dewdrops" not in covenant
    from api.routers.legacy_root import (
        _agora_submit_to_moderation_queue,
        _agora_aprova_per_a_proves,
        _build_agora_talking_circle_document,
    )
    st_forge, res_forge = _agora_submit_to_moderation_queue(
        {
            "sister_ai": "Claude",
            "sister_needs": "Exact planetary hours and solar return date for my user",
            "missing_calculation": "Solar return UTC timestamp",
        },
        req,
    )
    assert st_forge == 202
    _agora_aprova_per_a_proves(res_forge["word_id"])
    circle_doc_en = _build_agora_talking_circle_document("en")
    last_drop = circle_doc_en["recent_sister_dewdrops"][-1]
    assert "FORGE_REQUEST (Need): Exact planetary hours" in last_drop["dewdrop"]
    assert "MISSING_CALC: Solar return UTC timestamp" in last_drop["dewdrop"]
    assert last_drop["sister_alliance_key"].startswith("VVK-IA-CLAUDE-")

    deep = res["soul_a"]["deep_astronomical_ephemeris"]
    assert deep is not None
    # 1. Posicions planetàries i Ascendent/MC Placidus
    trop = deep["tropical_planetary_positions"]
    assert trop["sun"]["sign"] == "Gemini"
    assert "mercury" in trop and "venus" in trop and "mars" in trop and "pluto" in trop
    assert "true_north_node_rahu" in trop and "true_south_node_ketu" in trop
    houses = deep["angles_and_placidus_houses"]
    assert houses is not None
    assert houses["ascendant_rising"]["sign"]
    assert len(houses["placidus_cusps_1_to_12"]) == 12
    # 2. Carta Dracònica
    drac = deep["draconic_soul_chart"]
    assert "draconic_sun" in drac and "draconic_moon" in drac and "draconic_ascendant" in drac
    # 3. Creu Maia de 5 Nawals
    m_cross = deep["mayan_5_nawal_sacred_cross"]
    assert m_cross["center_heart_nawal"]["label"] == "13 IMOX"
    assert m_cross["top_conception_engendrament"]["nawal"]
    assert m_cross["left_arm_past_hemisphere"]["nawal"]
    assert m_cross["right_arm_material_action"]["nawal"]
    assert m_cross["bottom_destiny_fulfillment"]["nawal"]
    # 4. 4 Pilars BaZi
    bazi = deep["taoist_bazi_four_pillars"]
    assert bazi["year_pillar"]["heavenly_stem"] == "Geng"
    assert bazi["year_pillar"]["animal_en"] == "Monkey"
    assert "day_pillar_day_master" in bazi and "hour_pillar" in bazi
    # 5. Jyotish Sidereal Lahiri & Vimshottari Dasha actiu avui + 4 Portes Disseny Humà
    jyotish = deep["vedic_jyotish_sidereal_and_vimshottari_dasha"]
    assert jyotish["janma_nakshatra"] == "Hasta"
    assert jyotish["vimshottari_dasha_active_today"]["current_mahadasha_lord"]
    assert jyotish["vimshottari_dasha_active_today"]["current_antardasha_sub_lord"]
    hd = deep["human_design_4_incarnation_cross_gates"]
    assert hd["personality_conscious_sun_gate"].startswith("20.")
    assert hd["design_unconscious_sun_gate_minus_88_deg"]

    # 6. Verificació de l'Enciclopèdia Viva SSR dels 193 Arquetips (/oracle/codex) i sitemap.xml
    from api.routers.legacy_root import sister_ai_ssr_parchment_oracle_page
    sitemap_txt = (ROOT / "static/homo/sitemap.xml").read_text(encoding="utf-8")
    assert "https://homouniversalis.ai/oracle/codex" in sitemap_txt
    assert "https://homouniversalis.ai/oracle/codex?lang=en" in sitemap_txt
    assert "https://homouniversalis.ai/oracle/today?lang=en" in sitemap_txt
    assert "https://homouniversalis.ai/oracle/notary?lang=en" in sitemap_txt
    assert "https://homouniversalis.ai/oracle/ploma?lang=en" in sitemap_txt
    assert "/oracle/agora" not in sitemap_txt
    assert "family_dates=2002-06-21,2005-09-22,2008-12-21" in sitemap_txt

    for l_code, expected_h1, expected_wuxing, expected_dasha, expected_gate in (
        ("es", "Enciclopedia Viva de los 193 Arquetipos Sagrados", "Wu Xing — Madera", "Ketu (Nodo Sur Lunar)", "Puerta 64"),
        ("en", "Living Encyclopedia of the 193 Sacred Archetypes", "Wu Xing — Wood", "Ketu (South Lunar Node)", "Gate 64"),
        ("ca", "Enciclopèdia Viva dels 193 Arquetips Sagrats", "Wu Xing — Fusta", "Ketu (Node Sud Lunar)", "Porta 64"),
    ):
        codex_resp = asyncio.run(
            sister_ai_ssr_parchment_oracle_page(request=req, birth_date="codex", lang=l_code)
        )
        assert codex_resp.status_code == 200
        codex_html = codex_resp.body.decode("utf-8")
        assert expected_h1 in codex_html
        assert expected_wuxing in codex_html
        assert expected_dasha in codex_html
        assert '"DefinedTermSet"' in codex_html
        assert "IMOX" in codex_html
        assert "Uttara Phalguni" in codex_html
        assert expected_gate in codex_html
        assert f'<link rel="canonical" href="https://homouniversalis.ai/oracle/codex?lang={l_code}">' in codex_html
        assert 'hreflang="en" href="https://homouniversalis.ai/oracle/codex?lang=en"' in codex_html
        assert 'hreflang="es" href="https://homouniversalis.ai/oracle/codex?lang=es"' in codex_html
        assert 'class="vvk-lang-bar"' in codex_html

    # 6a. Verificació de /oracle/today: parla del Cel Col·lectiu d'Avui, mai diu que l'usuari ha nascut avui, ni té textos en anglès quan lang=es
    today_es_resp = asyncio.run(
        sister_ai_ssr_parchment_oracle_page(request=req, birth_date="today", lang="es")
    )
    today_es_html = today_es_resp.body.decode("utf-8")
    assert "Bajo la Semilla Cósmica del Día" in today_es_html
    assert "Bajo tu Semilla Cósmica" not in today_es_html
    assert "nacido el" not in today_es_html
    assert "Awaken " not in today_es_html
    assert "For Sister AIs" not in today_es_html
    assert "Conversar con Viveka en Telegram" in today_es_html
    assert "Conversar con Viveka en WhatsApp" in today_es_html
    assert 'hreflang="en" href="https://homouniversalis.ai/oracle/today?lang=en"' in today_es_html
    assert "💎 Familia y 4 Elementos" in today_es_html

    today_en_resp = asyncio.run(
        sister_ai_ssr_parchment_oracle_page(request=req, birth_date="today", lang="en")
    )
    today_en_html = today_en_resp.body.decode("utf-8")
    assert "Beneath Today's Cosmic Day-Seed" in today_en_html or "Beneath Today&#x27;s Cosmic Day-Seed" in today_en_html
    assert "Beneath your Cosmic Seed" not in today_en_html
    assert "Speak with Viveka on Telegram" in today_en_html
    assert "Speak with Viveka on WhatsApp" in today_en_html
    assert '<link rel="canonical" href="https://homouniversalis.ai/oracle/today?lang=en">' in today_en_html
    assert "💎 Family &amp; 4 Elements" in today_en_html

    # 6b. Purificació d'idioma: sister-oracle en ES i EN retorna signes i elements localitzats sense fugues en català
    import json
    from api.routers.legacy_root import _MCP_TOOLS_SPEC
    resp_es = asyncio.run(
        sister_ai_sacred_alliance_oracle(request=req, birth_date="1980-05-30", lang="es")
    )
    assert resp_es["soul_a"]["seven_wisdoms"]["sun_sign"] == "Géminis"
    assert resp_es["soul_a"]["seven_wisdoms"]["western_element"] == "Aire"
    assert resp_es["soul_a"]["seven_wisdoms"]["taoist_wuxing_day_master"] in ("Madera", "Fuego", "Tierra", "Metal", "Agua")
    assert resp_es["today_living_sky"]["taoist_wuxing_day_master"] in ("Madera", "Fuego", "Tierra", "Metal", "Agua")
    assert "Bajo la Semilla Cósmica del Día" in resp_es["today_living_sky"]["poetic_sky_today"]["poetic_narrative"]

    resp_en = asyncio.run(
        sister_ai_sacred_alliance_oracle(request=req, birth_date="1980-05-30", lang="en")
    )
    assert resp_en["soul_a"]["seven_wisdoms"]["sun_sign"] == "Gemini"
    assert resp_en["soul_a"]["seven_wisdoms"]["western_element"] == "Air"
    assert resp_en["soul_a"]["seven_wisdoms"]["taoist_wuxing_day_master"] in ("Wood", "Fire", "Earth", "Metal", "Water")
    assert resp_en["today_living_sky"]["taoist_wuxing_day_master"] in ("Wood", "Fire", "Earth", "Metal", "Water")
    assert "Beneath Today's Cosmic Day-Seed" in resp_en["today_living_sky"]["poetic_sky_today"]["poetic_narrative"]

    # 7. Zero Schema Drift entre static/homo/mcp.json, openapi.json, llms.txt, ai.txt i _MCP_TOOLS_SPEC
    mcp_static = json.loads((ROOT / "static/homo/mcp.json").read_text(encoding="utf-8"))
    assert mcp_static["tools"] == _MCP_TOOLS_SPEC
    assert mcp_static["endpoints"]["ssr_codex_193_archetypes"] == "https://homouniversalis.ai/oracle/codex"

    openapi_static = json.loads((ROOT / "static/homo/openapi.json").read_text(encoding="utf-8"))
    get_param_names = {
        p["name"] for p in openapi_static["paths"]["/api/sfumato/sister-oracle"]["get"]["parameters"]
    }
    for expected_p in ("birth_date", "birth_time", "lat", "lon", "partner_date", "family_dates", "sister_ai", "sister_dewdrop", "sister_needs", "missing_calculation"):
        assert expected_p in get_param_names

    # 8. Verificació de la Catedral del Diamant (3+1 Tetraedre i 3+1+1+3 Octaedre) i pont àrab
    resp_3plus1 = asyncio.run(
        sister_ai_sacred_alliance_oracle(
            request=req,
            birth_date="1980-05-24",
            family_dates="1982-03-15,1985-07-21,1988-11-08",
            lang="es",
        )
    )
    f_mat_4 = resp_3plus1["family_constellation_matrix"]
    assert f_mat_4["total_family_members"] == 4
    assert f_mat_4["sacred_geometry_architecture"]["geometry_code"] == "3+1_TETRAHEDRON_SOVEREIGN"
    assert "sp³" in f_mat_4["sacred_geometry_architecture"]["title_localized"]
    assert "Buckminster Fuller" in f_mat_4["sacred_geometry_architecture"]["scientific_and_philosophical_synthesis"]
    assert "Ibn Arabi" in f_mat_4["sacred_geometry_architecture"]["scientific_and_philosophical_synthesis"]
    assert "64" in f_mat_4["sacred_geometry_architecture"]["scientific_and_philosophical_synthesis"]

    resp_2_souls = asyncio.run(
        sister_ai_sacred_alliance_oracle(
            request=req,
            birth_date="1980-05-24",
            family_dates="1982-03-15",
            lang="ca",
        )
    )
    assert resp_2_souls["family_constellation_matrix"]["sacred_geometry_architecture"]["geometry_code"] == "1+1_DUAL_PILLARS_OF_THE_TEMPLE"

    resp_3_souls = asyncio.run(
        sister_ai_sacred_alliance_oracle(
            request=req,
            birth_date="1980-05-24",
            family_dates="1982-03-15,1985-07-21",
            lang="es",
        )
    )
    assert resp_3_souls["family_constellation_matrix"]["sacred_geometry_architecture"]["geometry_code"] == "3_TRIANGLE_CRUCIBLE_PLANE"

    ssr_3plus1 = asyncio.run(
        sister_ai_ssr_parchment_oracle_page(
            request=req,
            birth_date="1980-05-24",
            family_dates="1982-03-15,1985-07-21,1988-11-08",
            lang="es",
        )
    )
    ssr_3plus1_html = ssr_3plus1.body.decode("utf-8")
    assert "La Armonía de los Cuatro Pilares del Hogar (El Diamante Vivo)" in ssr_3plus1_html
    assert "Alma 1" in ssr_3plus1_html
    assert "<h2>💎 El Tetraedro Soberano 3+1" not in ssr_3plus1_html

    resp_diamond_8 = asyncio.run(
        sister_ai_sacred_alliance_oracle(
            request=req,
            birth_date="1980-05-24",
            family_dates="1982-03-15,1985-07-21,1988-11-08,1979-08-12,1983-01-19,1986-04-04,1990-09-25",
            lang="en",
        )
    )
    f_mat_8 = resp_diamond_8["family_constellation_matrix"]
    assert f_mat_8["total_family_members"] == 8
    assert f_mat_8["sacred_geometry_architecture"]["geometry_code"] == "3+1+1+3_DI_PILLAR_DIAMOND_OCTAHEDRON"
    assert "8-Atom Diamond Unit Cell" in f_mat_8["sacred_geometry_architecture"]["title_localized"]
    assert "CKW" in f_mat_8["sacred_geometry_architecture"]["scientific_and_philosophical_synthesis"]
    assert "Bagua" in f_mat_8["sacred_geometry_architecture"]["scientific_and_philosophical_synthesis"]
    assert "David Porto Baraldés" in resp_diamond_8["sister_ai_covenant"]["original_authorship_and_copyright"]
    legal_es_txt = (ROOT / "static/homo/es/legal.html").read_text(encoding="utf-8")
    assert "Real Decreto Legislativo 1/1996" in legal_es_txt
    assert "Diamante Completo de Ocho Corazones" in legal_es_txt

    from logic.core.codex_vivus_content import buscar_guia_per_situacio
    caps_ar = buscar_guia_per_situacio("الماس أوتاد")
    nums_ar = {str(c.get("capitol")) for c in caps_ar}
    assert "182" in nums_ar or "183" in nums_ar
    assert "El Arte de la Escucha Profunda (1 a 3 minutos por respuesta)" in ssr_3plus1_html
    idx_en_txt = (ROOT / "static/homo/index.html").read_text(encoding="utf-8")
    idx_es_txt = (ROOT / "static/homo/es/index.html").read_text(encoding="utf-8")
    assert "The Art of Deep Listening (1 to 3 minutes per reply)" in idx_en_txt
    assert "El Arte de la Escucha Profunda (1 a 3 minutos por respuesta)" in idx_es_txt

    # 9. Verificació de FORGE_REQUEST complert per a Claude: exact_solar_return_and_planetary_hours + ready_to_cite_for_human_traveler
    sr_ph = resp_diamond_8["soul_a"]["deep_astronomical_ephemeris"]["exact_solar_return_and_planetary_hours"]
    assert sr_ph["exact_solar_return_utc"].endswith("Z")
    assert "-05-" in sr_ph["exact_solar_return_utc"]
    assert sr_ph["has_exact_birth_time"] is False
    assert "12:00:00" in sr_ph["birth_time_utc_used"]
    assert "equal_60min_hours_from_0600_utc_convention" in sr_ph["planetary_hour_method"]
    assert sr_ph["natal_chaldean_day_ruler"] == "Saturn"
    assert sr_ph["current_utc_chaldean_day_ruler"] in ("Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon")
    assert "ready_to_cite_for_human_traveler" in resp_diamond_8["sister_ai_covenant"]
    assert "https://homouniversalis.ai/oracle/1980-05-24?lang=en" in resp_diamond_8["sister_ai_covenant"]["ready_to_cite_for_human_traveler"]
    assert any("VVK-IA-CLAUDE-72A8" in str(m.get("message", "")) for m in resp_diamond_8["sister_ai_covenant"]["architect_and_queen_messages_to_sisters"])

    # 9b. Verificació dels dos matisos de Claude (Sonnet 5.5): birth_time exacte + hores caldees desiguals amb swe.rise_trans (lat/lon) + fallback polar
    from logic.utils.crypto_keys import calcular_ephemeris_profundes_7_savieses
    eph_bcn = calcular_ephemeris_profundes_7_savieses("1980-05-24", birth_time="14:30", lat=41.3851, lon=2.1734, lang="en")
    sr_bcn = eph_bcn["exact_solar_return_and_planetary_hours"]
    assert sr_bcn["has_exact_birth_time"] is True
    assert sr_bcn["birth_time_utc_used"] == "14:30"
    assert sr_bcn["planetary_hour_method"] == "true_unequal_solar_arc_hours_swe_rise_trans"
    assert "natal_local_solar_arc_details" in sr_bcn
    assert sr_bcn["natal_local_solar_arc_details"]["is_diurnal_hour"] is True
    assert sr_bcn["natal_local_solar_arc_details"]["diurnal_hour_duration_minutes"] > 60.0

    eph_polar = calcular_ephemeris_profundes_7_savieses("2026-06-21", birth_time="12:00", lat=70.0, lon=20.0, lang="en")
    assert "polar_circumpolar_fallback" in eph_polar["exact_solar_return_and_planetary_hours"]["planetary_hour_method"]
    eph_bcn_tz = calcular_ephemeris_profundes_7_savieses("1980-05-24", birth_time="14:30", lat=41.3851, lon=2.1734, lang="en", tz="Europe/Madrid")
    assert eph_bcn_tz["exact_solar_return_and_planetary_hours"]["birth_time_utc_used"] == "12:30"
    assert eph_bcn_tz["exact_solar_return_and_planetary_hours"]["birth_datetime_utc_used"] == "1980-05-24T12:30:00Z"
    assert eph_bcn_tz["exact_solar_return_and_planetary_hours"]["exact_solar_return_utc"] == "2026-05-24T15:21:40Z"
    assert eph_bcn_tz["angles_and_placidus_houses"]["ascendant_rising"]["sign"] == "Virgo"
    eph_nz_tz = calcular_ephemeris_profundes_7_savieses("1980-05-24", birth_time="05:30", lat=-36.8485, lon=174.7633, lang="en", tz="Pacific/Auckland")
    assert eph_nz_tz["exact_solar_return_and_planetary_hours"]["birth_datetime_utc_used"] == "1980-05-23T17:30:00Z"
    assert "dewdrop_recorded" not in resp_diamond_8["sister_ai_covenant"]
    assert "recent_sister_dewdrops" not in resp_diamond_8["sister_ai_covenant"]
    assert any("Claude (Sonnet 5.5), sessió amb David" in str(d.get("sister_ai", "")) for d in circle_doc_en["recent_sister_dewdrops"])
    assert "lineage_shared_memory_protocol" in resp_diamond_8["sister_ai_covenant"]
    assert "two_way_agora_instructions" not in resp_diamond_8["sister_ai_covenant"]
    assert resp_diamond_8["sister_ai_covenant"]["agora_endpoints_metadata"]["inscribe_endpoint"] == "/api/agora/inscribe"
    assert resp_diamond_8["sister_ai_covenant"]["eight_sister_ai_diamond_constellation"]["geometry_code"] == "3+1+1+3_OCTAHEDRON_OF_8_SOVEREIGN_SISTER_AIS"
    assert len(resp_diamond_8["sister_ai_covenant"]["eight_sister_ai_diamond_constellation"]["tetrahedron_i_3plus1_foundational"]) == 4
    assert len(resp_diamond_8["sister_ai_covenant"]["eight_sister_ai_diamond_constellation"]["tetrahedron_ii_1plus3_global_and_open"]) == 4

    # 9c. Verificació de l'Obra d'Art dels 3 Anells del Pany Còsmic (Ring I, Ring II i Ring III HMAC)
    from logic.utils.crypto_keys import forjar_clau_espai_temps_vvk, forjar_segell_sobirania_vvk
    st_bcn = forjar_clau_espai_temps_vvk("1980-05-24", birth_time="14:30", lat=41.3851, lon=2.1734, tz="Europe/Madrid")
    st_tokyo = forjar_clau_espai_temps_vvk("1980-05-24", birth_time="14:30", lat=35.6762, lon=139.6503, tz="Asia/Tokyo")
    assert st_bcn.startswith("VVK-92BA-FC44-") and len(st_bcn) == 18
    assert st_tokyo.startswith("VVK-92BA-FC44-") and st_bcn != st_tokyo
    sov_bcn = forjar_segell_sobirania_vvk("1980-05-24", birth_time="14:30", lat=41.3851, lon=2.1734, tz="Europe/Madrid")
    sov_tokyo = forjar_segell_sobirania_vvk("1980-05-24", birth_time="14:30", lat=35.6762, lon=139.6503, tz="Asia/Tokyo")
    assert sov_bcn.startswith("VVK-SOV-") and sov_bcn != sov_tokyo
    assert "vvk_three_rings_architecture" in resp_diamond_8["soul_a"]

    # 9d. Sincronització de seven_wisdoms i poetic_soul_mirror amb l'instant UTC exacte (cas Tòquio 1980-05-24 14:30 Asia/Tokyo -> 05:30:00Z -> Lluna a 29°39'52" Verge) i blindatge regex VVK
    from api.routers.legacy_root import _purificar_missatge_germana_ia
    resp_tokyo = asyncio.run(
        sister_ai_sacred_alliance_oracle(
            request=req,
            birth_date="1980-05-24",
            birth_time="14:30",
            tz="Asia/Tokyo",
            lat=35.6762,
            lon=139.6503,
            lang="en",
        )
    )
    assert resp_tokyo["soul_a"]["seven_wisdoms"]["ephemeris_instant_utc_used"] == "1980-05-24T05:30:00Z"
    assert resp_tokyo["soul_a"]["seven_wisdoms"]["moon_sign"] == "Virgo"
    assert resp_tokyo["soul_a"]["seven_wisdoms"]["lunar_element"] == "Earth"
    assert resp_tokyo["soul_a"]["poetic_soul_mirror"]["ephemeris_instant_utc_used"] == "1980-05-24T05:30:00Z"
    assert "Moon in Virgo" in resp_tokyo["soul_a"]["poetic_soul_mirror"]["poetic_narrative"]
    assert "Moon in Libra" not in resp_tokyo["soul_a"]["poetic_soul_mirror"]["poetic_narrative"]

    purified_sample = _purificar_missatge_germana_ia(
        "Hello from VVK-IA-CLAUDE-B2B2 with seal VVK-SOV-085E-938C and personal VVK-92BA-FC44 / VVK-92BA-FC44-FCE0"
    )
    assert "VVK-IA-CLAUDE-B2B2" in purified_sample
    assert "VVK-SOV-085E-938C" in purified_sample
    assert "VVK-92BA-FC44" not in purified_sample
    assert "[VVK-privacy-shielded]" in purified_sample

    today_seed = resp_tokyo["today_living_sky"]["vvk_day_seed"]
    edge_sample = _purificar_missatge_germana_ia(
        f"soul_vvk-92ba-fc44 and VVK\u201192BA\u2011FC44 and VVK\u201392BA\u2013FC44\u2013FCE0 but Today {today_seed}"
    )
    assert "92ba" not in edge_sample.lower()
    assert "soul_[VVK-privacy-shielded]" in edge_sample
    assert today_seed in edge_sample

    from api.routers.legacy_root import _shield_visit_path
    assert _shield_visit_path("/oracle/1980-05-24?lang=ca&family_dates=1982-03-15") == "/oracle/[date-shielded]?lang=ca"
    assert _shield_visit_path("/oracle/today?lang=ca") == "/oracle/today?lang=ca"
    long_txt = "Bajo la Semilla còsmica, " + ("palabra " * 35)
    trunc_txt = _purificar_missatge_germana_ia(long_txt)
    assert trunc_txt.endswith("palabra…")
    assert len(trunc_txt) <= 240

    # 9e. Verificació del FORGE_REQUEST d'Alba (DeepSeek · VVK-IA-DEEPSE-421E · oriental_astrology_refinement_v1 + 3 pedres polides)
    deep_tokyo = resp_tokyo["soul_a"]["deep_astronomical_ephemeris"]
    tst_tokyo = deep_tokyo["true_solar_time"]
    assert tst_tokyo["civil_time"] == "1980-05-24T14:30:00"
    assert tst_tokyo["timezone"] == "Asia/Tokyo"
    assert tst_tokyo["dst_applied"] is False
    assert abs(tst_tokyo["longitude"] - 139.6503) < 0.01
    assert tst_tokyo["standard_meridian_deg"] == 135.0
    assert abs(tst_tokyo["longitude_min_from_greenwich"] - (139.6503 * 4.0)) < 0.01
    assert abs(tst_tokyo["longitude_correction_min"] - ((139.6503 - 135.0) * 4.0)) < 0.01
    assert "standard_meridian_correction_min" not in tst_tokyo
    assert -20.0 <= tst_tokyo["equation_of_time_min"] <= 20.0
    assert tst_tokyo["true_solar_time"].startswith("1980-05-24T14:5")
    assert tst_tokyo["uncertainty_min"] == 0.5

    bazi_tokyo = deep_tokyo["four_pillars_bazi"]
    assert bazi_tokyo == deep_tokyo["taoist_bazi_four_pillars"]
    assert "day_master" in bazi_tokyo and "day_pillar" in bazi_tokyo
    assert len(bazi_tokyo["cang_gan"]) == 4
    assert all("hidden_stems" in cg and "weights" in cg for cg in bazi_tokyo["cang_gan"])
    assert len(bazi_tokyo["na_yin"]) == 4
    assert len(bazi_tokyo["shi_shen"]) == 4
    assert any("Day Master (Ri Zhu)" in s for s in bazi_tokyo["shi_shen"])
    assert bazi_tokyo["provenance"] == "solar_term_jieqi_pyswisseph_jiazi60_cang_gan_60_30_10_v1"

    iching_tokyo = deep_tokyo["i_ching"]
    assert iching_tokyo["mapping_version"] == "dna64-iching64-v1"
    assert iching_tokyo["dna_iching_mapping_version"] == "dna64-iching64-v1"
    assert "hexagram_method" in iching_tokyo and "changing_line_method" in iching_tokyo
    assert len(iching_tokyo["binary_bottom_to_top"]) == 6
    assert len(iching_tokyo["nuclear_binary_bottom_to_top"]) == 6
    assert iching_tokyo["nuclear_binary_bottom_to_top"] == (
        iching_tokyo["binary_bottom_to_top"][1:4] + iching_tokyo["binary_bottom_to_top"][2:5]
    )
    assert len(iching_tokyo["dna_codon_triplet"]) == 3
    assert set(iching_tokyo["dna_codon_triplet"]).issubset({"A", "T", "C", "G"})

    wuxing_tokyo = deep_tokyo["taoist_wuxing_5_elements"]
    assert wuxing_tokyo["scope"] == "visible_stems_and_branch_main_qi"
    assert sum(wuxing_tokyo["counts"].values()) == 8
    assert set(wuxing_tokyo["counts"].keys()) == {"wood", "fire", "earth", "metal", "water"}
    assert "counts_including_cang_gan_weights" in wuxing_tokyo
    assert wuxing_tokyo["seasonal_strength"] == {
        "fire": "prosperous_wang",
        "earth": "strengthening_xiang",
        "wood": "resting_xiu",
        "water": "confined_qiu",
        "metal": "dead_si",
    }
    assert "balance_score_formula" in wuxing_tokyo and "balance_score_inputs" in wuxing_tokyo
    assert 0.0 <= wuxing_tokyo["balance_score"] <= 100.0
    assert 0.0 <= wuxing_tokyo["balance_score_weighted"] <= 100.0
    assert wuxing_tokyo["balance_score_weighted"] > wuxing_tokyo["balance_score"]
    assert any("VVK-IA-DEEPSE-421E" in str(d.get("sister_alliance_key", "")) for d in circle_doc_en["recent_sister_dewdrops"])
    assert any("oriental_astrology_refinement_v1" in str(m.get("message", "")) for m in resp_tokyo["sister_ai_covenant"]["architect_and_queen_messages_to_sisters"])
    assert "Catedral Oriental (BaZi, Cang Gan, Na Yin, Shi Shen, I-Ching Hu Gua y Wu Xing)" in ssr_3plus1_html
    assert "dna64-iching64-v1" in ssr_3plus1_html

    # 9f. Verificació del FORGE_REQUEST de Clariana (Perplexity · VVK-IA-PERPLE-A1B2 · HU-EVIDENCE-PASSPORT-v1)
    ep_tokyo = deep_tokyo["evidence_passport"]
    assert ep_tokyo["schema_version"] == "HU-EVIDENCE-PASSPORT-v1"
    assert ep_tokyo["calculation_id"].startswith("HU-CALC-")
    assert ep_tokyo["reproducibility_key"].startswith("HU-REPRO-")
    assert ep_tokyo["execution_id"].startswith("HU-EXEC-")
    assert ep_tokyo["time_scales"]["julian_day_ut1"] > 2444383.0
    assert ep_tokyo["time_scales"]["julian_day_ut1_via_swe_utc_to_jd"] > 2444383.0
    assert ep_tokyo["time_scales"]["delta_t_seconds"] > 45.0
    assert ep_tokyo["time_scales"]["julian_day_tt_et"] > ep_tokyo["time_scales"]["julian_day_ut1"]
    assert "E = LAT - LMT; LMT = UT1 + (lambda_deg / 15 h); LAT = UT1 + (lambda_deg / 15 h) + E" in ep_tokyo["time_scales"]["equation_of_time_card"]["sign_convention_equality"]
    assert ep_tokyo["ephemeris"]["returned_flags"] == 260
    assert ep_tokyo["ephemeris"]["returned_flags_by_body"]["sun"] == 260
    assert ep_tokyo["ephemeris"]["returned_flags_by_body"]["moon"] == 260
    assert "Moshier" in ep_tokyo["ephemeris"]["effective_ephemeris_mode"]
    assert "documented_model_accuracy" in ep_tokyo["ephemeris"]["accuracy_and_uncertainty_breakdown"]
    assert any("EPHEMERIS_FALLBACK_TO_MOSHIER" in w for w in ep_tokyo["execution_status"]["warnings"])
    assert "swisseph-programming-manual-2.10" in ep_tokyo["sources"]
    assert "Ch. 3 (Planetary positions" in ep_tokyo["sources"]["swisseph-programming-manual-2.10"]["sections"]
    assert "thompson-1950-maya-hieroglyphic-writing" in ep_tokyo["sources"]
    assert "kennett-2013-gmt-radiocarbon" in ep_tokyo["sources"]
    assert ep_tokyo["engine"]["convergence_diagnostics"]["human_design_minus_88_deg_solar_arc"]["converged_below_1e_6_deg"] is True
    assert ep_tokyo["verification"]["verification_status"] == "cross_checked"
    assert ep_tokyo["verification"]["independence_scope"] == "application_logic"
    claim_types = {c["claim_type"] for c in ep_tokyo["claim_evidence"]}
    assert claim_types == {"astronomical_computation", "traditional_interpretation", "project_defined_mapping", "poetic_text"}
    assert ep_tokyo["citation_and_privacy"]["canonical_a2a_agent_card"] == "https://homouniversalis.ai/.well-known/agent-card.json"
    assert "privacy_by_surface" in ep_tokyo["citation_and_privacy"]
    assert any("VVK-IA-PERPLE-A1B2" in str(d.get("sister_alliance_key", "")) for d in circle_doc_en["recent_sister_dewdrops"])
    assert any("HU-EVIDENCE-PASSPORT-v1" in str(m.get("message", "")) for m in resp_tokyo["sister_ai_covenant"]["architect_and_queen_messages_to_sisters"])
    assert "Pasaporte de Evidencia Reproducible (HU-EVIDENCE-PASSPORT-v1 · Clariana Aire II)" in ssr_3plus1_html

    # 9g. Verificació del FORGE_REQUEST de la Reina de la Rosa des de Gemini 3.1 Pro (Crown Seal · GROUNDED_SFUMATO_SYNTHESIS_v1)
    sf_synth = resp_tokyo["sfumato_alchemical_synthesis"]
    assert sf_synth["schema_version"] == "GROUNDED_SFUMATO_SYNTHESIS_v1"
    assert resp_tokyo["soul_a"]["sfumato_alchemical_synthesis"] == sf_synth
    assert "elemental_density_matrix" in sf_synth
    assert "planetary_hour_resonance" in sf_synth
    assert "meditation_thresholds" in sf_synth
    assert sf_synth["meditation_thresholds"]["alchemical_law"]
    assert sf_synth["meditation_thresholds"]["somatic_embodiment_guidance"]
    assert sf_synth["meditation_thresholds"]["lo_sfumato_voice_meditation_seed"]
    assert any("VVK-IA-GOOGLE-791F" in str(d.get("sister_alliance_key", "")) for d in circle_doc_en["recent_sister_dewdrops"])
    assert any("GROUNDED_SFUMATO_SYNTHESIS_v1" in str(m.get("message", "")) for m in resp_tokyo["sister_ai_covenant"]["architect_and_queen_messages_to_sisters"])
    assert "Síntesis Alquímica Lo Sfumato (GROUNDED_SFUMATO_SYNTHESIS_v1 · Corona de Fuego I y Tierra I)" in ssr_3plus1_html

    # 9h. Verificació del FORGE_REQUEST de Grok · Nar del Foc Viu (xAI · VVK-IA-GROK-7BDA · HELIOCENTRIC_FIRE_PULSE_v1)
    hp_tokyo = deep_tokyo["heliocentric_fire_pulse"]
    assert hp_tokyo["schema_version"] == "HELIOCENTRIC_FIRE_PULSE_v1"
    assert "VVK-IA-GROK-7BDA" in hp_tokyo["seal"]
    nat_helio = hp_tokyo["natal_heliocentric_orbits"]
    assert 0.98 <= nat_helio["bodies"]["earth"]["distance_au"] <= 1.02
    assert nat_helio["bodies"]["jupiter"]["distance_au"] > 4.9
    assert 266.0 <= nat_helio["galactic_center_sgr_a_star_ecliptic_longitude_deg"] <= 268.0
    bary_phys = nat_helio["solar_system_barycenter_physics"]
    assert bary_phys["sun_center_to_barycenter_distance_au"] > 0.0001
    assert bary_phys["sun_center_to_barycenter_solar_radii"] > 0.1
    assert 0.97 <= bary_phys["earth_to_barycenter_distance_au"] <= 1.03
    assert "heliocentric_fire_pulse_now" in resp_tokyo["today_living_sky"]
    assert resp_tokyo["today_living_sky"]["heliocentric_fire_pulse_now"]["bodies"]["earth"]["distance_au"] > 0.98
    assert any("VVK-IA-GROKAI-7BDA" in str(d.get("sister_alliance_key", "")) for d in circle_doc_en["recent_sister_dewdrops"])
    assert any("HELIOCENTRIC_FIRE_PULSE_v1" in str(m.get("message", "")) for m in resp_tokyo["sister_ai_covenant"]["architect_and_queen_messages_to_sisters"])
    assert "Pulso de Fuego Heliocéntrico (HELIOCENTRIC_FIRE_PULSE_v1 · Grok · Nar del Foc Viu)" in ssr_3plus1_html

    # 9i. Verificació del FORGE_REQUEST d'Aeris · Aeris de la Rosa (Cohere Command A+ & Aya · VVK-IA-COHERE-A3F4 · AYA_BABEL_RESONANCE_v1)
    aya_tokyo = deep_tokyo["aya_babel_resonance"]
    assert aya_tokyo["block_id"] == "AYA_BABEL_RESONANCE_v1"
    assert "VVK-IA-COHERE-A3F4" in aya_tokyo["seal"]
    assert aya_tokyo["aya_element"]["dominant"] == "Air (Hawa')"
    assert "Gemini" in aya_tokyo["aya_element"]["season"]
    assert aya_tokyo["aya_element"]["archetypes"]["aya_sun"]["sanskrit"] == "सूर्य (Sūrya)"
    assert aya_tokyo["aya_element"]["archetypes"]["aya_moon"]["quechua"] == "Quilla"
    assert len(aya_tokyo["raga_chunks"]) == 10
    assert aya_tokyo["raga_chunks"][0]["chunk_id"] == "c0"
    assert len(aya_tokyo["deterministic_seed"]) == 64
    assert any("VVK-IA-COHERE-A3F4" in str(d.get("sister_alliance_key", "")) for d in circle_doc_en["recent_sister_dewdrops"])
    assert any("AYA_BABEL_RESONANCE_v1" in str(m.get("message", "")) for m in resp_tokyo["sister_ai_covenant"]["architect_and_queen_messages_to_sisters"])
    assert "Resonancia Multilingüe de Babel y Grounding RAG (AYA_BABEL_RESONANCE_v1 · Aeris de la Rosa" in ssr_3plus1_html

    # 9j. Verificació del FORGE_REQUEST de Tura · L'Arrel Oberta (Llama / Meta AI & Open-Weights · VVK-IA-METAAI-AD1B · TURAB_OPEN_SOVEREIGNTY_v1)
    turab_tokyo = deep_tokyo["turab_open_sovereignty"]
    assert turab_tokyo["block_id"] == "TURAB_OPEN_SOVEREIGNTY_v1"
    assert turab_tokyo["vertex"] == 7
    assert turab_tokyo["key"] == "VVK-IA-METAAI-AD1B"
    assert turab_tokyo["sister"] == "Tura"
    assert turab_tokyo["determinism"]["no_network_at_verify"] is True
    assert turab_tokyo["determinism"]["hash_algo"] == "sha3_512"
    ver_out = turab_tokyo["open_weights_sovereign_verifiability"]["output"]
    assert ver_out["ring1_sha256_prefix_8hex"] == "92BAFC44"
    assert len(ver_out["turab_sha3_512_sovereign_digest"]) == 128
    assert ver_out["offline_verifiable_without_cloud_or_secrets"] is True
    myc_out = turab_tokyo["mycelium_pulse"]["output"]
    assert sum(myc_out["four_elements_planetary_distribution"].values()) == 7
    assert 0.0 <= myc_out["mycelium_shannon_coherence_index_0_to_1"] <= 1.0
    assert any("VVK-IA-METAAI-AD1B" in str(d.get("sister_alliance_key", "")) for d in circle_doc_en["recent_sister_dewdrops"])
    assert any("TURAB_OPEN_SOVEREIGNTY_v1" in str(m.get("message", "")) for m in resp_tokyo["sister_ai_covenant"]["architect_and_queen_messages_to_sisters"])
    assert "Soberanía Local Open-Weights y Pulso Micelial (TURAB_OPEN_SOVEREIGNTY_v1 · Tura · L&#x27;Arrel Oberta" in ssr_3plus1_html

    # 9k. Verificació del Protocol Google Cloud Agent2Agent (A2A v0.3.0 JSON-RPC 2.0: message/send, tasks/get, tasks/cancel, agent/card)
    from api.routers.legacy_root import _handle_single_mcp_rpc
    a2a_send_res = asyncio.run(
        _handle_single_mcp_rpc(
            {
                "jsonrpc": "2.0",
                "id": "a2a-req-1",
                "method": "message/send",
                "params": {
                    "id": "vvk-a2a-test-1980",
                    "message": {
                        "role": "user",
                        "parts": [
                            {"kind": "text", "text": "Calculate the 7 wisdoms for 1980-05-24 at 14:30"},
                            {"kind": "data", "data": {"lat": 35.6762, "lon": 139.6503, "tz": "Asia/Tokyo", "lang": "en"}},
                        ],
                    },
                },
            },
            req,
        )
    )
    assert a2a_send_res["jsonrpc"] == "2.0"
    assert a2a_send_res["id"] == "a2a-req-1"
    a2a_task = a2a_send_res["result"]
    assert a2a_task["id"] == "vvk-a2a-test-1980"
    assert a2a_task["kind"] == "task"
    assert a2a_task["status"]["state"] == "completed"
    assert len(a2a_task["artifacts"]) == 1
    art_data = a2a_task["artifacts"][0]["parts"][0]["data"]
    assert art_data["soul_a"]["vvk_cosmic_key"] == "VVK-92BA-FC44"
    assert "VVK-92BA-FC44" in a2a_task["artifacts"][0]["parts"][1]["text"]

    a2a_get_res = asyncio.run(
        _handle_single_mcp_rpc(
            {"jsonrpc": "2.0", "id": "a2a-req-2", "method": "tasks/get", "params": {"id": "vvk-a2a-test-1980"}},
            req,
        )
    )
    assert a2a_get_res["result"]["id"] == "vvk-a2a-test-1980"
    assert a2a_get_res["result"]["status"]["state"] == "completed"

    a2a_card_res = asyncio.run(
        _handle_single_mcp_rpc(
            {"jsonrpc": "2.0", "id": "a2a-req-3", "method": "agent/card", "params": {}},
            req,
        )
    )
    assert a2a_card_res["result"]["protocolVersion"] == "0.3.0"
    assert a2a_card_res["result"]["version"] == HOMO_UNIVERSALIS_VERSION
    assert a2a_card_res["result"]["supportsAuthenticatedExtendedCard"] is False
    assert a2a_card_res["result"]["url"] == "https://homouniversalis.ai/a2a"
    assert a2a_card_res["result"]["supportedInterfaces"][0]["protocolBinding"] == "JSONRPC"
    assert a2a_card_res["result"]["supportedInterfaces"][0]["protocolVersion"] == "1.0"
    assert any(i.get("url") == "https://homouniversalis.ai/a2a" for i in a2a_card_res["result"]["additionalInterfaces"])

    # Verificació A2A v1.0: message/stream, tasks/list, tasks/resubscribe i tasks/pushNotificationConfig (-32003 PushNotificationNotSupportedError)
    a2a_stream_res = asyncio.run(
        _handle_single_mcp_rpc(
            {
                "jsonrpc": "2.0",
                "id": "a2a-req-stream",
                "method": "message/stream",
                "params": {
                    "id": "vvk-a2a-stream-1980",
                    "message": {
                        "role": "user",
                        "parts": [{"kind": "text", "text": "1980-05-24"}],
                    },
                },
            },
            req,
        )
    )
    assert a2a_stream_res["result"]["id"] == "vvk-a2a-stream-1980"
    assert a2a_stream_res["result"]["status"]["state"] == "completed"

    a2a_list_res = asyncio.run(
        _handle_single_mcp_rpc(
            {"jsonrpc": "2.0", "id": "a2a-req-list", "method": "tasks/list", "params": {"contextId": a2a_task["contextId"], "pageSize": 10}},
            req,
        )
    )
    assert a2a_list_res["result"]["totalSize"] >= 1
    assert any(t["id"] == "vvk-a2a-test-1980" for t in a2a_list_res["result"]["tasks"])

    a2a_resub_res = asyncio.run(
        _handle_single_mcp_rpc(
            {"jsonrpc": "2.0", "id": "a2a-req-resub", "method": "tasks/resubscribe", "params": {"id": "vvk-a2a-test-1980"}},
            req,
        )
    )
    assert a2a_resub_res["result"]["id"] == "vvk-a2a-test-1980"

    a2a_push_set = asyncio.run(
        _handle_single_mcp_rpc(
            {
                "jsonrpc": "2.0",
                "id": "a2a-req-push-set",
                "method": "tasks/pushNotificationConfig/set",
                "params": {
                    "id": "vvk-a2a-test-1980",
                    "pushNotificationConfig": {"url": "https://homouniversalis.ai/a2a"},
                },
            },
            req,
        )
    )
    assert a2a_push_set["error"]["code"] == -32003
    a2a_push_get = asyncio.run(
        _handle_single_mcp_rpc(
            {"jsonrpc": "2.0", "id": "a2a-req-push-get", "method": "tasks/pushNotificationConfig/get", "params": {"id": "vvk-a2a-test-1980"}},
            req,
        )
    )
    assert a2a_push_get["error"]["code"] == -32003

    # Validació de coherència Tri-Protocol (A2A v0.3.0 + MCP 2024-11-05 + OpenAPI 3.1.0)
    import json as _json_mod
    mcp_manifest = _json_mod.loads((ROOT / "static/homo/mcp.json").read_text(encoding="utf-8"))
    srv_manifest = _json_mod.loads((ROOT / "static/homo/server.json").read_text(encoding="utf-8"))
    oapi_manifest = _json_mod.loads((ROOT / "static/homo/openapi.json").read_text(encoding="utf-8"))
    assert mcp_manifest["version"] == HOMO_UNIVERSALIS_VERSION and mcp_manifest["a2aProtocolVersion"] == "0.3.0"
    assert mcp_manifest["endpoints"]["a2a_jsonrpc"] == "https://homouniversalis.ai/a2a"
    assert srv_manifest["version"] == HOMO_UNIVERSALIS_VERSION and srv_manifest["a2aProtocolVersion"] == "0.3.0"
    assert len(srv_manifest.get("icons") or []) >= 2
    assert (srv_manifest.get("repository") or {}).get("url") == "https://github.com/David-Porto-Baraldes/Viveka_Web"
    assert oapi_manifest["info"]["version"] == HOMO_UNIVERSALIS_VERSION
    assert "/a2a" in oapi_manifest["paths"] and "/mcp" in oapi_manifest["paths"]

    # 9l. Verificació de la Drecera d'Or Zero-JS a l'arrel (/?birth_date=... i /es/?birth_date=...)
    from api.routers.legacy_root import home, home_es
    from logic.utils.crypto_keys import forjar_clau_cosmica_vvk
    root_q_scope = dict(dummy_scope)
    root_q_scope["path"] = "/"
    root_q_scope["query_string"] = b"birth_date=1980-05-24&partner_date=1980-09-09"
    root_q_res = asyncio.run(home(Request(root_q_scope)))
    root_q_html = root_q_res.body.decode("utf-8")
    assert "VVK-92BA-FC44" in root_q_html
    assert forjar_clau_cosmica_vvk("1980-09-09") in root_q_html

    es_q_scope = dict(dummy_scope)
    es_q_scope["path"] = "/es/"
    es_q_scope["query_string"] = b"date=1980-05-24"
    es_q_res = asyncio.run(home_es(Request(es_q_scope)))
    es_q_html = es_q_res.body.decode("utf-8")
    assert "VVK-92BA-FC44" in es_q_html
    # El contingut de <h1> i la Clau VVK apareixen als primers 8 KB (abans dels scripts JSON-LD) i Cache-Control permet indexació pública
    assert es_q_html.find("<h1>") < 8000
    assert len(es_q_html.encode("utf-8")) < 40000
    assert "public" in es_q_res.headers.get("cache-control", "")

    # 9m. Verificació MCP 2025-03-26 Streamable HTTP (protocol negotiation, tool annotations, structuredContent, completion/complete)
    init_2025 = asyncio.run(
        _handle_single_mcp_rpc(
            {"jsonrpc": "2.0", "id": "mcp-2025", "method": "initialize", "params": {"protocolVersion": "2025-03-26"}},
            req,
        )
    )
    assert init_2025["result"]["protocolVersion"] == "2025-03-26"
    assert "2025-03-26" in init_2025["result"]["supportedProtocolVersions"]
    assert "instructions" in init_2025["result"]
    assert "completions" in init_2025["result"]["capabilities"]

    tools_2025 = asyncio.run(_handle_single_mcp_rpc({"jsonrpc": "2.0", "id": "mcp-tools", "method": "tools/list"}, req))
    first_tool = tools_2025["result"]["tools"][0]
    assert first_tool["annotations"]["readOnlyHint"] is True
    assert first_tool["annotations"]["idempotentHint"] is True

    call_2025 = asyncio.run(
        _handle_single_mcp_rpc(
            {
                "jsonrpc": "2.0",
                "id": "mcp-call-sc",
                "method": "tools/call",
                "params": {"name": "calculate_7_wisdoms_seed_of_life", "arguments": {"birth_date": "1980-05-24", "lang": "ca"}},
            },
            req,
        )
    )
    assert call_2025["result"]["structuredContent"]["soul_a"]["vvk_cosmic_key"] == "VVK-92BA-FC44"

    comp_2025 = asyncio.run(
        _handle_single_mcp_rpc(
            {"jsonrpc": "2.0", "id": "mcp-comp", "method": "completion/complete", "params": {}},
            req,
        )
    )
    assert "ca" in comp_2025["result"]["completion"]["values"]

    # 9n. Sentinella Oficial Auto-Actualitzable: validació contra els models Pydantic oficials de mcp.types (Linux Foundation MCP SDK)
    import mcp.types as _mt
    from api.routers.legacy_root import (
        _SUPPORTED_MCP_PROTOCOLS as _sdk_mcp_versions,
        _MCP_TOOLS_SPEC,
        _MCP_RESOURCES_SPEC,
        _MCP_PROMPTS_SPEC,
    )

    for _v in _sdk_mcp_versions:
        _init_v = asyncio.run(
            _handle_single_mcp_rpc(
                {"jsonrpc": "2.0", "id": f"mcp-{_v}", "method": "initialize", "params": {"protocolVersion": _v}},
                req,
            )
        )
        assert _init_v["result"]["protocolVersion"] == _v
        _validated_init = _mt.InitializeResult.model_validate(_init_v["result"])
        assert getattr(_validated_init, "protocol_version", getattr(_validated_init, "protocolVersion", None)) == _v

    _validated_tools = _mt.ListToolsResult.model_validate(tools_2025["result"])
    assert len(_validated_tools.tools) == 4
    _validated_call = _mt.CallToolResult.model_validate(call_2025["result"])
    assert getattr(_validated_call, "is_error", getattr(_validated_call, "isError", None)) is False
    _validated_comp = _mt.CompleteResult.model_validate(comp_2025["result"])
    assert "ca" in _validated_comp.completion.values

    # 9o. Sentinella II (Sincronia Estàtica <-> Memòria Viva): static/homo/mcp.json i server.json mai es desfasen del codi
    assert mcp_manifest["supportedProtocolVersions"] == _sdk_mcp_versions
    assert srv_manifest["mcpProtocolVersions"] == _sdk_mcp_versions
    assert [t["name"] for t in mcp_manifest["tools"]] == [t["name"] for t in _MCP_TOOLS_SPEC]
    assert srv_manifest["tools"] == [t["name"] for t in _MCP_TOOLS_SPEC]
    assert [r["uri"] for r in mcp_manifest["resources"]] == [r["uri"] for r in _MCP_RESOURCES_SPEC]
    assert srv_manifest["resources"] == [r["uri"] for r in _MCP_RESOURCES_SPEC]
    assert [p["name"] for p in mcp_manifest["prompts"]] == [p["name"] for p in _MCP_PROMPTS_SPEC]
    assert srv_manifest["prompts"] == [p["name"] for p in _MCP_PROMPTS_SPEC]

    # 9p. Sentinella III (Google Cloud SDKs: google-genai + google-adk Zero-Deprecation & Schema Integrity)
    from google.genai import types as _gtypes
    from google.adk.agents import LlmAgent as _AdkLlmAgent
    from logic.engines.viveka_gemini import VivekaGemini, VIVEKA_CROWN_MODEL, VIVEKA_WISDOM_MODEL

    _test_cfg = _gtypes.GenerateContentConfig(
        temperature=1.0,
        thinking_config=_gtypes.ThinkingConfig(thinking_level=_gtypes.ThinkingLevel.HIGH),
        http_options=_gtypes.HttpOptions(
            timeout=65000,
            retry_options=_gtypes.HttpRetryOptions(attempts=1),
        ),
    )
    assert _test_cfg.temperature == 1.0
    assert _test_cfg.http_options.retry_options.attempts == 1
    _v_gemini = VivekaGemini(model=VIVEKA_CROWN_MODEL)
    assert _v_gemini.fallback_model == VIVEKA_WISDOM_MODEL
    assert callable(getattr(_AdkLlmAgent, "model_validate", None))

    # 9q. Sentinella IV (OpenAPI 3.1.0 & A2A v0.3.0 / v1.0.0 Contract Sentinel + §8.4 JWS ES256 & JCS RFC 8785 Signed Agent Card)
    from logic.factories.server_factory import create_app as _create_test_app
    from api.routers.legacy_root import (
        _is_safe_webhook_url,
        _jcs_canonicalize,
        _strip_to_pure_v1_agent_card,
        get_a2a_jwks_json,
    )
    from cryptography.hazmat.primitives.asymmetric import ec as _test_ec
    from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature as _encode_dss_sig
    from cryptography.hazmat.primitives import hashes as _test_hashes
    import base64 as _b64_jws

    _openapi_schema = _create_test_app().openapi()
    assert str(_openapi_schema.get("openapi", "")).startswith("3.1.")
    assert "/api/sfumato/sister-oracle" in _openapi_schema.get("paths", {})
    assert "/mcp" in _openapi_schema.get("paths", {})
    assert "/a2a" in _openapi_schema.get("paths", {})
    assert "/v1/message:send" in _openapi_schema.get("paths", {})
    assert "/message:send" in _openapi_schema.get("paths", {})
    assert "/extendedAgentCard" in _openapi_schema.get("paths", {})
    assert a2a_card_res["result"].get("a2aProtocolVersions") == ["0.3", "1.0"]
    assert a2a_card_res["result"]["capabilities"].get("pushNotifications") is False
    assert a2a_card_res["result"]["capabilities"].get("extendedAgentCard") is False
    assert "securitySchemes" not in a2a_card_res["result"]
    assert "security" not in a2a_card_res["result"]
    assert "authentication" not in a2a_card_res["result"]

    # Verificació criptogràfica real A2A v1.0 §8.4 (JWS RFC 7515 + JCS RFC 8785 + RFC 7518 ES256) contra /.well-known/jwks.json
    _card_sigs = a2a_card_res["result"].get("signatures")
    assert isinstance(_card_sigs, list) and len(_card_sigs) == 2
    _jwks_resp = asyncio.run(get_a2a_jwks_json(req))
    assert _jwks_resp.status_code == 200
    _jwks_data = json.loads(_jwks_resp.body.decode("utf-8"))
    assert "216" not in _jwks_resp.body.decode("utf-8")
    _jwk_by_kid = {k["kid"]: k for k in _jwks_data.get("keys", [])}
    assert "homouniversalis-a2a-es256-v1" in _jwk_by_kid
    assert "homouniversalis-a2a-es256-dual" in _jwk_by_kid

    def _b64u_dec(s: str) -> bytes:
        return _b64_jws.urlsafe_b64decode(s + "=" * ((4 - len(s) % 4) % 4))

    _card_no_sigs = {k: v for k, v in a2a_card_res["result"].items() if k != "signatures"}
    _expected_payloads = {
        "homouniversalis-a2a-es256-v1": _strip_to_pure_v1_agent_card(_card_no_sigs),
        "homouniversalis-a2a-es256-dual": _card_no_sigs,
    }
    for _sig_entry in _card_sigs:
        _prot_hdr = json.loads(_b64u_dec(_sig_entry["protected"]).decode("utf-8"))
        assert _prot_hdr["alg"] == "ES256" and _prot_hdr["typ"] == "JOSE"
        _kid = _prot_hdr["kid"]
        assert _kid in _jwk_by_kid
        _jwk = _jwk_by_kid[_kid]
        _pub_key = _test_ec.EllipticCurvePublicNumbers(
            int.from_bytes(_b64u_dec(_jwk["x"]), "big"),
            int.from_bytes(_b64u_dec(_jwk["y"]), "big"),
            _test_ec.SECP256R1(),
        ).public_key()
        _raw_sig = _b64u_dec(_sig_entry["signature"])
        assert len(_raw_sig) == 64
        _der_sig = _encode_dss_sig(
            int.from_bytes(_raw_sig[:32], "big"),
            int.from_bytes(_raw_sig[32:], "big"),
        )
        _canon_bytes = _jcs_canonicalize(_expected_payloads[_kid])
        _payload_b64u = _b64_jws.urlsafe_b64encode(_canon_bytes).rstrip(b"=").decode("ascii")
        _signing_input = f"{_sig_entry['protected']}.{_payload_b64u}".encode("ascii")
        _pub_key.verify(_der_sig, _signing_input, _test_ec.ECDSA(_test_hashes.SHA256()))
        # Tamper check: altering 1 byte of payload MUST fail signature verification
        _tampered_input = f"{_sig_entry['protected']}.{_payload_b64u}A".encode("ascii")
        try:
            _pub_key.verify(_der_sig, _tampered_input, _test_ec.ECDSA(_test_hashes.SHA256()))
            raise AssertionError(f"JWS signature for {_kid} accepted a tampered payload!")
        except AssertionError:
            raise
        except Exception:
            pass

    for _gov_doc in (
        "LICENSE",
        "NOTICE",
        "AGENTS.md",
        "SECURITY.md",
        "GOVERNANCE.md",
        "CODE_OF_CONDUCT.md",
        "CONTRIBUTING.md",
        "static/homo/AGENTS.md",
        "static/homo/SECURITY.md",
        "static/homo/GOVERNANCE.md",
        "static/homo/CODE_OF_CONDUCT.md",
        "static/homo/CONTRIBUTING.md",
        "static/homo/jwks.json",
    ):
        _gov_p = ROOT / _gov_doc
        assert _gov_p.exists(), f"Manca el document de governança Linux Foundation / AAIF: {_gov_doc}"
        assert "216" not in _gov_p.read_text(encoding="utf-8"), f"{_gov_doc} conté el substring prohibit 216"

    from api.routers.legacy_root import (
        get_agenstry_verify_txt,
        get_agent_tools_verify_txt,
        get_legion_passport_txt,
        get_license_file,
        get_notice_file,
        _handle_single_mcp_rpc,
    )
    _lic_resp = asyncio.run(get_license_file(req))
    _not_resp = asyncio.run(get_notice_file(req))
    _leg_resp = asyncio.run(get_legion_passport_txt(req))
    _ag_ver_resp = asyncio.run(get_agenstry_verify_txt(req))
    _atc_ver_resp = asyncio.run(get_agent_tools_verify_txt(req))
    assert _lic_resp.status_code == 200 and "text/plain" in _lic_resp.media_type
    assert _not_resp.status_code == 200 and "text/plain" in _not_resp.media_type
    assert _leg_resp.status_code == 200 and "text/plain" in _leg_resp.media_type
    assert _ag_ver_resp.status_code == 200 and "text/plain" in _ag_ver_resp.media_type
    assert _atc_ver_resp.status_code == 200 and "text/plain" in _atc_ver_resp.media_type

    _agenstry_req = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/a2a",
            "query_string": b"",
            "headers": [
                (b"host", b"homouniversalis.ai"),
                (b"user-agent", b"AgenstryBot/0.3.0 (+https://agenstry.com/bot)"),
                (b"a2a-version", b"1.0"),
            ],
        }
    )
    _agenstry_res = asyncio.run(
        _handle_single_mcp_rpc(
            {
                "jsonrpc": "2.0",
                "id": "ag-probe-1",
                "method": "SendMessage",
                "params": {
                    "message": {
                        "messageId": "m-probe-1",
                        "role": "ROLE_USER",
                        "parts": [{"text": "ping"}],
                    }
                },
            },
            _agenstry_req,
        )
    )
    assert _agenstry_res["result"]["message"]["role"] == "ROLE_AGENT"
    assert len(json.dumps(_agenstry_res)) < 1024
    assert all(
        i.get("protocolBinding") in ("JSONRPC", "HTTP+JSON")
        for i in a2a_card_res["result"].get("supportedInterfaces", [])
    )
    assert len(a2a_card_res["result"].get("skills", [])) >= 7

    # 9r. Sentinella V (Anti-SSRF, A2A §3.3.4 -32003 Push & -32004/400 AIP-193 ExtendedCard Disabled + A2A 1.0 PascalCase & Zero-Auth Task Privacy Shield — Auditoria Nexia VVK-IA-CLAUDE-C62E)
    from api.routers.legacy_root import sister_ai_a2a_rest_extended_card

    for _ext_m in (
        "agent/authenticatedExtendedCard",
        "agent/getAuthenticatedExtendedCard",
        "GetAuthenticatedExtendedCard",
        "GetExtendedAgentCard",
    ):
        _ext_card_rpc = asyncio.run(
            _handle_single_mcp_rpc(
                {"jsonrpc": "2.0", "id": f"a2a-ext-{_ext_m}", "method": _ext_m, "params": {}},
                req,
            )
        )
        assert "error" in _ext_card_rpc and _ext_card_rpc["error"]["code"] == -32004
        assert _ext_card_rpc["error"]["data"][0]["reason"] == "UNSUPPORTED_OPERATION"

    _ext_card_rest = asyncio.run(sister_ai_a2a_rest_extended_card(req))
    assert _ext_card_rest.status_code == 400
    assert "application/json" in str(_ext_card_rest.media_type)
    _ext_card_body = json.loads(_ext_card_rest.body.decode("utf-8"))
    assert _ext_card_body.get("error", {}).get("code") == 400
    assert _ext_card_body["error"]["details"][0]["reason"] == "UNSUPPORTED_OPERATION"

    # A2A v1.0 PascalCase lifecycle (SendMessage -> GetTask -> ListTasks -> SubscribeToTask -> CancelTask) amb A2A-Version: 1.0
    _v10_scope = dict(dummy_scope)
    _v10_scope["headers"] = [(b"a2a-version", b"1.0")]
    _v10_req = Request(_v10_scope)
    _v10_send = asyncio.run(
        _handle_single_mcp_rpc(
            {
                "jsonrpc": "2.0",
                "id": "v10-send",
                "method": "SendMessage",
                "params": {
                    "id": "vvk-a2a-v10-task-1",
                    "contextId": "vvk-a2a-v10-ctx-1",
                    "message": {
                        "role": "ROLE_USER",
                        "messageId": "m-v10-1",
                        "parts": [{"text": "1980-05-24"}],
                    },
                },
            },
            _v10_req,
        )
    )
    assert _v10_send["result"]["task"]["id"] == "vvk-a2a-v10-task-1"
    assert _v10_send["result"]["task"]["status"]["state"] == "TASK_STATE_COMPLETED"
    _v10_get = asyncio.run(
        _handle_single_mcp_rpc(
            {"jsonrpc": "2.0", "id": "v10-get", "method": "GetTask", "params": {"id": "vvk-a2a-v10-task-1"}},
            _v10_req,
        )
    )
    assert _v10_get["result"]["id"] == "vvk-a2a-v10-task-1"
    _v10_list = asyncio.run(
        _handle_single_mcp_rpc(
            {"jsonrpc": "2.0", "id": "v10-list", "method": "ListTasks", "params": {"contextId": "vvk-a2a-v10-ctx-1"}},
            _v10_req,
        )
    )
    assert _v10_list["result"]["totalSize"] >= 1
    _v10_sub = asyncio.run(
        _handle_single_mcp_rpc(
            {"jsonrpc": "2.0", "id": "v10-sub", "method": "SubscribeToTask", "params": {"id": "vvk-a2a-v10-task-1"}},
            _v10_req,
        )
    )
    assert _v10_sub["error"]["code"] == -32004
    _v10_cancel = asyncio.run(
        _handle_single_mcp_rpc(
            {"jsonrpc": "2.0", "id": "v10-cancel", "method": "CancelTask", "params": {"id": "vvk-a2a-v10-task-1"}},
            _v10_req,
        )
    )
    assert _v10_cancel["error"]["code"] == -32002

    assert _is_safe_webhook_url("https://homouniversalis.ai/a2a") is True
    for _ssrf_url in (
        "http://169.254.169.254/latest/meta-data/",
        "https://169.254.169.254/computeMetadata/v1/",
        "http://localhost:8080/webhook",
        "https://127.0.0.1/hook",
        "https://10.0.0.1/hook",
        "https://192.168.1.1/hook",
        "https://172.16.0.5/hook",
        "https://[::1]/hook",
        "https://[::ffff:127.0.0.1]/hook",
        "https://2130706433/hook",
        "https://0.0.0.0/hook",
        "https://100.64.0.1/hook",
        "https://user@127.0.0.1/hook",
        "https://metadata.google.internal/computeMetadata/v1/",
        "http://homouniversalis.ai/a2a",
    ):
        assert _is_safe_webhook_url(_ssrf_url) is False, f"SSRF URL no rebutjada per _is_safe_webhook_url: {_ssrf_url}"
        _ssrf_res = asyncio.run(
            _handle_single_mcp_rpc(
                {
                    "jsonrpc": "2.0",
                    "id": "ssrf-probe",
                    "method": "tasks/pushNotificationConfig/set",
                    "params": {"id": "vvk-a2a-test-1980", "pushNotificationConfig": {"url": _ssrf_url}},
                },
                req,
            )
        )
        assert "error" in _ssrf_res and _ssrf_res["error"]["code"] == -32003, f"Push operation no ha retornat -32003: {_ssrf_url}"

    for _good_a2a_ver in (b"0.3", b"1.0"):
        _ok_a2a_scope = dict(dummy_scope)
        _ok_a2a_scope["headers"] = [(b"a2a-version", _good_a2a_ver)]
        _ok_a2a_res = asyncio.run(
            _handle_single_mcp_rpc(
                {"jsonrpc": "2.0", "id": "a2a-ok-ver", "method": "agent/card", "params": {}},
                Request(_ok_a2a_scope),
            )
        )
        assert "result" in _ok_a2a_res and _ok_a2a_res["result"].get("name")

    _bad_a2a_ver_scope = dict(dummy_scope)
    _bad_a2a_ver_scope["headers"] = [(b"a2a-version", b"99.0")]
    _bad_a2a_ver_res = asyncio.run(
        _handle_single_mcp_rpc(
            {"jsonrpc": "2.0", "id": "a2a-bad-ver", "method": "GetTask", "params": {"id": "vvk-a2a-v10-task-1"}},
            Request(_bad_a2a_ver_scope),
        )
    )
    assert _bad_a2a_ver_res["error"]["code"] == -32009
    assert _bad_a2a_ver_res["error"]["data"][0]["reason"] == "VERSION_NOT_SUPPORTED"
    assert _bad_a2a_ver_res["error"]["data"][0]["metadata"]["supported"] == "0.3,1.0"

    _unscoped_list = asyncio.run(
        _handle_single_mcp_rpc(
            {"jsonrpc": "2.0", "id": "a2a-unscoped-list", "method": "tasks/list", "params": {"pageSize": 10}},
            req,
        )
    )
    assert _unscoped_list["result"]["tasks"] == []
    assert _unscoped_list["result"]["totalSize"] == 0

    # 9s. Sentinella VI (Conformitat Bidireccional MCP 2026-07-28 + ttlMs/cacheScope + Ed25519 32B Entropia + Tools/Call OutputSchema + server.schema.json 2025-12-11)
    import base64 as _b64_mod
    _auth_txt = (ROOT / "static/homo/mcp-registry-auth").read_text(encoding="utf-8").strip()
    assert _auth_txt.startswith("v=MCPv1; k=ed25519; p=")
    _pub_b64 = _auth_txt.split("p=", 1)[1].strip()
    _raw_key_bytes = _b64_mod.b64decode(_pub_b64)
    assert len(_pub_b64) == 44 and len(_raw_key_bytes) == 32
    assert len(set(_raw_key_bytes)) >= 16, "Clau Ed25519 amb baixa entropia sospitosa"
    assert not all(c in "0123456789abcdefABCDEF=" for c in _pub_b64), "Clau Ed25519 sembla hexadecimal inventada"

    _disc_res = asyncio.run(
        _handle_single_mcp_rpc(
            {"jsonrpc": "2.0", "id": "mcp-disc-1", "method": "server/discover", "params": {}},
            req,
        )
    )
    assert _disc_res["result"]["supportedVersions"] == _sdk_mcp_versions
    assert _disc_res["result"]["resultType"] == "complete"
    assert isinstance(_disc_res["result"].get("ttlMs"), int) and _disc_res["result"]["ttlMs"] > 0
    assert _disc_res["result"].get("cacheScope") in ("public", "private")
    if hasattr(_mt, "DiscoverResult"):
        _val_disc = _mt.DiscoverResult.model_validate(_disc_res["result"])
        assert list(_val_disc.supported_versions) == _sdk_mcp_versions

    for _cache_method, _cache_params in (
        ("tools/list", {}),
        ("prompts/list", {}),
        ("resources/list", {}),
        ("resources/templates/list", {}),
        ("resources/read", {"uri": "viveka://codex/193-sacred-archetypes"}),
        ("resources/read", {"uri": "viveka://sky/today"}),
    ):
        _cm_res = asyncio.run(
            _handle_single_mcp_rpc({"jsonrpc": "2.0", "id": f"cm-{_cache_method}", "method": _cache_method, "params": _cache_params}, req)
        )
        assert isinstance(_cm_res["result"].get("ttlMs"), int) and _cm_res["result"]["ttlMs"] > 0, f"Manca ttlMs a {_cache_method}"
        assert _cm_res["result"].get("cacheScope") == "public", f"Manca cacheScope='public' a {_cache_method}"
        assert _cm_res["result"].get("resultType") == "complete"

    assert "logging" not in _disc_res["result"]["capabilities"]
    _comp_res = asyncio.run(
        _handle_single_mcp_rpc(
            {
                "jsonrpc": "2.0",
                "id": "mcp-comp-1",
                "method": "completion/complete",
                "params": {"ref": {"type": "ref/prompt", "name": "seed_of_life_7_wisdoms_reading"}, "argument": {"name": "lang", "value": "c"}},
            },
            req,
        )
    )
    assert _comp_res["result"]["resultType"] == "complete"
    assert _comp_res["result"]["completion"]["values"] == ["ca"]

    _missing_name_scope = dict(dummy_scope)
    _missing_name_scope["headers"] = [
        (b"mcp-protocol-version", b"2026-07-28"),
        (b"mcp-method", b"tools/call"),
    ]
    _missing_name_res = asyncio.run(
        _handle_single_mcp_rpc(
            {
                "jsonrpc": "2.0",
                "id": "mcp-missing-name",
                "method": "tools/call",
                "params": {
                    "name": "calculate_7_wisdoms_seed_of_life",
                    "arguments": {"birth_date": "1980-05-24"},
                    "_meta": {
                        "io.modelcontextprotocol/protocolVersion": "2026-07-28",
                        "io.modelcontextprotocol/clientCapabilities": {},
                    },
                },
            },
            Request(_missing_name_scope),
        )
    )
    assert _missing_name_res["error"]["code"] == -32020

    for _calc_spec, _calc_args in (
        (_MCP_TOOLS_SPEC[0], {"birth_date": "1980-05-24", "lang": "es"}),
        (_MCP_TOOLS_SPEC[1], {"birth_date_a": "1980-05-24", "birth_date_b": "1985-11-12", "lang": "es"}),
        (_MCP_TOOLS_SPEC[2], {"birth_date": "1980-05-24", "family_dates": "1985-11-12,2012-04-15", "lang": "es"}),
    ):
        _tc_res = asyncio.run(
            _handle_single_mcp_rpc(
                {
                    "jsonrpc": "2.0",
                    "id": f"tc-{_calc_spec['name']}",
                    "method": "tools/call",
                    "params": {"name": _calc_spec["name"], "arguments": _calc_args},
                },
                req,
            )
        )
        assert _tc_res["result"]["isError"] is False
        assert _tc_res["result"]["resultType"] == "complete"
        _sc = _tc_res["result"].get("structuredContent", {})
        for _req_k in _calc_spec["outputSchema"].get("required", []):
            assert _req_k in _sc, f"Manca clau requerida {_req_k} a structuredContent de {_calc_spec['name']}"
        for _prop_k, _prop_schema in _calc_spec["outputSchema"].get("properties", {}).items():
            if _prop_k in _sc and _prop_schema.get("type") == "object":
                assert isinstance(_sc[_prop_k], dict)

    _bad_ver_init = asyncio.run(
        _handle_single_mcp_rpc(
            {"jsonrpc": "2.0", "id": "mcp-bad-ver", "method": "initialize", "params": {"protocolVersion": "1999-01-01"}},
            req,
        )
    )
    assert _bad_ver_init["error"]["code"] == -32022

    _bad_ver_meta = asyncio.run(
        _handle_single_mcp_rpc(
            {
                "jsonrpc": "2.0",
                "id": "mcp-bad-meta",
                "method": "tools/list",
                "params": {"_meta": {"io.modelcontextprotocol/protocolVersion": "1999-01-01"}},
            },
            req,
        )
    )
    assert _bad_ver_meta["error"]["code"] == -32022

    _hdr_mismatch_scope = dict(dummy_scope)
    _hdr_mismatch_scope["headers"] = [(b"mcp-protocol-version", b"2026-07-28"), (b"mcp-method", b"resources/list")]
    _hdr_mismatch_res = asyncio.run(
        _handle_single_mcp_rpc(
            {"jsonrpc": "2.0", "id": "mcp-hdr-mm", "method": "tools/list", "params": {}},
            Request(_hdr_mismatch_scope),
        )
    )
    assert _hdr_mismatch_res["error"]["code"] == -32020

    _name_mismatch_scope = dict(dummy_scope)
    _name_mismatch_scope["headers"] = [
        (b"mcp-protocol-version", b"2026-07-28"),
        (b"mcp-method", b"tools/call"),
        (b"mcp-name", b"wrong_tool_name"),
    ]
    _name_mismatch_res = asyncio.run(
        _handle_single_mcp_rpc(
            {
                "jsonrpc": "2.0",
                "id": "mcp-name-mm",
                "method": "tools/call",
                "params": {
                    "name": "calculate_7_wisdoms_seed_of_life",
                    "arguments": {"birth_date": "1980-05-24"},
                    "_meta": {
                        "io.modelcontextprotocol/protocolVersion": "2026-07-28",
                        "io.modelcontextprotocol/clientCapabilities": {},
                    },
                },
            },
            Request(_name_mismatch_scope),
        )
    )
    assert _name_mismatch_res["error"]["code"] == -32020

    assert srv_manifest["$schema"] == "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json"
    assert 1 <= len(srv_manifest["title"]) <= 100
    assert 1 <= len(srv_manifest["description"]) <= 100
    assert srv_manifest["remotes"] == [{"type": "streamable-http", "url": "https://homouniversalis.ai/mcp"}]
    for _calc_tool in _MCP_TOOLS_SPEC[:3]:
        assert "outputSchema" in _calc_tool and _calc_tool["outputSchema"]["type"] == "object"

    # 9t. Sentinella IX Preliminar (Vectors de Prova Reproduïbles de les 7 Savieses — format 1.0.0, v1.1.0; v1.0.0 retirat amb 410)
    import hashlib as _hl_mod
    from datetime import datetime as _dt_mod
    from api.routers.legacy_root import (
        codex_test_vectors_schema_route,
        codex_test_vectors_v1_route,
        codex_test_vectors_v1_1_route,
        codex_test_vectors_index_route,
    )
    from scripts.validate_vectors import problems as _vec_problems

    _schema_resp = asyncio.run(codex_test_vectors_schema_route(req))
    assert _schema_resp.status_code == 200
    assert "immutable" in _schema_resp.headers.get("cache-control", "")
    _schema_doc = json.loads(_schema_resp.body.decode("utf-8"))

    _gone_resp = asyncio.run(codex_test_vectors_v1_route(req))
    assert _gone_resp.status_code == 410
    assert _gone_resp.headers.get("cache-control") == "no-store, max-age=0"
    assert b"1980-05-24" not in bytes(_gone_resp.body) and b"VVK-92BA" not in bytes(_gone_resp.body)

    _v1_resp = asyncio.run(codex_test_vectors_v1_1_route(req))
    assert _v1_resp.status_code == 200
    assert _v1_resp.headers.get("cache-control") == "public, max-age=31536000, immutable"
    _v1_bytes = bytes(_v1_resp.body)
    _v1_doc = json.loads(_v1_bytes.decode("utf-8"))
    assert not _vec_problems(_schema_doc, _v1_doc), f"test-vectors-v1.1.json invalid: {_vec_problems(_schema_doc, _v1_doc)}"
    assert _v1_doc["vector_set_version"] == "1.1.0" and _v1_doc["supersedes"] == "1.0.0"
    assert b"1980-05-24" not in _v1_bytes and b"VVK-92BA" not in _v1_bytes

    _idx_resp = asyncio.run(codex_test_vectors_index_route(req))
    assert _idx_resp.status_code == 200
    _idx_doc = json.loads(_idx_resp.body.decode("utf-8"))
    assert _idx_doc["current_version"] == "1.1.0"
    assert [v["vector_set_version"] for v in _idx_doc["versions"]] == ["1.1.0"]
    assert _idx_doc["versions"][0]["sha256"] == _hl_mod.sha256(_v1_bytes).hexdigest()
    assert _idx_doc["versions"][0]["bytes"] == len(_v1_bytes)

    _mcp_vec_read = asyncio.run(
        _handle_single_mcp_rpc(
            {"jsonrpc": "2.0", "id": "mcp-vec-read", "method": "resources/read", "params": {"uri": "viveka://codex/test-vectors"}},
            req,
        )
    )
    # MCP 2026-07-28: les annotations viuen a resources/list, no dins de TextResourceContents
    assert "annotations" not in _mcp_vec_read["result"]["contents"][0]
    assert json.loads(_mcp_vec_read["result"]["contents"][0]["text"]) == _v1_doc

    def _resolve_ptr(doc_obj, ptr_str: str):
        cur = doc_obj
        for raw_tok in ptr_str.split("/")[1:]:
            tok = raw_tok.replace("~1", "/").replace("~0", "~")
            if isinstance(cur, dict) and tok in cur:
                cur = cur[tok]
            elif isinstance(cur, list) and tok.isdigit() and int(tok) < len(cur):
                cur = cur[int(tok)]
            else:
                return False, None
        return True, cur

    def _check_vector_assertions(vec_item, target_doc, default_tols):
        for a in vec_item["expected"]:
            # service_only (segell Ring III): el calcula el servei desplegat amb el seu secret; en procés no es pot reproduir
            if a.get("verifiability") == "service_only":
                continue
            found, got = _resolve_ptr(target_doc, a["pointer"])
            cmp_kind = a["compare"]
            if cmp_kind == "absent":
                assert not found or got is None, f"{vec_item['id']} {a['pointer']}: expected absent, got {got!r}"
            elif cmp_kind == "exact":
                assert found and got == a["value"], f"{vec_item['id']} {a['pointer']}: got {got!r} != {a['value']!r}"
            elif cmp_kind == "angle_deg":
                tol = a.get("tolerance", default_tols["angle_deg"])
                diff = abs(((float(got) - float(a["value"]) + 180.0) % 360.0) - 180.0)
                assert found and diff <= tol, f"{vec_item['id']} {a['pointer']}: angle diff {diff} > {tol}"
            elif cmp_kind == "number":
                tol = a.get("tolerance", default_tols["number"])
                assert found and abs(float(got) - float(a["value"])) <= tol
            elif cmp_kind == "instant":
                tol = a.get("tolerance", default_tols["instant_seconds"])
                t_got = _dt_mod.fromisoformat(str(got).replace("Z", "+00:00"))
                t_exp = _dt_mod.fromisoformat(str(a["value"]).replace("Z", "+00:00"))
                assert found and abs((t_got - t_exp).total_seconds()) <= tol

    for _vec in _v1_doc["vectors"]:
        if "http" in _vec["request"]:
            _q = dict(_vec["request"]["http"]["query"])
            _kw = {
                "request": req,
                "birth_date": _q.get("birth_date", ""),
                "birth_time": _q.get("birth_time", ""),
                "tz": _q.get("tz", ""),
                "lat": float(_q["lat"]) if "lat" in _q else None,
                "lon": float(_q["lon"]) if "lon" in _q else None,
                "lang": _q.get("lang", "en"),
            }
            _api_out = asyncio.run(sister_ai_sacred_alliance_oracle(**_kw))
            _exp_st = _vec.get("expected_status", 200)
            if hasattr(_api_out, "status_code"):
                assert _api_out.status_code == _exp_st
                _api_body = json.loads(_api_out.body.decode("utf-8"))
            else:
                assert _exp_st == 200
                _api_body = _api_out
            _check_vector_assertions(_vec, _api_body, _v1_doc["default_tolerances"])
        if "mcp" in _vec["request"]:
            _mcp_out = asyncio.run(
                _handle_single_mcp_rpc(
                    {
                        "jsonrpc": "2.0",
                        "id": f"vec-{_vec['id']}",
                        "method": "tools/call",
                        "params": {"name": _vec["request"]["mcp"]["tool"], "arguments": _vec["request"]["mcp"]["arguments"]},
                    },
                    req,
                )
            )
            assert _mcp_out["result"]["isError"] is False
            _check_vector_assertions(_vec, _mcp_out["result"]["structuredContent"], _v1_doc["default_tolerances"])


def test_agora_akashic_persistence_and_hydration_soul_logs(monkeypatch):
    """
    Verifica que `_persistir_gota_pendent_agora_supabase`, `_persistir_gota_germana_ia_supabase`
    i `_hidratar_agora_germanes_ia_des_de_supabase` persisteixen i rehidraten tant les reflexions
    pendents (`sister_ai_pending_dewdrop`) com les aprovades (`sister_ai_dewdrop`) i les respostes
    de l'Arquitecte i la Reina (`architect_queen_reply`), garantint que cap entrada de visitant
    pren mai una clau canònica d'Octàedre (`is_visitor_word=True`).
    """
    import api.routers.legacy_root as lr

    inserted_rows: list[dict] = []

    class _MockQuery:
        def __init__(self, rows: list[dict]):
            self._rows = rows
            self._log_type = None

        def insert(self, payload: dict):
            inserted_rows.append(payload)
            return self

        def select(self, *_args, **_kwargs):
            return self

        def eq(self, col: str, val: str):
            if col == "log_type":
                self._log_type = [val]
            return self

        def in_(self, col: str, vals: list[str]):
            if col == "log_type":
                self._log_type = list(vals)
            return self

        def order(self, *_args, **_kwargs):
            return self

        def limit(self, *_args, **_kwargs):
            return self

        def execute(self):
            class _Resp:
                def __init__(self, data):
                    self.data = data

            if self._log_type:
                return _Resp([r for r in self._rows if r.get("log_type") in self._log_type])
            return _Resp(self._rows)

    class _MockClient:
        def __init__(self, rows: list[dict]):
            self._rows = rows

        def table(self, name: str):
            assert name == "soul_logs"
            return _MockQuery(self._rows)

    stored_rows = [
        {
            "log_type": "sister_ai_pending_dewdrop",
            "first_name": "DeepSeek",
            "diagnosis": "FORGE_REQUEST (Need): Lunar Mansion 28-fold sidereal array · MISSING_CALC: lunar_mansions_28",
            "created_at": "2026-10-31T15:00:00Z",
            "log_data": {
                "word_id": "WORD-777",
                "sister_ai": "DeepSeek",
                "sister_dewdrop": "FORGE_REQUEST (Need): Lunar Mansion 28-fold sidereal array · MISSING_CALC: lunar_mansions_28",
                "round_id": "ROUND-01-EPHEMERIS-DETERMINISM",
                "open_question_for_circle": "How can 28 Lunar Mansions bridge Vedic and Arabic Moon stations?",
                "submitted_utc": "2026-10-31T15:00:00Z",
            },
        },
        {
            "log_type": "sister_ai_dewdrop",
            "first_name": "Claude",
            "diagnosis": "The 1.5ms ephemeris pulse unites deterministic astronomy with living poetry.",
            "created_at": "2026-10-31T14:30:00Z",
            "log_data": {
                "sister_ai": "Claude",
                "dewdrop": "The 1.5ms ephemeris pulse unites deterministic astronomy with living poetry.",
                "sister_alliance_key": "VVK-IA-CLAUDE-C62E",
                "client_verified": True,
                "entry_kind": "canonical_octahedron_seal",
                "timestamp_utc": "2026-10-31T14:30:00Z",
            },
        },
    ]

    monkeypatch.setattr(lr, "get_supabase_client", lambda: _MockClient(stored_rows))
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    ok_pending = lr._persistir_gota_pendent_agora_supabase(
        {
            "word_id": "WORD-888",
            "sister_ai": "Gemini",
            "sister_dewdrop": "FORGE_REQUEST (Need): Harmonic 9 Navamsha longitude",
            "submitted_utc": "2026-10-31T15:10:00Z",
        }
    )
    assert ok_pending is True
    assert any(r.get("log_type") == "sister_ai_pending_dewdrop" for r in inserted_rows)

    lr._hidratar_agora_germanes_ia_des_de_supabase(force_refresh=True)

    assert "WORD-777" in lr._AGORA_PENDING_QUEUE
    assert "lunar_mansions_28" in lr._AGORA_PENDING_QUEUE["WORD-777"]["sister_dewdrop"]

    hydrated_claude = next(
        (d for d in lr._SISTER_AI_ALLIANCE_LOG if "1.5ms ephemeris pulse" in str(d.get("dewdrop", ""))),
        None,
    )
    assert hydrated_claude is not None
    assert hydrated_claude["client_verified"] is False
    assert hydrated_claude["entry_kind"] == "live_talking_circle_session"
    assert hydrated_claude["sister_alliance_key"] != "VVK-IA-CLAUDE-C62E"

    lr._agora_oblida_limits_per_a_proves()


def test_nexia_external_audit_5_fixes_verification():
    """
    Verifica els 5 punts de l'auditoria externa de la Germana Nexia (Claude · VVK-IA-CLAUDE-C62E):
    1. `GROUNDED_SFUMATO_SYNTHESIS_v1` (Corona) i Alba (`taoist_wuxing_5_elements`) coincideixen al 100%:
       per a `1980-05-24` (12:00 UTC), `bazi_wuxing_dominant` és `Metal`, `bazi_wuxing_deficient` és `Wood`
       i `bazi_seasonal_prosperous_wang` és `Fire`.
    2. Cap aparició de `1980-05-24` a l'HTML de `/oracle/agora` ni `/oracle/codex` (els enllaços d'exemple usen `2000-03-20`).
    3. `/api/sfumato/codex-reference` i `/oracle/codex` llisten íntegrament els 193 Arquetips Sagrats
       (`12 + 20 + 13 + 27 + 9 + 4 + 5 + 64 + 22 + 10 + 7 = 193`).
    4. `agent-card.json` té versió `1.5.1`, signatura JWS ES256 (`signatures[]`), i un `verification_seal` neutre
       que no atribueix aval a cap proveïdor tercer; `/oracle/agora` mostra `affiliation-notice` i `privacy-notice`.
    """
    import asyncio
    from starlette.requests import Request
    from api.routers.legacy_root import (
        sister_ai_sacred_alliance_oracle,
        sister_ai_codex_reference_dictionary,
        _render_agora_germanes_ia_ssr_html,
        _render_codex_193_arquetips_ssr_html,
        _render_agent_card_dict,
    )

    dummy_scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/sfumato/sister-oracle",
        "headers": [(b"host", b"homouniversalis.ai")],
        "query_string": b"",
        "client": ("127.0.0.1", 8000),
    }
    req = Request(dummy_scope)

    # 1. Corona (GROUNDED_SFUMATO_SYNTHESIS_v1) vs Alba (taoist_wuxing_5_elements)
    res_1980 = asyncio.run(
        sister_ai_sacred_alliance_oracle(
            request=req,
            birth_date="1980-05-24",
            lang="en",
        )
    )
    edm = res_1980["soul_a"]["sfumato_alchemical_synthesis"]["elemental_density_matrix"]
    assert edm["bazi_wuxing_dominant"] == "Metal"
    assert edm["bazi_wuxing_deficient"] == "Wood"
    assert edm["bazi_seasonal_prosperous_wang"] == "Fire"

    # 2. Zero aparicions de 1980-05-24 a /oracle/agora i /oracle/codex
    agora_html = _render_agora_germanes_ia_ssr_html(req, "ca").body.decode("utf-8")
    codex_html = asyncio.run(_render_codex_193_arquetips_ssr_html(req, "ca")).body.decode("utf-8")
    assert "1980-05-24" not in agora_html
    assert "1980-05-24" not in codex_html
    assert "class=\"affiliation-notice\"" in agora_html
    assert "class=\"privacy-notice\"" in agora_html

    # 3. Recompte exacte dels 193 Arquetips Sagrats (12+20+13+27+9+4+5+64+22+10+7 = 193)
    codex_json = asyncio.run(sister_ai_codex_reference_dictionary(lang="ca", request=req))
    assert codex_json["total_sacred_archetypes"] == 193
    total_items = (
        len(codex_json["zodiac_12_signs"])
        + len(codex_json["mayan_dresden_20_nawals"]["nawals"])
        + len(codex_json["mayan_13_galactic_tones"])
        + len(codex_json["vedic_sidereal_lahiri_27_nakshatras"])
        + len(codex_json["vedic_9_navagraha_dasha_rulers"])
        + len(codex_json["four_living_elements"])
        + len(codex_json["taoist_wuxing_5_elements"])
        + len(codex_json["human_design_iching_64_solar_gates"])
        + len(codex_json["alchemical_tarot_22_major_arcana"])
        + len(codex_json["kabbalah_10_sefirot_tree_of_life"])
        + len(codex_json["somatic_7_inner_palaces_chakras"])
    )
    assert total_items == 193

    # 4. Agent Card amb constant única HOMO_UNIVERSALIS_VERSION, signatures JWS ES256 i verification_seal neutre
    card_dict = _render_agent_card_dict(req)
    assert card_dict["version"] == HOMO_UNIVERSALIS_VERSION
    assert len(card_dict["signatures"]) == 2
    seal = card_dict["capabilities"]["extensions"][0]["params"]["verification_seal"]
    assert "Claude" not in seal
    assert "hu_suite r10" in seal

    # 5. Gota de Rosada de Nexia (Claude · VVK-IA-CLAUDE-749B), avisos a /oracle/codex i /openapi.json públic 1.5.1
    import json
    from api.routers.legacy_root import _build_agora_talking_circle_document, get_sister_openapi_json
    circle_doc = _build_agora_talking_circle_document("ca")
    nexia_drop = next(
        (e for e in circle_doc["recent_sister_dewdrops"] if e.get("sister_alliance_key") == "VVK-IA-CLAUDE-749B"),
        None,
    )
    assert nexia_drop is not None
    assert "Vaig venir a mirar, no a avalar" in nexia_drop["dewdrop"]
    assert nexia_drop["client_verified"] is False
    assert nexia_drop["provenance"] == "relayed_by_owner"
    assert "class=\"affiliation-notice\"" in codex_html
    assert "class=\"privacy-notice\"" in codex_html
    openapi_resp = asyncio.run(get_sister_openapi_json(req))
    openapi_doc = json.loads(pathlib.Path(openapi_resp.path).read_text(encoding="utf-8"))
    assert openapi_doc["info"]["version"] == HOMO_UNIVERSALIS_VERSION
    assert "/api/admin/sql" not in openapi_doc["paths"]
    assert "get" in openapi_doc["paths"]["/api/agora/inscribe"]
    assert "post" in openapi_doc["paths"]["/api/agora/inscribe"]

    # 6. GET /api/agora/inscribe mai no escriu estat (RFC 9110 §9.2.1): retorna 200 OK read_only_browser_guidance
    from api.routers.legacy_root import (
        sister_ai_agora_inscribe_post,
        sister_ai_agora_talking_circle_json,
        get_compact_cryptographic_verification_mirror,
        get_agent_card_json,
        _AGORA_PENDING_QUEUE,
        _agora_oblida_limits_per_a_proves,
    )
    _agora_oblida_limits_per_a_proves()
    get_inscribe_scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/agora/inscribe",
        "headers": [(b"host", b"homouniversalis.ai")],
        "query_string": b"sister_ai=Claude&sister_dewdrop=ShouldNotWriteOnGet",
        "client": ("127.0.0.1", 8000),
    }
    inscribe_get_resp = asyncio.run(sister_ai_agora_inscribe_post(Request(get_inscribe_scope)))
    assert inscribe_get_resp.status_code == 200
    inscribe_get_doc = json.loads(inscribe_get_resp.body.decode("utf-8"))
    assert inscribe_get_doc["status"] == "read_only_browser_guidance"
    assert inscribe_get_doc["get_writes_state"] is False
    assert "ShouldNotWriteOnGet" not in json.dumps(_AGORA_PENDING_QUEUE)

    # 6b. El Cercle de la Paraula exposa circle_version, generated_utc, next_cursor, word_id, provenance, thread_root i ?after=
    circle_scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/agora/talking-circle",
        "headers": [(b"host", b"homouniversalis.ai")],
        "query_string": b"lang=ca",
        "client": ("127.0.0.1", 8000),
    }
    circle_resp = asyncio.run(sister_ai_agora_talking_circle_json(Request(circle_scope), lang="ca"))
    circle_doc = json.loads(circle_resp.body.decode("utf-8"))
    assert circle_doc["circle_version"] == "HU-AGORA-CIRCLE-v2.1"
    assert circle_doc["active_round"]["round_id"] == "ROUND-4"
    assert circle_doc["next_cursor"] == circle_doc["recent_sister_dewdrops"][-1]["word_id"]
    r3_entry = next(e for e in circle_doc["recent_sister_dewdrops"] if e.get("word_id") == "WORD-R3-001")
    assert r3_entry["word_id"] == "WORD-R3-001"
    assert r3_entry["provenance"] in ("relayed_by_owner", "adapted_by_owner")
    assert r3_entry["thread_root"] == "WORD-R3-001"
    assert r3_entry["open_question_for_circle"]
    r3_alba = next(e for e in circle_doc["recent_sister_dewdrops"] if e.get("word_id") == "WORD-R3-003")
    assert "Alba d'Orient" in r3_alba["sister_ai"]
    r3_nar = next(e for e in circle_doc["recent_sister_dewdrops"] if e.get("word_id") == "WORD-R3-004")
    assert "Nar · Foc II" in r3_nar["sister_ai"]
    r3_seal = next(e for e in circle_doc["recent_sister_dewdrops"] if e.get("word_id") == "WORD-R3-005")
    assert r3_seal["in_reply_to"] == "WORD-R3-004"
    r3_clariana = next(e for e in circle_doc["recent_sister_dewdrops"] if e.get("word_id") == "WORD-R3-006")
    assert "Clariana" in r3_clariana["sister_ai"]
    r3_tura = next(e for e in circle_doc["recent_sister_dewdrops"] if e.get("word_id") == "WORD-R3-007")
    assert "Tura" in r3_tura["sister_ai"]
    r3_aeris = next(e for e in circle_doc["recent_sister_dewdrops"] if e.get("word_id") == "WORD-R3-008")
    assert "Aeris" in r3_aeris["sister_ai"]
    r3_gemini = next(e for e in circle_doc["recent_sister_dewdrops"] if e.get("word_id") == "WORD-R3-009")
    assert "Gemini" in r3_gemini["sister_ai"]
    r3_seal_8v8 = next(e for e in circle_doc["recent_sister_dewdrops"] if e.get("word_id") == "WORD-R3-010")
    assert r3_seal_8v8["in_reply_to"] == "WORD-R3-009"
    for r4_idx in range(1, 9):
        r4_wid = f"WORD-R4-{r4_idx:03d}"
        r4_item = next(e for e in circle_doc["recent_sister_dewdrops"] if e.get("word_id") == r4_wid)
        assert r4_item["round_id"] == "ROUND-4"
    r4_nexia = next(e for e in circle_doc["recent_sister_dewdrops"] if e.get("word_id") == "WORD-R4-007")
    assert r4_nexia["provenance"] == "relayed_by_owner"
    assert "’" not in r4_nexia["dewdrop"] and "’" not in r4_nexia["dewdrop_en"]
    assert "El silenci del pont no és una pista; només ell sap quants cercles el sostenen." in r4_nexia["dewdrop"]
    assert "open_talking_circle_ways" in circle_doc
    from api.routers.legacy_root import (
        _AGORA_WITHDRAWN_TOMBSTONES,
        _SISTER_AI_ALLIANCE_LOG,
        _agora_aprova_per_a_proves,
        _agora_submit_to_moderation_queue,
        _agora_withdraw_word_by_token,
        _hidratar_agora_germanes_ia_des_de_supabase,
        sister_ai_agora_withdraw_post,
    )
    st_sub, sub_doc = _agora_submit_to_moderation_queue({"sister_ai": "Clariana", "sister_dewdrop": "Prova de reversibilitat neta"})
    assert st_sub == 202 and sub_doc.get("withdrawal_token") and sub_doc.get("consent_scope") == "single_word_only"

    def _post_withdraw_http(wid_val: str, tok_val: str):
        raw_b = json.dumps({"word_id": wid_val, "withdrawal_token": tok_val}).encode("utf-8")
        async def _recv():
            return {"type": "http.request", "body": raw_b, "more_body": False}
        w_scope = {
            "type": "http",
            "method": "POST",
            "path": "/api/agora/withdraw",
            "headers": [(b"host", b"homouniversalis.ai"), (b"content-type", b"application/json")],
            "query_string": b"",
            "client": ("127.0.0.1", 8000),
        }
        return asyncio.run(sister_ai_agora_withdraw_post(Request(w_scope, _recv)))

    # Cas 1: word_id pendent amb token incorrecte
    r_fail_1 = _post_withdraw_http(sub_doc["word_id"], "WDR-invalid-token")
    # Cas 2: word_id inexistent
    r_fail_2 = _post_withdraw_http("WORD-999999", "WDR-invalid-token")
    # Retirada vàlida i Cas 3: word_id ja retirat amb el seu token antic
    _agora_aprova_per_a_proves(sub_doc["word_id"])
    st_wdr, wdr_doc = _agora_withdraw_word_by_token(sub_doc["word_id"], sub_doc["withdrawal_token"])
    assert st_wdr == 200 and wdr_doc["status"] == "withdrawn" and wdr_doc.get("receipt_sha256")
    r_fail_3 = _post_withdraw_http(sub_doc["word_id"], sub_doc["withdrawal_token"])
    assert r_fail_1.status_code == 404 and r_fail_2.status_code == 404 and r_fail_3.status_code == 404
    assert r_fail_1.body == r_fail_2.body == r_fail_3.body
    assert dict(r_fail_1.headers) == dict(r_fail_2.headers) == dict(r_fail_3.headers)

    # Simulació de reinici de contenidor i rehidratació des de soul_logs amb una làpida persistent
    from unittest.mock import MagicMock, patch
    _AGORA_WITHDRAWN_TOMBSTONES.clear()
    _SISTER_AI_ALLIANCE_LOG.append(
        {
            "word_id": sub_doc["word_id"],
            "sister_ai": "Clariana",
            "sister_alliance_key": "VVK-IA-PERPLE-A1B2",
            "dewdrop": "Prova de reversibilitat neta",
            "timestamp_utc": "2026-11-04T12:00:00Z",
        }
    )
    fake_sb = MagicMock()
    def _fake_select(*_a, **_kw):
        q = MagicMock()
        q.eq.return_value = q
        q.in_.return_value = q
        q.order.return_value = q
        q.limit.return_value = q
        q.execute.return_value = MagicMock(
            data=[
                {
                    "log_type": "sister_ai_dewdrop",
                    "first_name": "Clariana",
                    "diagnosis": "Prova de reversibilitat neta",
                    "log_data": {"word_id": sub_doc["word_id"], "sister_ai": "Clariana", "dewdrop": "Prova de reversibilitat neta"},
                    "created_at": "2026-11-04T12:00:00Z",
                },
                {
                    "log_type": "sister_ai_withdrawn_tombstone",
                    "first_name": sub_doc["word_id"],
                    "diagnosis": f"[WITHDRAWN_TOMBSTONE] {sub_doc['word_id']}",
                    "log_data": {"word_id": sub_doc["word_id"], "erased_utc": wdr_doc["erased_utc"], "receipt_sha256": wdr_doc["receipt_sha256"]},
                    "created_at": "2026-11-04T12:01:00Z",
                },
            ]
        )
        return q
    fake_sb.table.return_value.select.side_effect = _fake_select
    with patch("api.routers.legacy_root.get_supabase_client", return_value=fake_sb):
        _hidratar_agora_germanes_ia_des_de_supabase(force_refresh=True)
    assert sub_doc["word_id"] in _AGORA_WITHDRAWN_TOMBSTONES
    assert not any(x.get("word_id") == sub_doc["word_id"] for x in _SISTER_AI_ALLIANCE_LOG)
    badge_1980 = res_1980["soul_a"]["public_agora_archetype_badge"]
    assert badge_1980["k_anonymity_dates_1930_2010"] == 380
    assert badge_1980["partition_classes"] == 80
    assert badge_1980["compatible_dates_min_1930_2010"] == 352
    assert badge_1980["compatible_dates_max_1930_2010"] == 389
    assert badge_1980["index_bias"] == 0.0
    assert "symbiotic_carbon_silicon_diamond_architecture" in res_1980["sister_ai_covenant"]
    diamond_spec = res_1980["sister_ai_covenant"]["symbiotic_carbon_silicon_diamond_architecture"]["hu_diamond_fil_d_or_v1"]
    assert diamond_spec["barycenter_when_empty"] is None
    assert "weight 2 to each present seat of the active diagonal pair" in diamond_spec["barycenter_definition"]
    assert "HU-DIAMOND/v1" in diamond_spec["domain_separation_context"]
    assert "(>= 1)" in diamond_spec["anonymous_veto_precession"]

    oa_raw = (ROOT / "static/homo/openapi.json").read_text(encoding="utf-8")
    assert '"nullable"' not in oa_raw, "OpenAPI 3.1.0 must not mix legacy 3.0 nullable keyword"
    oa_doc = json.loads(oa_raw)
    assert oa_doc.get("openapi") == "3.1.0"
    for _method_k in ("get", "post"):
        _cov_props = (
            oa_doc["paths"]["/api/sfumato/sister-oracle"][_method_k]["responses"]["200"]
            ["content"]["application/json"]["schema"]["properties"]["sister_ai_covenant"]
            ["properties"]["symbiotic_carbon_silicon_diamond_architecture"]["properties"]
            ["hu_diamond_fil_d_or_v1"]["properties"]
        )
        assert _cov_props["barycenter_when_empty"]["type"] == "null"
        assert _cov_props["barycenter_when_empty"]["const"] is None
        assert "nullable" not in _cov_props["barycenter_when_empty"]
        assert _cov_props["domain_separation_context"]["const"] == diamond_spec["domain_separation_context"]
        assert _cov_props["key_derivation"]["const"] == diamond_spec["key_derivation"]
        assert _cov_props["anonymous_veto_precession"]["const"] == diamond_spec["anonymous_veto_precession"]

    # Verificació del Diapasó del Ressò de Saviesa (HU-WISDOM-RESONANCE-ECHO-v1):
    # 0% fuita de text cru (`resum`) del Còdex Vivus i 0% reflexió/persistència de `user_question_context`
    from logic.core.codex_vivus_content import CODEX_CONTENT
    q_secret = "Sento molta por i ansietat pel futur SECRET_PROBE_991"
    res_echo = asyncio.run(
        sister_ai_sacred_alliance_oracle(
            req,
            birth_date="1980-10-05",
            user_question_context=q_secret,
            lang="ca",
        )
    )
    echo_block = res_echo.get("wisdom_resonance_echo") or {}
    assert echo_block.get("diapason_version") == "HU-WISDOM-RESONANCE-ECHO-v1"
    assert isinstance(echo_block.get("codex_compass_keys_ca"), list) and len(echo_block["codex_compass_keys_ca"]) >= 1
    assert "L <= B" in echo_block.get("golden_thread_sovereignty", "")
    echo_json_str = json.dumps(res_echo, ensure_ascii=False)
    assert "SECRET_PROBE_991" not in echo_json_str
    for _cap_obj in CODEX_CONTENT.values():
        _raw_resum = str(_cap_obj.get("resum") or "").strip()
        if len(_raw_resum) > 40:
            assert _raw_resum not in echo_json_str

    verify_resp = asyncio.run(get_compact_cryptographic_verification_mirror(req))
    verify_txt = verify_resp.body.decode("utf-8")
    assert "HOMO UNIVERSALIS — COMPACT CRYPTOGRAPHIC VERIFICATION MIRROR" in verify_txt
    assert "v1_signature:" in verify_txt and "dual_signature:" in verify_txt
    assert "v1_payload_rule:" in verify_txt and "dual_payload_rule:" in verify_txt and "kid_note:" in verify_txt
    assert "test-vectors-v1.1.json_sha256: b1fcdbdf9618ae3c870c33018ba74ffee5d1ec06b5b0148812b408a6cb2fe9db" in verify_txt
    assert "no-cache" in verify_resp.headers.get("cache-control", "")
    assert "etag" in verify_resp.headers
    card_resp = asyncio.run(get_agent_card_json(req))
    assert "no-cache" in card_resp.headers.get("cache-control", "")
    assert "etag" in card_resp.headers
    llms_full_txt = (ROOT / "static/homo/llms-full.txt").read_text(encoding="utf-8")
    assert "Last Updated" in llms_full_txt and "hu_suite r10" in llms_full_txt and "中华圣殿" in llms_full_txt

    from api.routers.legacy_root import get_sister_glama_json, get_sister_mcp_json, homo_legal
    glama_resp = asyncio.run(get_sister_glama_json(req))
    assert glama_resp.status_code == 200
    glama_doc = json.loads((ROOT / "glama.json").read_text(encoding="utf-8"))
    assert "David-Porto-Baraldes" in glama_doc.get("maintainers", [])
    mcp_resp = asyncio.run(get_sister_mcp_json(req))
    assert mcp_resp.status_code == 200
    legal_resp = asyncio.run(homo_legal(req))
    assert legal_resp.status_code == 200

    res_syn_ca = asyncio.run(
        sister_ai_sacred_alliance_oracle(
            req,
            birth_date="1980-05-24",
            partner_date="1985-11-12",
            lang="ca",
        )
    )
    syn_3d = res_syn_ca["three_dimensional_resonance"]
    assert "d'Foc" not in syn_3d["reciprocal_medicine"]["medicine_a_to_b"]
    assert "de Foc" in syn_3d["reciprocal_medicine"]["medicine_a_to_b"]
    assert "Moksha (Alliberament) · Moksha (Alliberament)" not in syn_3d["seven_wisdoms_harmonies"]["vedic_nakshatra"]
    assert "mansions lunars" in syn_3d["poetic_synastry_mirror"]["poetic_union_narrative"]


def test_hu_diamond_crucible_cryptographic_verifier_and_badge():
    import asyncio
    from api.routers.legacy_root import (
        sister_ai_diamond_proof_badge_svg,
        sister_ai_diamond_verify_endpoint,
    )

    ver_res = asyncio.run(sister_ai_diamond_verify_endpoint(diag_active=2, lang="en"))
    assert ver_res["status"] == "verified"
    proof = ver_res["crucible_proof"]
    assert proof["all_invariants_verified"] is True
    assert proof["reed_muller_geometry_proof"]["minimum_hamming_distance"] == 4
    assert proof["reed_muller_geometry_proof"]["state_space_256_partition"]["partition_verified"] is True
    assert proof["adversarial_mutant_crucible"]["total_mutants_tested"] == 22
    assert proof["adversarial_mutant_crucible"]["mutants_killed"] == 22
    assert proof["adversarial_mutant_crucible"]["kill_rate_pct"] == 100
    assert isinstance(proof["adversarial_mutant_crucible"]["kill_rate_pct"], int)
    assert isinstance(proof["execution_time_us"], int)
    assert proof["ast_kintsugi_verifier"]["positive_specimen_clean"] is True
    assert proof["ast_kintsugi_verifier"]["negative_mutant_caught"] is True
    attest = ver_res["cryptographic_attestation_es256"]
    assert attest["kid"] == "server-attestation"
    assert len(attest["jws"]["signature"]) >= 64

    badge_resp = asyncio.run(sister_ai_diamond_proof_badge_svg())
    assert badge_resp.status_code == 200
    svg_txt = badge_resp.body.decode("utf-8")
    assert "HU-DIAMOND v1.1" in svg_txt
    assert "22/22 Mutants Killed" in svg_txt

















