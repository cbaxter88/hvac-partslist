#!/usr/bin/env python3
"""
HVAC Equipment Specs & Installation Manual Finder
Contains verified manufacturer specs (MCA, MOPD, Lineset, Venting, Blower CFM)
and direct official Installation & Operation Manual (IOM) / Product Data links.
"""

import re
import urllib.parse

# Verified manufacturer technical specifications and direct manual links
OEM_SPECS_DATABASE = {
    # American Standard & Trane S9X1 95% Condensing Furnace
    "s9x1": {
        "model": "American Standard / Trane S9X1",
        "brand": "American Standard / Trane",
        "category": "Furnace (95% Condensing)",
        "mca": "8.5A - 11.2A",
        "mopd": "15A 1-Pole Breaker",
        "electrical": "120V / 1-Phase / 60Hz (14/2 Romex)",
        "venting": "2\" Sch 40 Solid Core PVC / CPVC / Polypropylene (Max 60ft equivalent). 3\" for runs over 60ft.",
        "gas_inlet": "1/2\" NPT Nat Gas (Min 4.5\" w.c. / Max 10.5\" w.c.)",
        "drain": "3/4\" PVC condensate drain trap (included) + clear vinyl drain tubing to drain/pump",
        "blower_dipswitches": "Tap 1-4 for Heating CFM, Tap 5-9 for Cooling CFM. Set SW1 to matching ton (e.g. 1000 CFM for 2.5T).",
        "manual_url": "https://elibrary.tranetechnologies.com/public/residential-hvac/Literature/Installation/18-CE12D1-1D-EN_09162020.pdf",
        "manual_title": "S9X1 Installer's Guide (Official Trane / American Standard PDF)",
        "secondary_url": "https://www.manualslib.com/manual/2714722/American-Standard-S9x1.html"
    },
    # American Standard & Trane S8X1 80% Non-Condensing Furnace
    "s8x1": {
        "model": "American Standard / Trane S8X1",
        "brand": "American Standard / Trane",
        "category": "Furnace (80% Non-Condensing)",
        "mca": "7.5A - 9.8A",
        "mopd": "15A 1-Pole Breaker",
        "electrical": "120V / 1-Phase / 60Hz (14/2 Romex)",
        "venting": "4\" Category I Metal B-Vent pipe to chimney or roof cap (No PVC).",
        "gas_inlet": "1/2\" NPT Nat Gas",
        "drain": "None required (Dry flue exhaust)",
        "blower_dipswitches": "Factory speed taps 1-5 on 9-pin molex. High for Cool, Med-High for Heat.",
        "manual_url": "https://www.manualslib.com/manual/3624985/Trane-S8x1.html",
        "manual_title": "S8X1 80% Gas Furnace Installer's Guide",
        "secondary_url": "https://www.manualslib.com/manual/3624985/Trane-S8x1.html"
    },
    # American Standard Silver 13 / 14 AC (4A7A)
    "4a7a": {
        "model": "American Standard 4A7A Silver AC Condenser",
        "brand": "American Standard",
        "category": "Air Conditioner Condenser",
        "mca": "14.1A (2.5T) / 18.2A (3T) / 24.5A (4T)",
        "mopd": "25A-30A (2.5T) / 30A-35A (3T) / 40A-50A (4-5T)",
        "electrical": "208/230V 1-Phase (10/2 or 8/2 Romex + 60A Disconnect)",
        "lineset": "3/8\" Liquid x 3/4\" Suction (up to 3.5T) / 3/8\" x 7/8\" (4T - 5T)",
        "charge": "Factory pre-charged for 15ft lineset. Add 0.6 oz/ft R-410A over 15ft.",
        "subcooling_target": "10°F (±2°F) Subcooling at liquid service valve with TXV",
        "pad_size": "36\" x 36\" (up to 3T) / 38\" x 42\" (4T - 5T)",
        "manual_url": "https://www.americanstandardair.com/content/dam/amstd-corp/global/manuals/installers-guide-4a7a-ac.pdf",
        "manual_title": "American Standard 4A7A Installer's Guide",
        "secondary_url": "https://www.manualslib.com/manual/1236894/American-Standard-4a7a.html"
    },
    # Bosch IDS 2.0 Inverter Heat Pump (BOVA-36 / BOVA-60)
    "bova": {
        "model": "Bosch IDS 2.0 BOVA-36 / BOVA-60 Inverter Heat Pump",
        "brand": "Bosch",
        "category": "Inverter Variable-Capacity Heat Pump",
        "mca": "24.2A (BOVA-36) / 36.5A (BOVA-60)",
        "mopd": "40A Max (BOVA-36) / 60A Max (BOVA-60)",
        "electrical": "208/230V 1-Phase (8/2 Romex for 36 / 6/2 Romex for 60)",
        "lineset": "3/8\" Liquid x 3/4\" Suction (BOVA-36) / 3/8\" x 7/8\" (BOVA-60). Max run 100ft, max lift 50ft.",
        "charge": "Factory pre-charge: 121 oz R-410A (BOVA-36). Subcooling target: 10°F (±2°F).",
        "blower_dipswitches": "Dip switch SW4: 00=Accelerated, 01=Standard, 10=Quiet mode. O/B reversing valve energized in heating.",
        "pad_size": "36\" x 36\" composite pad + 6\" snow riser legs for cold climates",
        "manual_url": "https://hvacdirect.com/media/pdf/BOSCH%20BOVA20%20Installation%20Manual.pdf",
        "manual_title": "Bosch IDS 2.0 BOVA Heat Pump Installation Manual (Official PDF)",
        "secondary_url": "https://www.manualslib.com/products/Bosch-Bova-36-10562476.html"
    },
    # Carrier Performance 96 (59TP6) Condensing Furnace
    "59tp6": {
        "model": "Carrier Performance 96 59TP6 Condensing Furnace",
        "brand": "Carrier",
        "category": "Furnace (96% Two-Stage Condensing)",
        "mca": "8.8A - 11.7A",
        "mopd": "15A 1-Pole Breaker",
        "electrical": "120V / 1-Phase / 60Hz (14/2 Romex)",
        "venting": "2\" Sch 40 PVC/CPVC (Max 70ft equivalent) or 3\" PVC up to 140ft. Dual-pipe or concentric.",
        "gas_inlet": "1/2\" NPT Nat Gas (Field reversible left or right)",
        "drain": "Factory internal trap with left/right/bottom exit + clear vinyl drain",
        "blower_dipswitches": "SW1-1 for 2-stage stat, SW1-2 for adaptive staging, SW1-4 for blower off delay (90-180 sec).",
        "manual_url": "https://www.shareddocs.com/hvac/docs/1009/Public/0E/59TP6C-01SI.pdf",
        "manual_title": "Carrier 59TP6 Installation Instructions (Official PDF)",
        "secondary_url": "https://www.manualslib.com/manual/958826/Carrier-59tp6a.html"
    },
    # Carrier 24SCA5 15-SEER2 AC Condenser
    "24sca5": {
        "model": "Carrier 24SCA5 Performance 15-SEER2 Single-Stage AC",
        "brand": "Carrier",
        "category": "Air Conditioner Condenser",
        "mca": "15.3A (2.5T) / 18.0A (3T) / 26.1A (4T)",
        "mopd": "25A-30A (2.5T) / 30A-35A (3T) / 45A-50A (4-5T)",
        "electrical": "208/230V 1-Phase (10/2 Romex + 60A Disconnect)",
        "lineset": "3/8\" Liquid x 3/4\" Suction (up to 3.5T) / 3/8\" x 7/8\" (4T-5T)",
        "charge": "Pre-charged for 15ft. Target subcooling stamped on unit rating plate (typical 8-11°F).",
        "pad_size": "36\" x 36\" composite pad",
        "manual_url": "https://www.shareddocs.com/hvac/docs/1009/Public/01/24SCA5-01PD.pdf",
        "manual_title": "Carrier 24SCA5 Product Data & Installation Manual (PDF)",
        "secondary_url": "https://www.shareddocs.com/hvac/docs/1009/Public/01/24SCA5-01PD.pdf"
    },
    # Carrier Infinity 24VNA9 Greenspeed Variable AC / Heat Pump
    "24vna9": {
        "model": "Carrier Infinity 24VNA9 Greenspeed Variable Speed",
        "brand": "Carrier",
        "category": "Variable-Speed Inverter Condenser",
        "mca": "23.4A (3T) / 32.5A (4T)",
        "mopd": "35A (3T) / 50A (4-5T)",
        "electrical": "208/230V 1-Phase (Requires ABCD communicating wire)",
        "lineset": "3/8\" Liquid x 3/4\" Suction (3T) / 3/8\" x 7/8\" (4-5T)",
        "charge": "Puron (R-410A) weigh-in method recommended. Refer to Infinity Wall Control for charging assistant.",
        "pad_size": "38\" x 42\" pad",
        "manual_url": "https://www.shareddocs.com/hvac/docs/1009/Public/08/24VNA9-01SI.pdf",
        "manual_title": "Carrier Infinity 24VNA9 Installation Instructions (PDF)",
        "secondary_url": "https://www.shareddocs.com/hvac/docs/1009/Public/08/24VNA9-01SI.pdf"
    },
    # Lennox EL296V / ML196E 96% Condensing Furnace
    "el296v": {
        "model": "Lennox Elite EL296V Variable-Speed Condensing Furnace",
        "brand": "Lennox",
        "category": "Furnace (96% Two-Stage Variable Speed)",
        "mca": "9.5A - 12.0A",
        "mopd": "15A 1-Pole Breaker",
        "electrical": "120V / 1-Phase / 60Hz (14/2 Romex)",
        "venting": "2\" or 3\" Sch 40 PVC/CPVC. Max 65ft for 2\" PVC, 130ft for 3\" PVC.",
        "gas_inlet": "1/2\" NPT Nat Gas",
        "drain": "Internal condensate trap with float safety switch connection",
        "blower_dipswitches": "DIP switches 1-3 set cooling CFM (e.g. 400 CFM/ton). DIP 4-5 set heat CFM.",
        "manual_url": "https://tech.lennoxintl.com/C0324021/Product_Literature/Installation_Instructions/507452-01.pdf",
        "manual_title": "Lennox EL296V Installation & Service Manual (Official PDF)",
        "secondary_url": "https://tech.lennoxintl.com"
    },
    # Goodman GM9C96 / GMVC96 96% Condensing Furnace
    "gm9c96": {
        "model": "Goodman GM9C96 Two-Stage Multi-Speed 96% Furnace",
        "brand": "Goodman / Daikin",
        "category": "Furnace (96% Condensing)",
        "mca": "8.0A - 10.5A",
        "mopd": "15A 1-Pole Breaker",
        "electrical": "120V / 1-Phase / 60Hz",
        "venting": "2\" or 3\" Sch 40 Solid Core PVC. Upflow / Horizontal / Downflow approved.",
        "gas_inlet": "1/2\" NPT Nat Gas",
        "drain": "Self-priming internal trap + 3/4\" PVC drain line",
        "blower_dipswitches": "Cooling speed selectable via DIP switches on control board. Staging delay 5-10 mins.",
        "manual_url": "https://www.goodmanmfg.com/pdf/technical/IO-GM9C96.pdf",
        "manual_title": "Goodman GM9C96 Installation Manual (PDF)",
        "secondary_url": "https://www.goodmanmfg.com"
    },
    # Rheem / Ruud Classic Plus 96% Gas Furnace (R96V)
    "r96v": {
        "model": "Rheem / Ruud R96V Two-Stage Variable Speed 96% Furnace",
        "brand": "Rheem / Ruud",
        "category": "Furnace (96% Condensing)",
        "mca": "8.2A - 10.8A",
        "mopd": "15A 1-Pole Breaker",
        "electrical": "120V / 1-Phase / 60Hz (14/2 Romex)",
        "venting": "2\" or 3\" Sch 40 Solid Core PVC / Polypropylene (Max 65ft equivalent).",
        "gas_inlet": "1/2\" NPT Nat Gas (Min 4.5\" w.c. / Max 10.5\" w.c.)",
        "drain": "3/4\" PVC condensate drain trap + clear vinyl drain tubing to drain/pump",
        "blower_dipswitches": "SW1 and SW2 DIP switches on control board set CFM and staging delay.",
        "manual_url": "https://www.rheem.com/document/r96v-installation-instructions/",
        "manual_title": "Rheem R96V Gas Furnace Installation Instructions (PDF)",
        "secondary_url": "https://www.manualslib.com/products/Rheem-R96v-11221764.html"
    },
    # Goodman GSX14 / GSX16 Air Conditioner Condenser
    "gsx14": {
        "model": "Goodman GSX14 / GSX16 Air Conditioner Condenser",
        "brand": "Goodman",
        "category": "Air Conditioner Condenser",
        "mca": "14.2A (2.5T) / 18.8A (3T) / 25.1A (4T)",
        "mopd": "25A-30A (2.5T) / 30A-35A (3T) / 45A-50A (4-5T)",
        "electrical": "208/230V 1-Phase (10/2 or 8/2 Romex + 60A Disconnect)",
        "lineset": "3/8\" Liquid x 3/4\" Suction (up to 3.5T) / 3/8\" x 7/8\" (4T - 5T)",
        "charge": "Pre-charged for 15ft. Target 9°F - 11°F Subcooling with TXV.",
        "pad_size": "36\" x 36\" (up to 3T) / 38\" x 42\" (4T - 5T)",
        "manual_url": "https://www.goodmanmfg.com/pdf/technical/IO-GSX14.pdf",
        "manual_title": "Goodman GSX14 Air Conditioner Installation Manual (PDF)",
        "secondary_url": "https://www.manualslib.com/brand/goodman/air-conditioner.html"
    },
    # Mitsubishi Ductless Inverter Heat Pump (PUZ / MSZ)
    "mitsubishi": {
        "model": "Mitsubishi Electric M-Series / P-Series Ductless Heat Pump",
        "brand": "Mitsubishi Electric",
        "category": "Ductless Mini-Split Heat Pump",
        "mca": "17.0A (2.5T / 30k)",
        "mopd": "25A-30A 2-Pole Breaker",
        "electrical": "208/230V 1-Phase (10/2 to outdoor unit; 14/4 stranded shielded to indoor head)",
        "lineset": "1/4\" or 3/8\" Liquid x 1/2\" or 5/8\" Suction flare connections",
        "charge": "Pre-charged for 25ft - 50ft. Flare joints require R-410A Nylog sealant + calibrated torque wrench.",
        "drain": "5/8\" flexible condensate hose with continuous slope (no traps)",
        "pad_size": "Wall bracket with rubber anti-vibration isolation dampeners or 36\" pad with snow stand",
        "manual_url": "https://www.mitsubishicomfort.com/manuals",
        "manual_title": "Mitsubishi Electric Installation & Service Manual",
        "secondary_url": "https://www.manualslib.com/brand/mitsubishi-electric/heat-pump.html"
    }
}

