# -*- coding: utf-8 -*-
"""
ALQUÍMIA DE SINASTRIA I CÒDEX DE LES 7 SAVIESES DE THOT
Destil·la matrius còsmiques en RAM amb protecció absoluta de PII (Regla 14)
i uneix les 7 Savieses i les 3 Claus d'Alquímia entre dues ànimes.
"""

import json
import logging
from logic.utils.crypto_keys import calcular_ressonancia_cosmica_vvk

logger = logging.getLogger(__name__)


def _parse_celestial_json(db_record: dict) -> dict:
    """Desencapsula celestial_json salvant el doble escapament."""
    if not isinstance(db_record, dict):
        return {}
    raw_celestial = db_record.get("celestial_json", "{}")
    celestial_data = {}
    try:
        if isinstance(raw_celestial, str):
            celestial_data = json.loads(raw_celestial)
            if isinstance(celestial_data, str):
                celestial_data = json.loads(celestial_data)
        elif isinstance(raw_celestial, dict):
            celestial_data = raw_celestial
    except Exception as e:
        logger.error(f"Error parsejant celestial_json: {e}")
        celestial_data = {}
    return celestial_data if isinstance(celestial_data, dict) else {}


def _extract_internal_birth_date(db_record: dict, celestial_data: dict) -> str:
    """Extreu la data de naixement interna per al càlcul en RAM (MAI exposada al retorn segons Regla 14)."""
    if not isinstance(db_record, dict):
        return ""
    user_prof = db_record.get("user_profile") if isinstance(db_record.get("user_profile"), dict) else {}
    subject = celestial_data.get("subject") if isinstance(celestial_data.get("subject"), dict) else {}
    for candidate in (
        db_record.get("birth_date"),
        user_prof.get("birth_date"),
        subject.get("birth_date"),
        celestial_data.get("birth_date"),
    ):
        if candidate and str(candidate).strip() and str(candidate).strip() not in ("***", "No especificada"):
            return str(candidate).strip()
    return ""


