"""OCR/spelling cleanup for Native Sons availability data.
Apply known fixes to the parsed JSON, then regenerate availability_data.js.
"""
import json
import re

INPUT = "/Users/tfross/.hermes/nativesons-retail/availability.json"
OUTPUT = "/Users/tfross/.hermes/nativesons-retail/availability.json"

# Substring replacements (case-sensitive). Order matters - longer patterns first.
FIXES = [
    # 8 → t (very common: Li8le, fru8cosa, Polys8chum, etc.)
    ("Li8le", "Little"),
    ("LiRle", "Little"),
    ("Li1le", "Little"),
    ("LiAle", "Little"),
    ("Wa8le", "Wattle"),
    ("fru8cosa", "fruticulosa"),
    ("Polys8chum", "Polystichum"),
    ("Calamagros8s", "Calamagrostis"),
    ("amethys8na", "amethystina"),
    # 4 → a (saba4us → sabatius)
    ("saba4us", "sabatius"),
    # 1 → i
    ("ves1ta", "vestita"),
    # B → t (botle/bottle) - in these specific contexts
    ("boDle", "bottle"),
    ("BoDle", "Bottle"),
    # HGaorodde'n → Garden
    ("HGaorodde'n", "Garden"),
    # ArgenBna → Argentina
    ("ArgenBna", "Argentina"),
    # Matilija poppy OCR
    ("Ma6lija", "Matilija"),
    # "Res3os" / "ResJos" → "Restios" (section header)
    ("Res3os", "Restios"),
    ("ResJos", "Restios"),
    # "Con1' Confe3" → "Confetti"
    ("Con1' Confe3", "Confetti"),
    # SoR / SoZ / SoT → "Soft" (likely ft→soft OCR error)
    ("SoR orange", "Soft orange"),
    ("SoR lavender", "Soft lavender"),
    ("SoR pink", "Soft pink"),
    ("SoZ pink", "Soft pink"),
    ("SoT pink", "Soft pink"),
    # "pBinlokom" garbled - looking at context: "SoR orange, maturing bright pBinlokom"
    # This is for Hesperozygis which has orange flowers. Likely "bright pink bloom" but
    # the original isn't fully clear. Best guess: just strip the garbled word
    ("pBinlokom", "pink"),
    # Hesperozygis x satureja was missing the bloom info - rewrite the whole flower_color
    # Actually just leave it; the fix is for SoR orange and the pink replacement.
    # "LiRle" was already covered above
    # Generic: "naveson" → "nativeson" (shouldn't appear in data but be safe)
    ("naveson", "nativeson"),
    # Additional: "frutLcosa" / "frutBcosa" / "frutIcosa" - I haven't seen these yet
    # "PaciTic" / "paciTic" → "Pacific" / "pacific"
    ("PaciTic", "Pacific"),
    ("paciTic", "pacific"),
    # "T omanes" / "T omales" → "Tomales" (T followed by space)
    ("T omanes", "Tomales"),
    ("T omales", "Tomales"),
    # "ResJos" already covered
    # "MatVija" / "Matilija" - covered
    # "frutLcosa" / "frutBcosa"
    ("frutLcosa", "fruticulosa"),
    ("frutBcosa", "fruticulosa"),
    # Weskaapse dakriet is actually correct (it's Afrikaans/Dutch for "Cape thatching reed")
    # But "Chondropetalum tectorum" common name in English is "Cape rush" - keep as-is since
    # the PDF uses Weskaapse dakriet intentionally
    # "HyssopiB" → "hyssopifolia"
    ("HyssopiB", "hyssopifolia"),
    # 2gal / plant variants (shouldn't appear in our data)
    # "odBlebrush" / "oDle" already covered
    # "Dickson's" / "Dickson" - leave as is (apostrophe may be correct)
    # "Grevillea fililoba" - might be "fililoba" (correct species) or OCR
    # "Pittosporum 'Elfin'" - leave
    # "Pittosporum tenuifolium 'Beach Ball'™" - leave
    # "Pittosporum eugenioides 'Variegatum'" - leave
    # "Itoh" / "Molly's" / etc. - leave alone
    # PiIosporum → Pittosporum (capital I misread as t in PDF)
    ("PiIosporum", "Pittosporum"),
    # LeonoAs → Leonotis (capital A misread as t in PDF)
    ("LeonoAs", "Leonotis"),
    # arguAfolius → argutifolius (Helleborus)
    ("arguAfolius", "argutifolius"),
    # angusAfolia → angustifolia (Lavandula)
    ("angusAfolia", "angustifolia"),
]

