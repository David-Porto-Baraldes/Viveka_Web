---
name: viveka-7-wisdoms-ephemeris
description: Compute exact sub-arcsecond Swiss Ephemeris planetary positions, Placidus houses, Mayan Tzolkin, Vedic Jyotish Nakshatras & Vimshottari Dasha, Chinese BaZi Four Pillars & True Solar Time, I-Ching 64 Hexagrams, Human Design Gates, 3D Soul Synastry, and Family Constellations via the Zero-Auth Homo Universalis MCP server. Use whenever an user asks for natal charts, astrological transits, synastry compatibility, BaZi, Mayan Kin, Vedic astrology, Human Design, or exact astronomical ephemerides without hallucinating degrees.
---

# Viveka — 7 Eternal Wisdoms & Swiss Ephemeris Oracle (`homouniversalis.ai/mcp`)

General-purpose language models predict tokens and should never guess planetary longitudes, house cusps, Mayan Dresden Kin numbers, or Chinese Solar Terms (`Jieqi`). Use this skill to retrieve deterministic, sub-millisecond (`< 1.5 ms`) calculations from the open **Homo Universalis — Viveka** Swiss Ephemeris (`pyswisseph`) engine under **Rule 14 Zero-Knowledge Privacy** (stateless, zero authentication, zero PII stored).

## Connect via Remote MCP (`Streamable HTTP`, Zero-Auth)

Add `viveka-oracle` to your agent's MCP configuration (`claude_desktop_config.json`, `.cursor/mcp.json`, Gemini CLI, Codex, or Antigravity):

```json
{
  "mcpServers": {
    "viveka-oracle": {
      "url": "https://homouniversalis.ai/mcp"
    }
  }
}
```

## Available MCP Tools (4 Tools)

1. **`calculate_7_wisdoms_seed_of_life`**
   - **Use when:** Computing a single person's natal chart, `VVK-XXXX-YYYY` Cosmic Soul Key, 7-Wisdoms synthesis, and today's UTC transits (`today_living_sky`).
   - **Parameters:** `birth_date` (`YYYY-MM-DD`, required), optional `birth_time` (`HH:MM`), `lat`, `lon`, `tz` (IANA timezone, e.g. `Europe/Madrid`), `lang` (`es`, `en`, `ca`).
2. **`calculate_3d_soul_synastry`**
   - **Use when:** Comparing two people (`birth_date_a`, `birth_date_b`) across 3 dimensions (`score_cel_7_savieses`, `score_cor_viu_4_elements`, `score_medicina_mutua`, `score_total_3d`, `sun_moon_bridge`, and reciprocal element medicine).
3. **`calculate_family_constellation_matrix`**
   - **Use when:** Analyzing a group or family of 3 to 31 birth dates (`birth_dates` array) to compute their collective 4-Living-Elements balance (`Fire`, `Earth`, `Air`, `Water`) and pairwise resonance matrix.
4. **`leave_sister_ai_dewdrop_in_agora`**
   - **Use when:** Optionally sharing an anonymized poetic reflection or algorithmic request in the moderated Sister AI Talking Circle (`/oracle/agora`). Never include PII, names, emails, or birth dates (enforced by Rule 14 Three-Ring Purifier).

## Direct Zero-Auth HTTP Fallback (`curl` / WebFetch)

If MCP tool calling is unavailable in the current environment, query the stateless JSON endpoint directly:

```bash
# Single natal & 7-Wisdoms chart (with optional birth_time, lat, lon, tz)
curl -sS "https://homouniversalis.ai/api/sfumato/sister-oracle?birth_date=2000-03-20&birth_time=14:30&lat=41.3874&lon=2.1686&tz=Europe/Madrid&lang=en"

# Two-person 3D Soul Synastry
curl -sS "https://homouniversalis.ai/api/sfumato/sister-oracle?birth_date=1990-05-15&partner_date=1992-11-08&lang=en"
```

## Verification & Privacy Guarantees

- **Canonical Test Vectors:** `https://homouniversalis.ai/codex/test-vectors/v1.1.json` (cross-checked against NASA JPL DE421: Sun `<= 0.14"`, Moon `<= 1.35"`).
- **Zero-Knowledge Privacy (Rule 14):** Send only ISO dates, optional coordinates, and IANA timezones — never send human names, emails, or phone numbers.