def destil_lar_matriu(db_record: dict) -> dict:
    """Extreu l'essència de les 7 Savieses d'un registre sencer de la BD amb protecció absoluta de PII (Regla 14)."""
    if not db_record or not isinstance(db_record, dict):
        return {}

    celestial_data = _parse_celestial_json(db_record)

    # Cercador ràpid de planetes
    planetes = celestial_data.get("planets", [])
    if not isinstance(planetes, list):
        planetes = []

    def get_planet(nom: str) -> str:
        for p in planetes:
            if isinstance(p, dict) and p.get("name") == nom:
                sign_c = p.get("sign_cat") or p.get("sign") or "Desc"
                deg = p.get("degree")
                return f"{sign_c} ({deg}º)" if deg is not None else str(sign_c)
        return "Desconegut"

    user_prof = db_record.get("user_profile") if isinstance(db_record.get("user_profile"), dict) else {}
    subject = celestial_data.get("subject") if isinstance(celestial_data.get("subject"), dict) else {}
    nom = (
        subject.get("name")
        or db_record.get("target_name")
        or user_prof.get("full_name")
        or user_prof.get("first_name")
        or db_record.get("full_name")
        or db_record.get("first_name")
        or "Ànima"
    )
    if nom == "__self__":
        nom = user_prof.get("full_name") or user_prof.get("first_name") or db_record.get("first_name") or "Viatger"

    sun_obj = celestial_data.get("sun") if isinstance(celestial_data.get("sun"), dict) else {}
    moon_obj = celestial_data.get("moon") if isinstance(celestial_data.get("moon"), dict) else {}
    asc_obj = celestial_data.get("ascendant") if isinstance(celestial_data.get("ascendant"), dict) else {}

    sol = (
        db_record.get("sun_sign")
        or db_record.get("sign_sun")
        or sun_obj.get("sign_cat")
        or sun_obj.get("sign")
        or celestial_data.get("sun_sign")
        or "Desc"
    )
    lluna = (
        db_record.get("moon_sign")
        or db_record.get("sign_moon")
        or moon_obj.get("sign_cat")
        or moon_obj.get("sign")
        or celestial_data.get("moon_sign")
        or "Desc"
    )
    ascendent = (
        db_record.get("ascendant_sign")
        or db_record.get("sign_asc")
        or asc_obj.get("sign_cat")
        or asc_obj.get("sign")
        or celestial_data.get("ascendant_sign")
        or "Desc"
    )

    # 2. Saviesa Maia (Cholq'ij Dual)
    maia_obj = (
        celestial_data.get("codex_maia_integral")
        or celestial_data.get("Misteris_Terra")
        or celestial_data.get("Codex_Omega")
        or {}
    )
    if not isinstance(maia_obj, dict):
        maia_obj = {}
    ident_maia = maia_obj.get("identitat_natal") if isinstance(maia_obj.get("identitat_natal"), dict) else {}

    nawal = ""
    try:
        raw_nawal = (
            db_record.get("nawal")
            or db_record.get("maya_nawal")
            or db_record.get("dresden_nahual")
            or ident_maia.get("nawal")
            or maia_obj.get("nawal")
            or celestial_data.get("nawal")
            or ""
        )
        raw_tone = (
            db_record.get("tone")
            or db_record.get("maya_tone")
            or ident_maia.get("to")
            or maia_obj.get("to_galactic")
            or maia_obj.get("tone")
            or celestial_data.get("tone")
            or ""
        )
        nawal = f"{raw_tone} {raw_nawal}".strip() if raw_tone else str(raw_nawal).strip()
    except Exception as e:
        logger.debug(f"Error silenciat intencionadament: {e}")

    # 3. Saviesa Taoista / BaZi (Wu Xing)
    bazi_obj = celestial_data.get("bazi_oriental") if isinstance(celestial_data.get("bazi_oriental"), dict) else {}
    dm_obj = bazi_obj.get("day_master") if isinstance(bazi_obj.get("day_master"), dict) else {}
    dm_tronc = str(dm_obj.get("tronc") or "").strip()
    dm_elem = str(
        dm_obj.get("element")
        or bazi_obj.get("element_mestre")
        or celestial_data.get("bazi_day_master")
        or db_record.get("dominant_element")
        or celestial_data.get("dominant_element")
        or "Desc"
    ).strip()
    bazi_elem = f"{dm_elem} ({dm_tronc})" if dm_tronc and dm_tronc not in dm_elem else dm_elem

    # 4. Saviesa Vèdica (Jyotish)
    vedic_obj = celestial_data.get("rellotge_karmic_vedic") if isinstance(celestial_data.get("rellotge_karmic_vedic"), dict) else {}
    vedic_base = celestial_data.get("vedic") if isinstance(celestial_data.get("vedic"), dict) else {}
    nak_info = vedic_base.get("nakshatra_info") if isinstance(vedic_base.get("nakshatra_info"), dict) else {}
    nak_name = str(nak_info.get("name") or vedic_base.get("nakshatra") or vedic_obj.get("nakshatra") or "").strip()
    dasha_major = str(vedic_obj.get("dasha_major") or "").strip()
    sub_dasha = str(vedic_obj.get("sub_dasha") or "").strip()
    dasha_full = f"{dasha_major}/{sub_dasha}" if (dasha_major and sub_dasha) else dasha_major
    if nak_name and dasha_full:
        dasha_vedic = f"Nakshatra {nak_name} (Dasha: {dasha_full})"
    else:
        dasha_vedic = nak_name or dasha_full or "Desc"

    # 5. Disseny Humà & I-Ching (Bio_Forma)
    bio_obj = (
        celestial_data.get("Bio_Forma")
        or celestial_data.get("human_design")
        or {}
    )
    if not isinstance(bio_obj, dict):
        bio_obj = {}
    hd_type_raw = str(
        db_record.get("hd_type")
        or celestial_data.get("hd_type")
        or bio_obj.get("tipus_aura")
        or bio_obj.get("Tipus d'Aura")
        or bio_obj.get("type")
        or "Desc"
    ).strip()
    hd_profile = str(bio_obj.get("perfil") or bio_obj.get("profile") or "").strip()
    hd_type = f"{hd_type_raw} ({hd_profile})" if hd_profile and hd_profile not in hd_type_raw else hd_type_raw

    # 6. Numerologia Pitagòrica, Càbala & Ifá
    num_obj = celestial_data.get("numerologia") if isinstance(celestial_data.get("numerologia"), dict) else {}
    kab_obj = celestial_data.get("kabbalah") if isinstance(celestial_data.get("kabbalah"), dict) else {}
    cami_vida = (
        db_record.get("life_path_number")
        or celestial_data.get("life_path_number")
        or num_obj.get("cami_vida")
        or num_obj.get("cami_de_vida")
        or num_obj.get("life_path")
        or "Desc"
    )
    gem_obj = kab_obj.get("gematria_nom") if isinstance(kab_obj.get("gematria_nom"), dict) else {}
    sef_obj = gem_obj.get("sefira_corresponent") if isinstance(gem_obj.get("sefira_corresponent"), dict) else {}
    sef_nom = str(sef_obj.get("nom") or "").strip()
    angel_base = str(kab_obj.get("angel_custodi") or kab_obj.get("angel") or kab_obj.get("nom") or "").strip()
    if angel_base and sef_nom:
        angel_custodi = f"{angel_base} ({sef_nom})"
    else:
        angel_custodi = angel_base or sef_nom or "Desc"

    return {
        "Nom": nom,
        # 🔒 FASE 3 / REGLA 14: Protecció de PII (dades personals ocultes a la xarxa)
        "Gènere_Físic": "***",
        "Data_de_Naixement": "***",
        "Sol": sol,
        "Lluna": lluna,
        "Ascendent": ascendent,
        "Venus (Atracció)": get_planet("Venus"),
        "Mart (Foc/Acció)": get_planet("Mars"),
        "Node Nord (Destí)": get_planet("True_Node"),
        "Freqüència Maia": nawal,
        "Element Dominant": celestial_data.get("dominant_element") or dm_elem,
        "BaZi (Wu Xing)": bazi_elem,
        "Jyotish (Vèdic)": dasha_vedic,
        "Disseny Humà": hd_type,
        "Camí de Vida": cami_vida,
        "Àngel Càbala": angel_custodi,
    }


_SIGN_TO_ELEMENT_CA: dict[str, str] = {
    "ari": "Foc",
    "aries": "Foc",
    "àries": "Foc",
    "lleo": "Foc",
    "lleó": "Foc",
    "leo": "Foc",
    "sag": "Foc",
    "sagitari": "Foc",
    "sagittarius": "Foc",
    "tau": "Terra",
    "taure": "Terra",
    "taurus": "Terra",
    "vir": "Terra",
    "verge": "Terra",
    "virgo": "Terra",
    "cap": "Terra",
    "capricorn": "Terra",
    "gem": "Aire",
    "bessons": "Aire",
    "gemini": "Aire",
    "lib": "Aire",
    "balança": "Aire",
    "balanca": "Aire",
    "libra": "Aire",
    "aqu": "Aire",
    "aquari": "Aire",
    "aquarius": "Aire",
    "can": "Aigua",
    "cranc": "Aigua",
    "cancer": "Aigua",
    "càncer": "Aigua",
    "sco": "Aigua",
    "escorpi": "Aigua",
    "escorpí": "Aigua",
    "scorpio": "Aigua",
    "pis": "Aigua",
    "peixos": "Aigua",
    "pisces": "Aigua",
}