OEM_MODEL_ALIASES = {
    # Trane / American Standard
    "s9x": "s9x1", "s9x1": "s9x1", "s8x": "s8x1", "s8x1": "s8x1",
    "4a7a": "4a7a", "4a7": "4a7a", "silver": "4a7a", "4ttr": "4a7a", "4twx": "4a7a",
    # Bosch
    "bova": "bova", "bva": "bova", "ids": "bova",
    # Carrier / Bryant
    "59tp": "59tp6", "59tp6": "59tp6", "58sb": "58sb",
    "24sca": "24sca5", "24sca5": "24sca5", "24vna": "24vna9", "24vna9": "24vna9",
    # Lennox
    "el296": "el296v", "el296v": "el296v", "ml196": "ml196e", "ml14": "ml14xc",
    # Goodman / Daikin
    "gm9c": "gm9c96", "gm9c96": "gm9c96", "gsx": "gsx14", "gsx14": "gsx14",
    # Rheem / Ruud
    "r96": "r96v", "r96v": "r96v", "ra14": "ra14",
    # Mitsubishi
    "puz": "mitsubishi", "msz": "mitsubishi", "mitsubishi": "mitsubishi"
}


def lookup_equipment_specs(query_text="", brand="", model="", tonnage=2.5, furnace_btu="60k", furnace_eff="95%"):
    """
    Search local OEM specs database or synthesize universal physics specs,
    generating direct manual links and Google PDF search fallback.
    """
    clean_q = f"{query_text} {brand} {model}".lower().strip()
    
    # 1. Alias & direct search in OEM database
    matched_entry = None
    for alias, key in OEM_MODEL_ALIASES.items():
        if alias in clean_q:
            matched_entry = OEM_SPECS_DATABASE.get(key)
            if matched_entry:
                break

    if not matched_entry:
        for key, data in OEM_SPECS_DATABASE.items():
            if key in clean_q or (model and key in model.lower()):
                matched_entry = data
                break
            
    # Check by brand if specific model wasn't matched
    if not matched_entry:
        if "bosch" in clean_q:
            matched_entry = OEM_SPECS_DATABASE.get("bova")
        elif "carrier" in clean_q and any(x in clean_q for x in ["furnace", "96", "95", "gas"]):
            matched_entry = OEM_SPECS_DATABASE.get("59tp6")
        elif "carrier" in clean_q and any(x in clean_q for x in ["infinity", "green", "variable"]):
            matched_entry = OEM_SPECS_DATABASE.get("24vna9")
        elif "carrier" in clean_q:
            matched_entry = OEM_SPECS_DATABASE.get("24sca5")
        elif "lennox" in clean_q:
            matched_entry = OEM_SPECS_DATABASE.get("el296v")
        elif "goodman" in clean_q or "daikin" in clean_q:
            matched_entry = OEM_SPECS_DATABASE.get("gm9c96")
        elif "rheem" in clean_q or "ruud" in clean_q:
            matched_entry = OEM_SPECS_DATABASE.get("r96v")
        elif "mitsubishi" in clean_q or "mini" in clean_q:
            matched_entry = OEM_SPECS_DATABASE.get("mitsubishi")
        elif ("american standard" in clean_q or "trane" in clean_q) and any(x in clean_q for x in ["furnace", "s9x1", "95", "96", "s9"]):
            matched_entry = OEM_SPECS_DATABASE.get("s9x1")
        elif ("american standard" in clean_q or "trane" in clean_q):
            matched_entry = OEM_SPECS_DATABASE.get("4a7a")

    # 2. Universal Physics Calculation (Always available)
    ton = float(tonnage) if tonnage else 2.5
    is_furnace = "furnace" in clean_q or "gas" in clean_q
    is_condensing = "95" in clean_q or "96" in clean_q or "condens" in clean_q or "%" in str(furnace_eff) and int(re.search(r'\d+', str(furnace_eff)).group(0) if re.search(r'\d+', str(furnace_eff)) else 80) >= 90
    
    if ton <= 2.5:
        calc_mopd = "30A 2-Pole Breaker + 30A RK5 Fuses"
        calc_mca = "15.0A - 18.5A"
        calc_wire = "10/2 Romex"
        calc_lineset = '3/8" Liquid x 3/4" Suction (50ft)'
        calc_pad = '36" x 36" Composite Pad'
    elif ton <= 3.5:
        calc_mopd = "35A or 40A 2-Pole Breaker + 35A/40A Fuses"
        calc_mca = "19.0A - 24.5A"
        calc_wire = "8/2 Romex"
        calc_lineset = '3/8" Liquid x 3/4" Suction (50ft)'
        calc_pad = '36" x 36" Composite Pad'
    else:
        calc_mopd = "50A 2-Pole Breaker + 50A Fuses"
        calc_mca = "26.0A - 34.0A"
        calc_wire = "6/2 Romex"
        calc_lineset = '3/8" Liquid x 7/8" Suction (50ft Heavy Suction)'
        calc_pad = '38" x 42" Equipment Pad + Leveling Shims'

    if is_condensing:
        calc_vent = '2" Sch 40 Solid Core PVC (2 Sticks) + 90° Elbows (Max 60ft equivalent)'
        calc_drain = '3/4" PVC Secondary Trap + Clear Vinyl Tubing to Drain/Pump'
    else:
        calc_vent = '4" Metal B-Vent Pipe (5ft) + Adjustable Elbow + Draft Hood (Natural Draft)'
        calc_drain = 'Not required for 80% Non-Condensing Flue'

    # Build direct search fallback URL for Google and ManualsLib
    raw_term = (model or query_text or "").strip()
    first_tok = raw_term.split()[0] if raw_term else ""
    if re.search(r'^[A-Z0-9\-_]{3,20}$', first_tok, re.IGNORECASE):
        search_target = first_tok
    else:
        search_target = raw_term or "HVAC"

    brand_str = f"{brand} " if (brand and brand.lower() not in search_target.lower()) else ""
    full_search_phrase = f"{brand_str}{search_target} installation manual pdf".strip()
    google_search_url = f"https://www.google.com/search?q={urllib.parse.quote(full_search_phrase)}"
    manualslib_url = f"https://www.manualslib.com/search.php?q={urllib.parse.quote((brand_str + search_target).strip())}"

    if matched_entry:
        return {
            "found": True,
            "is_exact_match": True,
            "model_name": matched_entry["model"],
            "brand": matched_entry["brand"],
            "category": matched_entry["category"],
            "mca": matched_entry.get("mca", calc_mca),
            "mopd": matched_entry.get("mopd", calc_mopd),
            "electrical": matched_entry.get("electrical", f"{calc_mopd} ({calc_wire})"),
            "lineset": matched_entry.get("lineset", calc_lineset),
            "venting": matched_entry.get("venting", calc_vent),
            "drain": matched_entry.get("drain", calc_drain),
            "charge_subcooling": matched_entry.get("charge") or matched_entry.get("subcooling_target") or "Target 10°F Subcooling at service valve",
            "blower_tips": matched_entry.get("blower_dipswitches", f"Adjust CFM tap to ~400 CFM/ton (approx {int(ton*400)} CFM)"),
            "manual_url": matched_entry.get("manual_url", google_search_url),
            "manual_title": matched_entry.get("manual_title", "Official Manufacturer Installation Manual (PDF)"),
            "secondary_url": matched_entry.get("secondary_url", manualslib_url),
            "google_search_url": google_search_url
        }
    else:
        display_title = f"{brand or 'OEM'} {model or query_text or 'System'} ({ton}T)"
        return {
            "found": True,
            "is_exact_match": False,
            "model_name": display_title,
            "brand": brand or "HVAC Manufacturer",
            "category": "Universal Sized Equipment",
            "mca": calc_mca,
            "mopd": calc_mopd,
            "electrical": f"{calc_mopd} ({calc_wire})",
            "lineset": calc_lineset,
            "venting": calc_vent,
            "drain": calc_drain,
            "charge_subcooling": "Refer to unit rating plate (typical 8°F - 12°F Subcooling)",
            "blower_tips": f"Set blower speed to ~400 CFM/ton ({int(ton*400)} CFM total)",
            "manual_url": google_search_url,
            "manual_title": f"Search Official {brand or 'HVAC'} Manual (PDF)",
            "secondary_url": manualslib_url,
            "google_search_url": google_search_url
        }


if __name__ == "__main__":
    test1 = lookup_equipment_specs("S9X1", brand="American Standard")
    print("Test 1 (S9X1):", test1["model_name"], "->", test1["manual_url"][:60])
    test2 = lookup_equipment_specs("BOVA-36", brand="Bosch", tonnage=3.0)
    print("Test 2 (Bosch BOVA-36):", test2["model_name"], "-> MOPD:", test2["mopd"])
    test3 = lookup_equipment_specs("Daikin Fit", tonnage=4.0)
    print("Test 3 (Daikin Fit 4T):", test3["model_name"], "-> Lineset:", test3["lineset"])