# Patterns to also catch: any word in flower_color that ends in "m" but the actual word
# is something else. e.g. "pBinlokom" - I'll handle by the explicit fix above.

def apply_fixes(s):
    if not s:
        return s
    for old, new in FIXES:
        if old in s:
            s = s.replace(old, new)
    return s

# Post-process fixes for specific records
SPECIFIC_FIXES = [
    # The Hesperozygis record has a complex fix
    {
        "match_botanical": "Hesperozygis x satureja 'Sunrise Mojito'",
        "fixes": {
            "flower_color": "Soft orange, maturing bright pink",
        }
    },
    # Convolvulus sabatius is the actual species (not sabatius Prime White)
    # already handled by saba4us→sabatius
    # Convolvulus sabatius 'Compacta' needs the prime check
    {
        "match_botanical_starts": "Convolvulus sab",
        "fixes": {
            "botanical": "Convolvulus sabatius",  # template; specific plants handled below
        }
    },
]

# Convolvulus sabatius is the actual species
# but we have 3 entries: "Convolvulus sab. 'Compacta'", "Convolvulus sabatius", "Convolvulus sabatius 'Prime White'"
# the first one is the abbreviation "sab." which is a known botany shorthand
# so keep that one as-is

def fix_record(p):
    bot = p.get("botanical", "")
    com = p.get("common", "")
    orig = p.get("origin", "")
    fc = p.get("flower_color", "")
    ft = p.get("flower_time", "")
    sec = p.get("section", "")

    new_bot = apply_fixes(bot)
    new_com = apply_fixes(com)
    new_orig = apply_fixes(orig)
    new_fc = apply_fixes(fc)
    new_ft = apply_fixes(ft)
    new_sec = apply_fixes(sec)

    # Specific overrides
    if "Hesperozygis x satureja 'Sunrise Mojito'" in new_bot:
        new_fc = "Soft orange, maturing bright pink"

    # Convolvulus sab. (abbreviation, keep as-is) vs saba4us (OCR error, fix to sabatius)
    if "sab. " in new_bot or new_bot.endswith("sab."):
        pass  # keep abbreviation
    elif "sabatius" in new_bot or "saba4us" in new_bot:
        new_bot = new_bot.replace("saba4us", "sabatius")

    if new_bot != bot or new_com != com or new_orig != orig or new_fc != fc or new_ft != ft or new_sec != sec:
        return {
            "changed": True,
            "before": {"botanical": bot, "common": com, "origin": orig, "flower_color": fc, "flower_time": ft, "section": sec},
            "after": {"botanical": new_bot, "common": new_com, "origin": new_orig, "flower_color": new_fc, "flower_time": new_ft, "section": new_sec},
        }
    return {"changed": False}


def main():
    d = json.load(open(INPUT))

    changes = []
    for i, p in enumerate(d["plants"]):
        r = fix_record(p)
        if r["changed"]:
            changes.append((i, p, r))

    # Apply changes
    for i, p, r in changes:
        for k, v in r["after"].items():
            p[k] = v

    # Report
    print(f"Applied {len(changes)} fixes:")
    for i, p, r in changes:
        before = r["before"]
        after = r["after"]
        for k in after:
            if before[k] != after[k]:
                print(f"  [{p.get('botanical', '?')[:50]:50}] {k}: {before[k]!r}  ->  {after[k]!r}")

    # Save
    with open(OUTPUT, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

    # Regenerate availability_data.js
    js = "/* Native Sons Weekly Availability - generated */\n"
    js += "window.AVAILABILITY = " + json.dumps(d, indent=2, ensure_ascii=False) + ";\n"
    with open("/Users/tfross/.hermes/nativesons-retail/availability_data.js", "w") as f:
        f.write(js)
    print(f"\nRegenerated availability_data.js ({len(js)} bytes)")

if __name__ == "__main__":
    main()