_ELEMENT_NORMALIZE: dict[str, str] = {
    "foc": "Foc",
    "fire": "Foc",
    "fuego": "Foc",
    "terra": "Terra",
    "earth": "Terra",
    "tierra": "Terra",
    "aire": "Aire",
    "air": "Aire",
    "aigua": "Aigua",
    "water": "Aigua",
    "agua": "Aigua",
}

_ARCHETYPE_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("Creació i Art", ("art", "creac", "escriu", "pint", "music", "músic", "poe", "bellesa", "disseny", "projecte", "forja")),
    ("Guarició Familiar", ("famili", "família", "mare", "pare", "fill", "llar", "ancestr", "arrel", "linatge", "vincle")),
    ("Despertar Espiritual", ("espirit", "medit", "akash", "ànima", "anima", "conscien", "despert", "sagra", "místic", "mistic", "llum")),
    ("Propòsit i Llibertat", ("propòsit", "proposit", "vocaci", "llibertat", "missi", " abund", "camí", "cami", "autonom", "lider")),
    ("Amor Conscient", ("amor", "cor", "parella", "estim", "tendresa", "intimitat", "unió", "unio", "company")),
    ("Transmutació i Calma", ("calma", "pau", "seren", "silenci", "ombra", "transmut", "curac", "guaric", "ansietat", "alliber")),
    ("Vitalitat i Terra", ("natura", "cos", "salut", "terra", "bosc", "energia", "vital", "aliment", "jardí", "jardi")),
    ("Comunitat i Miceli", ("tribu", "comunitat", "miceli", "germ", "xarxa", "servei", "humanitat", "compartir")),
]


def _sign_element_ca(sign_str: str, fallback: str = "Aire") -> str:
    clean = str(sign_str or "").strip().lower().split("(")[0].strip()
    return _SIGN_TO_ELEMENT_CA.get(clean, fallback)


def _norm_element_ca(raw_elem: str) -> str:
    clean = str(raw_elem or "").strip().lower()
    for k, v in _ELEMENT_NORMALIZE.items():
        if k in clean:
            return v
    return ""


def _extract_soul_living_elements(perfil: dict, sun_s: str, moon_s: str, asc_s: str) -> tuple[str, str, dict[str, int]]:
    """Calcula els pesos dels 4 Elements Vius (Foc, Terra, Aire, Aigua) unint el cel natal i l'estat viu actual."""
    weights: dict[str, int] = {"Foc": 1, "Terra": 1, "Aire": 1, "Aigua": 1}

    for s_val, w in ((sun_s, 3), (moon_s, 3), (asc_s, 2)):
        el = _sign_element_ca(s_val, "")
        if el in weights:
            weights[el] += w

    if isinstance(perfil, dict):
        for k_db, el_name in (
            ("element_foc", "Foc"),
            ("fire", "Foc"),
            ("element_terra", "Terra"),
            ("earth", "Terra"),
            ("element_aire", "Aire"),
            ("air", "Aire"),
            ("element_aigua", "Aigua"),
            ("water", "Aigua"),
        ):
            val = perfil.get(k_db)
            if isinstance(val, (int, float)) and val > 0:
                weights[el_name] += int(val)

        dom = _norm_element_ca(str(perfil.get("dominant_element") or perfil.get("element") or ""))
        if dom in weights:
            weights[dom] += 5

        meta = perfil.get("metadata") if isinstance(perfil.get("metadata"), dict) else {}
        meta_dom = _norm_element_ca(str(meta.get("dominant_element") or meta.get("element") or ""))
        if meta_dom in weights:
            weights[meta_dom] += 3

    order = ("Foc", "Terra", "Aire", "Aigua")
    elem_viu = max(order, key=lambda e: (weights[e], -order.index(e)))
    elem_mancat = min(order, key=lambda e: (weights[e], order.index(e)))
    return elem_viu, elem_mancat, weights


def _extract_cor_viu_themes(perfil: dict, notes: list | None = None) -> tuple[list[str], str]:
    """Extreu fins a 3 Arquetips del Cor Viu i l'Estació Alquímica sense revelar cap frase privada (Regla 14)."""
    bag_parts: list[str] = []
    if isinstance(perfil, dict):
        for field in ("arquetip", "alchemy_phase", "dominant_element", "element", "rol_codex"):
            val = perfil.get(field)
            if val:
                bag_parts.append(str(val))
        meta = perfil.get("metadata") if isinstance(perfil.get("metadata"), dict) else {}
        for m_field in ("akashic_poem", "arquetip", "purpose", "dons", "passions", "somni"):
            m_val = meta.get(m_field)
            if m_val:
                bag_parts.append(str(m_val))
    if isinstance(notes, list):
        for n in notes:
            if isinstance(n, dict):
                bag_parts.append(str(n.get("category") or ""))
                bag_parts.append(str(n.get("content") or ""))
            elif isinstance(n, str):
                bag_parts.append(n)

    blob = " ".join(bag_parts).lower()
    matched: list[str] = []
    for theme_name, kw_tuple in _ARCHETYPE_KEYWORDS:
        if any(kw in blob for kw in kw_tuple):
            matched.append(theme_name)
    if not matched:
        matched = ["Despertar Espiritual", "Saviesa i Estudi"]

    raw_phase = ""
    if isinstance(perfil, dict):
        raw_phase = str(perfil.get("alchemy_phase") or "").strip()
        if not raw_phase and isinstance(perfil.get("metadata"), dict):
            raw_phase = str(perfil["metadata"].get("alchemy_phase") or "").strip()

    phase_lower = raw_phase.lower()
    if "rubedo" in phase_lower:
        estacio = "Rubedo (Plenitud i Encarnació Daurada)"
    elif "citrinitas" in phase_lower:
        estacio = "Citrinitas (Alba Solar i Saviesa)"
    elif "albedo" in phase_lower:
        estacio = "Albedo (Purificació Lunar i Claredat)"
    elif "nigredo" in phase_lower:
        estacio = "Nigredo (Hivern Fèrtil i Transmutació Interior)"
    else:
        estacio = "Albedo-Citrinitas (Obertura Conscient)"

    return matched[:3], estacio


def _extract_ofereix_i_busca_arquetips(
    perfil: dict,
    notes: list | None = None,
    kg_items: list | None = None,
) -> tuple[list[str], list[str]]:
    """
    Extreu de forma 100% anònima (Regla 14: 0 noms propis, 0 dades privades)
    els Arquetips del que l'ànima OFEREIX (dons, passions, talents) i del que BUSCA/NECESSITA
    (necessitats, projectes, anhels vitals) combinant `user_notes` i `kg_entitats`/`kg_relacions`.
    """
    ofereix_parts: list[str] = []
    busca_parts: list[str] = []

    if isinstance(perfil, dict):
        if perfil.get("ofereix_arquetips") and isinstance(perfil.get("ofereix_arquetips"), list):
            ofereix_parts.extend(str(x) for x in perfil["ofereix_arquetips"] if x)
        if perfil.get("busca_arquetips") and isinstance(perfil.get("busca_arquetips"), list):
            busca_parts.extend(str(x) for x in perfil["busca_arquetips"] if x)
        meta = perfil.get("metadata") if isinstance(perfil.get("metadata"), dict) else {}
        for k_of in ("dons", "passions", "arquetip", "purpose"):
            if meta.get(k_of):
                ofereix_parts.append(str(meta.get(k_of)))
        for k_bu in ("necessitats", "projectes"):
            if meta.get(k_bu):
                busca_parts.append(str(meta.get(k_bu)))

    all_notes = list(notes) if isinstance(notes, list) else []
    if isinstance(perfil, dict) and isinstance(perfil.get("notes_compact"), list) and not all_notes:
        all_notes = list(perfil["notes_compact"])

    for n in all_notes:
        if isinstance(n, dict):
            cat = str(n.get("category") or "").strip().lower()
            cnt = str(n.get("content") or "").strip()
            if not cnt:
                continue
            if any(c in cat for c in ("dons", "passions", "feina", "gustos")):
                ofereix_parts.append(cnt)
            elif any(c in cat for c in ("necessitats", "projectes", "salut", "relacions")):
                busca_parts.append(cnt)
            else:
                ofereix_parts.append(cnt)
                busca_parts.append(cnt)

    all_kg = list(kg_items) if isinstance(kg_items, list) else []
    if isinstance(perfil, dict) and isinstance(perfil.get("kg_compact"), list) and not all_kg:
        all_kg = list(perfil["kg_compact"])

    for k_item in all_kg:
        if isinstance(k_item, dict):
            kt = str(k_item.get("tipus") or k_item.get("tipus_relacio") or "").strip().lower()
            kv = str(k_item.get("nom") or k_item.get("descripcio") or "").strip()
            if not kv:
                continue
            if kt in ("do_talent", "passio_vital", "te_el_do_de", "li_apassiona_fer"):
                ofereix_parts.append(kv)
            elif kt in ("necessitat_vital", "necessita_ara"):
                busca_parts.append(kv)

    blob_of = " ".join(ofereix_parts).lower()
    blob_bu = " ".join(busca_parts).lower()

    ofereix_matched = [
        theme_name for theme_name, kw_tuple in _ARCHETYPE_KEYWORDS if any(kw in blob_of for kw in kw_tuple)
    ]
    busca_matched = [
        theme_name for theme_name, kw_tuple in _ARCHETYPE_KEYWORDS if any(kw in blob_bu for kw in kw_tuple)
    ]

    if not ofereix_matched:
        temes_base, _ = _extract_cor_viu_themes(perfil, all_notes)
        ofereix_matched = temes_base[:2] if temes_base else ["Despertar Espiritual"]
    if not busca_matched:
        _, elem_mancat, _ = _extract_soul_living_elements(
            perfil if isinstance(perfil, dict) else {},
            str((perfil or {}).get("sign_sun") or ""),
            str((perfil or {}).get("sign_moon") or ""),
            str((perfil or {}).get("sign_asc") or ""),
        )
        _map_set = {
            "Terra": "Natura i Arrelament",
            "Aigua": "Sanació i Acompanyament",
            "Foc": "Lideratge i Emprenedoria",
            "Aire": "Saviesa i Estudi",
        }
        busca_matched = [_map_set.get(elem_mancat, "Saviesa i Estudi")]

    return list(dict.fromkeys(ofereix_matched))[:3], list(dict.fromkeys(busca_matched))[:3]


def calcular_ressonancia_tridimensional_vvk(
    perfil_a: dict,
    perfil_b: dict,
    notes_a: list | None = None,
    notes_b: list | None = None,
) -> dict:
    """
    Calcula la Ressonància d'Ànimes en 3 Dimensions i Els 4 Elements Vius (Quintaessència Alquímica):
    - Dimensió 1: El Cel Complet (`score_cel` 0..100 — Sol, Lluna, Ascendent, Disseny Humà, 7 Savieses)
    - Dimensió 2: La Freqüència del Cor Viu i Els 4 Elements (`score_cor_viu` 0..100 — Foc, Terra, Aire, Aigua + 8 Arquetips sense PII)
    - Dimensió 3: La Medicina Complementària (`score_medicina` 0..100 — Què aporta A a B i què aporta B a A)
    Compleix al 100% la Regla 14 (0 dates de naixement ni frases privades exposades).
    """
    p_a = perfil_a if isinstance(perfil_a, dict) else {}
    p_b = perfil_b if isinstance(perfil_b, dict) else {}

    mat_a = destil_lar_matriu(p_a)
    mat_b = destil_lar_matriu(p_b)
    cel_a = _parse_celestial_json(p_a)
    cel_b = _parse_celestial_json(p_b)

    bdate_a = _extract_internal_birth_date(p_a, cel_a)
    bdate_b = _extract_internal_birth_date(p_b, cel_b)
    res_cosmic = calcular_ressonancia_cosmica_vvk(bdate_a, bdate_b) if (bdate_a and bdate_b) else None

    sun_a = str((res_cosmic and res_cosmic.get("sun_sign_a")) or mat_a.get("Sol") or p_a.get("sign_sun") or "Bessons")
    sun_b = str((res_cosmic and res_cosmic.get("sun_sign_b")) or mat_b.get("Sol") or p_b.get("sign_sun") or "Bessons")

    raw_moon_a = mat_a.get("Lluna") if mat_a.get("Lluna") not in (None, "", "Desc", "Desconegut") else p_a.get("sign_moon")
    raw_moon_b = mat_b.get("Lluna") if mat_b.get("Lluna") not in (None, "", "Desc", "Desconegut") else p_b.get("sign_moon")
    moon_a = str(raw_moon_a or (res_cosmic and res_cosmic.get("moon_sign_a")) or sun_a)
    moon_b = str(raw_moon_b or (res_cosmic and res_cosmic.get("moon_sign_b")) or sun_b)

    elem_moon_a = _sign_element_ca(moon_a, (res_cosmic and res_cosmic.get("elem_moon_a")) or "Aigua")
    elem_moon_b = _sign_element_ca(moon_b, (res_cosmic and res_cosmic.get("elem_moon_b")) or "Aigua")

    raw_asc_a = mat_a.get("Ascendent") if mat_a.get("Ascendent") not in (None, "", "Desc", "Desconegut") else p_a.get("sign_asc")
    raw_asc_b = mat_b.get("Ascendent") if mat_b.get("Ascendent") not in (None, "", "Desc", "Desconegut") else p_b.get("sign_asc")
    asc_a = str(raw_asc_a or "Horitzó Obert")
    asc_b = str(raw_asc_b or "Horitzó Obert")

    hd_type_a = str(mat_a.get("Disseny Humà") or "Generador")
    hd_type_b = str(mat_b.get("Disseny Humà") or "Generador")
    if hd_type_a in ("Desc", "Desconegut"):
        hd_type_a = "Alquímic"
    if hd_type_b in ("Desc", "Desconegut"):
        hd_type_b = "Alquímic"

    # Sinergia d'Aura de Disseny Humà
    hd_pair = f"{hd_type_a.lower()} + {hd_type_b.lower()}"
    if ("generador" in hd_pair and "projector" in hd_pair):
        sinergia_hd_ca = f"Aliança Sagrada de Força Vital Sacral i Guia Direccional ({hd_type_a} ↔ {hd_type_b})"
        hd_bonus = 6
    elif "generador" in hd_type_a.lower() and "generador" in hd_type_b.lower():
        sinergia_hd_ca = f"Ressonància Sacral Creadora d'Alta Energia ({hd_type_a} ↔ {hd_type_b})"
        hd_bonus = 5
    elif "manifestador" in hd_pair or "reflector" in hd_pair:
        sinergia_hd_ca = f"Catalitzador d'Iniciació i Mirall Còsmic ({hd_type_a} ↔ {hd_type_b})"
        hd_bonus = 5
    else:
        sinergia_hd_ca = f" Harmonia d'Aures i Portes Solars ({hd_type_a} ↔ {hd_type_b})".strip()
        hd_bonus = 4

    if res_cosmic and res_cosmic.get("sun_moon_bridge_ca"):
        base_bridge = res_cosmic["sun_moon_bridge_ca"]
    elif _sign_element_ca(sun_a) == elem_moon_b or _sign_element_ca(sun_b) == elem_moon_a:
        base_bridge = f"Pont d'Or Sol-Lluna (Sol {sun_a}/Lluna {moon_a} ↔ Sol {sun_b}/Lluna {moon_b})"
    else:
        base_bridge = f"Refugi Lunar i Ascendent (Lluna {moon_a} [{elem_moon_a}] ↔ Lluna {moon_b} [{elem_moon_b}])"

    pont_sol_lluna_asc_ca = f"{base_bridge} · Ascendents {asc_a} ↔ {asc_b}"

    base_cel = int(res_cosmic["score"]) if res_cosmic else 82
    lunar_bonus = 4 if (elem_moon_a == elem_moon_b or moon_a == sun_b or moon_b == sun_a) else 2
    score_cel = min(100, max(65, round(base_cel * 0.92 + hd_bonus + lunar_bonus)))

    # ------------------------------------------------------------------
    # DIMENSIÓ 2: LA FREQÜÈNCIA DEL COR VIU I ELS 4 ELEMENTS VIUS
    # ------------------------------------------------------------------
    elem_viu_a, elem_mancat_a, weights_a = _extract_soul_living_elements(p_a, sun_a, moon_a, asc_a)
    elem_viu_b, elem_mancat_b, weights_b = _extract_soul_living_elements(p_b, sun_b, moon_b, asc_b)

    pair_set = {elem_viu_a, elem_viu_b}
    quintaessencia_activa = (elem_viu_a == elem_mancat_b) or (elem_viu_b == elem_mancat_a) or (len(pair_set) == 2)

    if pair_set == {"Aigua", "Terra"}:
        rel_4_elem_title = "L'Oasi Fèrtil (Aigua 💧 + Terra 🌍)"
        rel_4_elem_desc = (
            f"La Terra contenidora i serena d'una ànima dóna llera segura a l'Aigua profunda i sensible de l'altra; "
            f"l'Aigua fertilitza i estova la Terra ({elem_viu_a} ↔ {elem_viu_b})."
        )
        elem_pts = 94
    elif pair_set == {"Foc", "Aire"}:
        rel_4_elem_title = "La Flama Alada (Foc 🔥 + Aire 💨)"
        rel_4_elem_desc = (
            f"L'Aire de la visió i la paraula aviva el Foc de l'entusiasme; el Foc converteix les idees de l'Aire "
            f"en presència càlida i viva ({elem_viu_a} ↔ {elem_viu_b})."
        )
        elem_pts = 94
    elif elem_viu_a == elem_viu_b:
        rel_4_elem_title = f"Empatia Elemental Immediata ({elem_viu_a} + {elem_viu_b})"
        rel_4_elem_desc = (
            f"Totes dues ànimes respiren el mateix dialecte elemental ({elem_viu_a}) i es reconeixen sense esforç, "
            f"convocant juntes l'element {elem_mancat_a} com a horitzó d'equilibri."
        )
        elem_pts = 90
    elif pair_set == {"Foc", "Aigua"}:
        rel_4_elem_title = "El Vapor Alquímic i La Quintaessència (Foc 🔥 + Aigua 💧)"
        rel_4_elem_desc = (
            f"Unió d'alquímia profunda: la calidesa del Foc evita que l'Aigua es refredi en la malenconia, "
            f"i la tendresa de l'Aigua tempera el Foc perquè cremi com una llàntia sagrada ({elem_viu_a} ↔ {elem_viu_b})."
        )
        elem_pts = 92
    elif pair_set == {"Aire", "Terra"}:
        rel_4_elem_title = "El Jardí Pensant i La Quintaessència (Aire 💨 + Terra 🌍)"
        rel_4_elem_desc = (
            f"L'Aire aporta horitzó, lleugeresa i música a la Terra; la Terra ofereix arrel, cos i pau tangible "
            f"als somnis de l'Aire ({elem_viu_a} ↔ {elem_viu_b})."
        )
        elem_pts = 92
    else:
        rel_4_elem_title = f"Pont de la Quintaessència ({elem_viu_a} ↔ {elem_viu_b})"
        rel_4_elem_desc = (
            f"El que a una ànima li falta en la seva estació present ({elem_mancat_a}/{elem_mancat_b}), "
            f"l'altra ho porta com a presència viva ({elem_viu_a} ↔ {elem_viu_b})."
        )
        elem_pts = 91

    alquimia_4_elements_ca = f"{rel_4_elem_title}: {rel_4_elem_desc}"

    temes_a, estacio_a = _extract_cor_viu_themes(p_a, notes_a)
    temes_b, estacio_b = _extract_cor_viu_themes(p_b, notes_b)
    ofereix_a, busca_a = _extract_ofereix_i_busca_arquetips(p_a, notes_a)
    ofereix_b, busca_b = _extract_ofereix_i_busca_arquetips(p_b, notes_b)

    shared_themes = [t for t in temes_a if t in temes_b]
    match_of_a_bu_b = [t for t in ofereix_a if t in busca_b]
    match_of_b_bu_a = [t for t in ofereix_b if t in busca_a]
    has_gift_need_synergy = bool(match_of_a_bu_b or match_of_b_bu_a)

    if any(t in ("Art i Creació", "Lideratge i Emprenedoria", "Saviesa i Estudi") for t in (match_of_a_bu_b + match_of_b_bu_a)):
        tipus_pont_ca = "🎨 Aliança Creativa i de Missió"
    elif any(t in ("Sanació i Acompanyament", "Natura i Arrelament") for t in (match_of_a_bu_b + match_of_b_bu_a)) or (
        "Nigredo" in estacio_a or "Nigredo" in estacio_b
    ):
        tipus_pont_ca = "🕯️ Mirall de Guarició i Suport Vital"
    elif "Amor Conscient" in (match_of_a_bu_b + match_of_b_bu_a) and score_cel >= 92:
        tipus_pont_ca = "🌹 Alquímia Sagrada i Amor Conscient"
    else:
        tipus_pont_ca = "🤝 Amistat d'Ànima i Tribu"

    all_themes = list(dict.fromkeys(temes_a + temes_b))
    theme_bonus = 6 if (shared_themes or has_gift_need_synergy) else 3
    score_cor_viu = min(100, elem_pts + theme_bonus)

    estacio_alquimica_ca = f"{estacio_a} ↔ {estacio_b}"
    cor_viu_summary_ca = (
        f"Arquetips del Cor Viu en ressonància: {', '.join(all_themes[:4])} | "
        f"Pont d'Unió: {tipus_pont_ca} (Ofereix: {', '.join(ofereix_b[:2])} · Busca: {', '.join(busca_b[:2])}) | "
        f"Estació Alquímica: {estacio_alquimica_ca}"
    )

    # ------------------------------------------------------------------
    # DIMENSIÓ 3: LA MEDICINA COMPLEMENTÀRIA (RECIPROCITAT VIVA)
    # ------------------------------------------------------------------
    nawal_a_str = f"{res_cosmic['tone_a']} {res_cosmic['nawal_a']}" if res_cosmic else str(mat_a.get("Freqüència Maia") or "Nawal Solar")
    nawal_b_str = f"{res_cosmic['tone_b']} {res_cosmic['nawal_b']}" if res_cosmic else str(mat_b.get("Freqüència Maia") or "Nawal Lunar")
    wuxing_a_str = str(res_cosmic["wuxing_a"]) if res_cosmic else str(mat_a.get("BaZi (Wu Xing)") or elem_viu_a)
    wuxing_b_str = str(res_cosmic["wuxing_b"]) if res_cosmic else str(mat_b.get("BaZi (Wu Xing)") or elem_viu_b)

    prep_mancat_b = "d'" if str(elem_mancat_b)[:1].upper() in ("A", "E", "I", "O", "U") else "de "
    prep_mancat_a = "d'" if str(elem_mancat_a)[:1].upper() in ("A", "E", "I", "O", "U") else "de "
    medicina_a_cap_a_b = (
        f"L'Ànima 1 aporta el seu element viu {elem_viu_a} (nodrint la set {prep_mancat_b}{elem_mancat_b} de l'Ànima 2), "
        f"la claredat del Sol en {sun_a}, la sensibilitat de la Lluna en {moon_a} ({elem_moon_a}) "
        f"i el pols del Nawal {nawal_a_str} ({wuxing_a_str})."
    )
    medicina_b_cap_a_a = (
        f"L'Ànima 2 aporta el seu element viu {elem_viu_b} (nodrint la set {prep_mancat_a}{elem_mancat_a} de l'Ànima 1), "
        f"l'escalfor del Sol en {sun_b}, el refugi de la Lluna en {moon_b} ({elem_moon_b}) "
        f"i la saviesa del Nawal {nawal_b_str} ({wuxing_b_str})."
    )
    sintesi_medicina_mutua = (
        f"Medicina Recíproca dels 4 Elements ({elem_viu_a} ↔ {elem_viu_b}): {medicina_a_cap_a_b} "
        f"Alhora, {medicina_b_cap_a_a}"
    )

    complement_bonus = 6 if (quintaessencia_activa or has_gift_need_synergy) else 3
    occult_bonus = 4 if (res_cosmic and (res_cosmic.get("is_occult_tone_pair") or res_cosmic.get("is_mayan_cross_pair"))) else 2
    score_medicina = min(100, 88 + complement_bonus + occult_bonus)

    score_total_3d = min(100, int(round(0.45 * score_cel + 0.25 * score_cor_viu + 0.30 * score_medicina)))

    return {
        "score_cel": score_cel,
        "score_cor_viu": score_cor_viu,
        "score_medicina": score_medicina,
        "score_total_3d": score_total_3d,
        "sun_a": sun_a,
        "sun_b": sun_b,
        "moon_a": moon_a,
        "moon_b": moon_b,
        "elem_moon_a": elem_moon_a,
        "elem_moon_b": elem_moon_b,
        "asc_a": asc_a,
        "asc_b": asc_b,
        "hd_type_a": hd_type_a,
        "hd_type_b": hd_type_b,
        "sinergia_hd_ca": sinergia_hd_ca,
        "pont_sol_lluna_asc_ca": pont_sol_lluna_asc_ca,
        "elem_viu_a": elem_viu_a,
        "elem_viu_b": elem_viu_b,
        "elem_mancat_a": elem_mancat_a,
        "elem_mancat_b": elem_mancat_b,
        "weights_4_elements_a": weights_a,
        "weights_4_elements_b": weights_b,
        "quintaessencia_activa": quintaessencia_activa,
        "rel_4_elem_title": rel_4_elem_title,
        "alquimia_4_elements_ca": alquimia_4_elements_ca,
        "temes_cor_viu_a": temes_a,
        "temes_cor_viu_b": temes_b,
        "ofereix_arquetips_a": ofereix_a,
        "busca_arquetips_a": busca_a,
        "ofereix_arquetips_b": ofereix_b,
        "busca_arquetips_b": busca_b,
        "tipus_pont_ca": tipus_pont_ca,
        "estacio_alquimica_ca": estacio_alquimica_ca,
        "cor_viu_summary_ca": cor_viu_summary_ca,
        "medicina_a_cap_a_b": medicina_a_cap_a_b,
        "medicina_b_cap_a_a": medicina_b_cap_a_a,
        "sintesi_medicina_mutua": sintesi_medicina_mutua,
    }


def destillar_alquimia_7_savieses_thot(perfil_a: dict, perfil_b: dict) -> dict:
    """
    Combina les matrius de dues ànimes i calcula el Còdex de les 7 Savieses,
    les 3 Claus d'Alquímia de Thot i la Ressonància Tridimensional amb els 4 Elements Vius,
    complint estrictament la Regla 14 (0 dates de naixement crues exposades).
    """
    matriu_a = destil_lar_matriu(perfil_a)
    matriu_b = destil_lar_matriu(perfil_b)

    cel_a = _parse_celestial_json(perfil_a)
    cel_b = _parse_celestial_json(perfil_b)
    bdate_a = _extract_internal_birth_date(perfil_a, cel_a)
    bdate_b = _extract_internal_birth_date(perfil_b, cel_b)

    nom_a = matriu_a.get("Nom", "Ànima 1")
    nom_b = matriu_b.get("Nom", "Ànima 2")

    ressonancia = calcular_ressonancia_cosmica_vvk(bdate_a, bdate_b) if (bdate_a and bdate_b) else None
    res_3d = calcular_ressonancia_tridimensional_vvk(perfil_a, perfil_b)

    if ressonancia:
        savieses_7 = {
            "1_Occidental": f"{nom_a} (Sol {ressonancia['sun_sign_a']}, Lluna {res_3d['moon_a']}, Asc {matriu_a.get('Ascendent')}) ↔ {nom_b} (Sol {ressonancia['sun_sign_b']}, Lluna {res_3d['moon_b']}, Asc {matriu_b.get('Ascendent')}) · {ressonancia['solar_harmony']} (Δ{ressonancia['solar_angle']}°) · {ressonancia.get('sun_moon_bridge_ca', '')}",
            "2_Maia_Cholqij": f"{ressonancia['tone_a']} {ressonancia['nawal_a']} ↔ {ressonancia['tone_b']} {ressonancia['nawal_b']} · {ressonancia['nawal_harmony']} · {ressonancia['tone_harmony']}",
            "3_Taoista_BaZi_WuXing": ressonancia["wuxing_harmony"],
            "4_Vedica_Jyotish": ressonancia["vedic_harmony"],
            "5_Disseny_Huma_IChing": f"{ressonancia['iching_harmony']} ({matriu_a.get('Disseny Humà')} ↔ {matriu_b.get('Disseny Humà')} · {res_3d['sinergia_hd_ca']})",
            "6_Numerologia_Cabala": ressonancia["numerology_harmony"],
            "7_Sintesi_Alquimica": ressonancia["seven_wisdoms_ca"],
        }
        claus_3 = {
            "La_Llum_de_l_Encontre": ressonancia["llum_encontre"],
            "L_Ombra_a_Cuidar": ressonancia["ombra_a_cuidar"],
            "El_Tercer_Esser": ressonancia["tercer_esser"],
            "Resum_3_Claus": ressonancia["three_keys_ca"],
        }
        score = ressonancia["score"]
        tier = ressonancia["tier"]
    else:
        savieses_7 = {
            "1_Occidental": f"{nom_a} (Sol {matriu_a.get('Sol')}, Lluna {matriu_a.get('Lluna')}, Asc {matriu_a.get('Ascendent')}) ↔ {nom_b} (Sol {matriu_b.get('Sol')}, Lluna {matriu_b.get('Lluna')}, Asc {matriu_b.get('Ascendent')})",
            "2_Maia_Cholqij": f"{matriu_a.get('Freqüència Maia') or 'Desc'} ↔ {matriu_b.get('Freqüència Maia') or 'Desc'}",
            "3_Taoista_BaZi_WuXing": f"{matriu_a.get('BaZi (Wu Xing)')} ↔ {matriu_b.get('BaZi (Wu Xing)')}",
            "4_Vedica_Jyotish": f"{matriu_a.get('Jyotish (Vèdic)')} ↔ {matriu_b.get('Jyotish (Vèdic)')}",
            "5_Disseny_Huma_IChing": f"{matriu_a.get('Disseny Humà')} ↔ {matriu_b.get('Disseny Humà')}",
            "6_Numerologia_Cabala": f"Camins de Vida {matriu_a.get('Camí de Vida')} ↔ {matriu_b.get('Camí de Vida')}",
            "7_Sintesi_Alquimica": f"Alquímia Arquetípica entre {nom_a} i {nom_b}",
        }
        claus_3 = {
            "La_Llum_de_l_Encontre": f"Ressonància solar i lunar entre {matriu_a.get('Sol')} i {matriu_b.get('Sol')}.",
            "L_Ombra_a_Cuidar": f"Escoltar amb tendresa els ritmes d'element {matriu_a.get('Element Dominant')} i {matriu_b.get('Element Dominant')}.",
            "El_Tercer_Esser": f"Camí compartit entre els Nawals {matriu_a.get('Freqüència Maia')} i {matriu_b.get('Freqüència Maia')}.",
            "Resum_3_Claus": f"✨ Ressonància {matriu_a.get('Sol')}↔{matriu_b.get('Sol')} | 🕯️ Cura elemental | 🌹 Propòsit compartit",
        }
        score = None
        tier = "Alquímia Arquetípica"

    return {
        "Nom_A": nom_a,
        "Nom_B": nom_b,
        "Score_Ressonancia": score,
        "Tier_Alquimic": tier,
        "Codex_7_Savieses": savieses_7,
        "Tres_Claus_Alquimia": claus_3,
        "Ressonancia_3D_i_4_Elements": res_3d,
    }


async def forjar_sinastria_oficial(record_a: dict, record_b: dict) -> dict:
    """Extrau i fusiona les matrius astrològiques nues i l'Alquímia de les 7 Savieses perquè el Frontend o l'Orquestrador les processi instantàniament."""
    try:
        matriu_a = destil_lar_matriu(record_a)
        matriu_b = destil_lar_matriu(record_b)

        nom_a = matriu_a.get("Nom", "Ànima 1")
        nom_b = matriu_b.get("Nom", "Ànima 2")

        logger.info(f"🌌 [SINASTRIA] Encreuant instàniament els cels de {nom_a} i {nom_b} a la Farga...")

        alquimia_7 = destillar_alquimia_7_savieses_thot(record_a, record_b)

        resposta_hibrida = {
            "Anima_1": matriu_a,
            "Anima_2": matriu_b,
            "Alquimia_7_Savieses": alquimia_7,
            "Alquimia_Requerida": True,
        }

        return resposta_hibrida

    except Exception as e:
        logger.error(f"❌ [SINASTRIA] Error: {e}", exc_info=True)
        return {"error": "El Teler no ha pogut fusionar aquests dos cels."}
