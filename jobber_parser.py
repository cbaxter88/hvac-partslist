import re
import subprocess
import os
from spec_manual_finder import lookup_equipment_specs

OCR_TOOL_PATH = "/Users/corybaxter/Desktop/AI/projects/HVAC-partslist/ocr_tool"

def run_vision_ocr(image_path):
    if not os.path.exists(OCR_TOOL_PATH):
        return ""
    try:
        cmd = [OCR_TOOL_PATH, image_path]
        res = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=20)
        return res.decode('utf-8', errors='replace')
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""

def parse_jobber_text(text):
    text_lower = text.lower()
    
    # 0. Job # and Customer Name extraction
    job_number = ""
    job_patterns = [
        r'(?:Job|Work\s*Order|Invoice|Quote|WO|Job\s*#)[:\s#]+([0-9]{3,8})\b',
        r'#\s*([0-9]{4,8})\b',
        r'\bJob\s+([0-9]{3,8})\b'
    ]
    for p in job_patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            job_number = m.group(1).strip()
            break

    customer_name = ""
    cust_patterns = [
        r'(?:Client|Customer|Name|Bill\s*To|Property)[:\s]+([A-Za-z0-9\s,\.\x27\-]{2,30})',
        r'(?:Job\s*(?:for|at))[:\s]+([A-Za-z0-9\s,\.\x27\-]{2,30})',
        r'\bfor\s+([A-Z][a-z]{2,20})\b'
    ]
    for p in cust_patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            c = m.group(1).strip().split('\n')[0]
            if len(c) >= 2 and not any(w in c.lower() for w in ['system', 'air', 'furnace', 'american', 'standard']):
                customer_name = c
                break

    if not customer_name:
        m_paren = re.search(r'\(([A-Z][a-z]{2,20})\)', text)
        if m_paren:
            customer_name = m_paren.group(1).strip()

    if job_number and customer_name:
        job_title = f"Job #{job_number} ({customer_name})"
    elif job_number:
        job_title = f"Job #{job_number}"
    elif customer_name:
        job_title = f"Job: {customer_name}"
    else:
        job_title = ""

    # 1. Brand detection
    brands = [
        "American Standard", "Trane", "Carrier", "Lennox", "Bryant", 
        "Rheem", "Ruud", "Goodman", "Daikin", "Mitsubishi", "Bosch", 
        "York", "Payne", "Amana", "Heil", "Tempstar", "RunTru", "Oxbox",
        "Coleman", "Armstrong", "Ducane", "Navien"
    ]
    detected_brand = ""
    for b in brands:
        if b.lower() in text_lower:
            detected_brand = b
            break
            
    # Model-specific brand inferences
    if not detected_brand:
        if "s9x1" in text_lower or "s8x1" in text_lower or "4a7a" in text_lower or "4ttr" in text_lower or "silver" in text_lower:
            detected_brand = "American Standard"
        elif "bova" in text_lower or "bva" in text_lower or "ids 2.0" in text_lower:
            detected_brand = "Bosch"
        elif "59tp" in text_lower or "24sca" in text_lower or "infinity" in text_lower or "puron" in text_lower:
            detected_brand = "Carrier"
        elif "el296" in text_lower or "ml196" in text_lower or "ml14" in text_lower:
            detected_brand = "Lennox"
        elif "r96v" in text_lower or "ra14" in text_lower:
            detected_brand = "Rheem"
        elif "gm9c" in text_lower or "gsx14" in text_lower:
            detected_brand = "Goodman"
        elif "puz" in text_lower or "msz" in text_lower:
            detected_brand = "Mitsubishi"
        else:
            detected_brand = "HVAC System"
            
    # 2. System Type detection
    # Check explicit "furnace only" or "ac only"
    has_furnace_only = bool(re.search(r'\bfurnace\s*only\b', text_lower))
    has_ac_only = bool(re.search(r'\b(ac|air\s*condition(er|ing)?)\s*only\b', text_lower))

    is_minisplit = bool(re.search(r'\b(mini[- ]?split|ductless)\b', text_lower))
    is_heatpump = bool(re.search(r'\b(heat pump|heatpump|hp)\b', text_lower))
    is_furnace = bool(re.search(r'\b(furnace|gas heat)\b', text_lower))
    is_ac = bool(re.search(r'\b(ac|air condition(er|ing)?|condenser)\b', text_lower))

    if has_furnace_only:
        is_ac = False
        is_heatpump = False
        is_minisplit = False
        system_type = "furnace-only"
        type_title = "Furnace Only"
    elif has_ac_only:
        is_furnace = False
        system_type = "ac-only"
        type_title = "AC Only (Condenser & Coil)"
    elif is_minisplit:
        system_type = "mini-split"
        type_title = "Mini-Split Heat Pump"
    elif is_heatpump:
        system_type = "heatpump"
        type_title = "Heat Pump System"
    elif is_ac and is_furnace:
        system_type = "full-system"
        type_title = "Full System AC & Furnace"
    elif is_ac:
        system_type = "ac-only"
        type_title = "AC Only (Condenser & Coil)"
    elif is_furnace:
        system_type = "furnace-only"
        type_title = "Furnace Only"
    else:
        system_type = "full-system"
        type_title = "Full System AC & Furnace"

    # 3. Tonnage detection
    tonnage = 2.5 # default fallback
    ton_match = re.search(r'(\d+(?:\.\d+)?)\s*[-_ ]*\s*ton\b', text_lower)
    if not ton_match:
        ton_match = re.search(r'\b(\d+(?:\.\d+)?)\s*[-_ ]*\s*t\b', text_lower)

    if ton_match:
        try:
            val = float(ton_match.group(1))
            if 1.0 <= val <= 10.0:
                tonnage = val
        except:
            tonnage = 2.5
    else:
        # Check BTU equivalent in AC context only (avoid matching 60k/80k furnace BTU)
        ac_context_match = re.search(r'(?:ac|air|condenser|heat pump|hp).*?\b(18|24|30|36|42|48|60)\s*k\b', text_lower)
        if ac_context_match:
            ton_map = {"18": 1.5, "24": 2.0, "30": 2.5, "36": 3.0, "42": 3.5, "48": 4.0, "60": 5.0}
            tonnage = ton_map.get(ac_context_match.group(1), 2.5)

    # 4. SEER detection
    seer_match = re.search(r'(\d+(?:\.\d+)?)\s*[- ]?seer(?:2)?', text_lower)
    seer = (seer_match.group(1) + ("-SEER2" if "seer2" in text_lower else "-SEER")) if seer_match else ("13-SEER2" if "seer2" in text_lower else "14-SEER")

    # 5. Furnace specs (BTU & Efficiency)
    furnace_btu = "60k"
    furnace_eff = "80%"
    is_condensing_90plus = False

    if is_furnace:
        f_btu_match = re.search(r'(?:furnace|gas).*?(\d{2,3})\s*k', text_lower)
        if not f_btu_match:
            f_btu_match = re.search(r'\b(\d{2,3})\s*k\b', text_lower)
        if f_btu_match:
            furnace_btu = f_btu_match.group(1) + "k"
        
        eff_match = re.search(r'(\d{2})%', text_lower)
        if eff_match:
            eff_num = int(eff_match.group(1))
            if eff_num >= 90:
                is_condensing_90plus = True
                furnace_eff = f"{eff_num}% Condensing"
            else:
                furnace_eff = f"{eff_num}% Standard"
        elif "95%" in text_lower or "96%" in text_lower or "s9x1" in text_lower:
            is_condensing_90plus = True
            furnace_eff = "95% Condensing"

    # 6. Lineset sizing rules
    if system_type == "furnace-only":
        lineset_size = "None (Furnace Only)"
        lineset_note = "No outdoor lineset needed"
    elif tonnage <= 2.0:
        lineset_size = '3/8" x 3/4" x 50ft'
        lineset_note = f'Matched to {tonnage}-Ton'
    elif tonnage <= 3.5:
        lineset_size = '3/8" x 3/4" x 50ft'
        lineset_note = f'Matched to {tonnage}-Ton'
    else: # 4.0 - 5.0 Ton
        lineset_size = '3/8" x 7/8" x 50ft'
        lineset_note = f'Matched to {tonnage}-Ton (Heavy 7/8" Suction)'

    # 7. Venting rules
    if is_furnace:
        if is_condensing_90plus:
            venting_spec = '2" Sch 40 PVC (2 sticks) + 90s'
            venting_note = f'{furnace_eff} (No Metal B-Vent)'
        else:
            venting_spec = '4" Metal B-Vent pipe + Draft Hood'
            venting_note = f'{furnace_eff} Non-Condensing Natural Draft'
    else:
        venting_spec = 'None (Electric Heat Pump / AC only)'
        venting_note = 'No combustion venting required'

    # 8. Electrical sizing rules
    if system_type == "furnace-only":
        elec_spec = '15A 1-Pole Breaker (120V) + SSU Switch'
        elec_note = '120V Branch circuit for furnace ignition & blower'
    elif tonnage <= 2.5:
        elec_spec = '30A 2-Pole Breaker + 10/2 Romex'
        elec_note = f'MOPD: 30A Max for {tonnage}-Ton'
    elif tonnage <= 3.5:
        elec_spec = '35A or 40A 2-Pole Breaker + 8/2 Romex'
        elec_note = f'MOPD: 35-40A for {tonnage}-Ton'
    else:
        elec_spec = '50A 2-Pole Breaker + 6/2 Romex'
        elec_note = f'MOPD: 50A for {tonnage}-Ton'

    # 9. Pad sizing
    if system_type == "furnace-only":
        pad_spec = "None (Furnace Only)"
        pad_note = "No outdoor pad needed"
    elif tonnage <= 2.5:
        pad_spec = '36" x 36" DiversiTech Composite Pad'
        pad_note = f'Standard base for {tonnage}-Ton'
    else:
        pad_spec = '38" x 42" Equipment Pad + Shims'
        pad_note = f'Large footprint for {tonnage}-Ton'

    # 10. Tearout / Removal
    has_removal = "removal of old" in text_lower or "removal" in text_lower or "tear out" in text_lower or "tearout" in text_lower
    
    # 11. New Lineset vs Flush
    has_new_lines = "new refrigerant line" in text_lower or "new lineset" in text_lower or "new line" in text_lower
    reusing_lineset = "reuse" in text_lower or "flush" in text_lower

    # 12. Model Extraction & Auto-Link Verified Specs + OEM Manuals
    furnace_model = ""
    if "s9x1" in text_lower or "s9x" in text_lower:
        furnace_model = "S9X1"
    elif "s8x1" in text_lower or "s8x" in text_lower:
        furnace_model = "S8X1"
    elif "59tp6" in text_lower or "59tp" in text_lower:
        furnace_model = "59TP6"
    elif "58sb0" in text_lower or "58sb" in text_lower:
        furnace_model = "58SB0"
    elif "el296v" in text_lower or "el296" in text_lower:
        furnace_model = "EL296V"
    elif "ml196e" in text_lower or "ml196" in text_lower:
        furnace_model = "ML196E"
    elif "gm9c96" in text_lower or "gm9c" in text_lower:
        furnace_model = "GM9C96"
    elif "gm9s96" in text_lower or "gm9s" in text_lower:
        furnace_model = "GM9S96"
    elif "r96v" in text_lower or "r96" in text_lower:
        furnace_model = "R96V"
    elif "r801" in text_lower:
        furnace_model = "R801V"
    if not furnace_model and is_furnace:
        f_stop = {"STAGE", "INPUT", "SINGLE", "NATURAL", "PROPANE", "SYSTEM", "FULL", "FURNACE", "COIL", "INCLUDES", "INDOOR", "OUTDOOR", "BURNER", "GAS", "HEAT", "EFF"}
        f_m = re.search(r'(?:furnace|gas heat).*?\b([A-Za-z0-9]{4,10})\b', text_lower)
        if f_m and f_m.group(1).upper() not in f_stop and re.search(r'\d', f_m.group(1)):
            furnace_model = f_m.group(1).upper()
        elif detected_brand in ["American Standard", "Trane"]:
            furnace_model = "S9X1" if is_condensing_90plus else "S8X1"
        elif detected_brand == "Carrier":
            furnace_model = "59TP6" if is_condensing_90plus else "58SB0"
        elif detected_brand == "Lennox":
            furnace_model = "EL296V"
        elif detected_brand in ["Goodman", "Daikin"]:
            furnace_model = "GM9C96"
        elif detected_brand in ["Rheem", "Ruud"]:
            furnace_model = "R96V"

    ac_model = ""
    if "4a7a" in text_lower or "4a7" in text_lower:
        ac_model = "4A7A"
    elif "4ttr" in text_lower:
        ac_model = "4TTR4"
    elif "4twx" in text_lower or "4twr" in text_lower:
        ac_model = "4TWR6"
    elif "bova" in text_lower:
        ac_model = "BOVA-36" if tonnage <= 3.0 else "BOVA-60"
    elif "24sca5" in text_lower or "24sca" in text_lower:
        ac_model = "24SCA5"
    elif "24vna9" in text_lower or "24vna" in text_lower:
        ac_model = "24VNA9"
    elif "gsx14" in text_lower or "gsx16" in text_lower or "gsx" in text_lower:
        ac_model = "GSX14"
    elif "ra14" in text_lower or "ra13" in text_lower:
        ac_model = "RA14"
    elif "ml14xc1" in text_lower or "ml14" in text_lower:
        ac_model = "ML14XC1"
    
    if not ac_model and (is_ac or is_heatpump):
        ac_stop = {"STAGE", "SEER", "SEER2", "TON", "TONS", "SYSTEM", "FURNACE", "COIL", "INCLUDES", "INDOOR", "OUTDOOR", "FULL", "AIR", "CONDITIONER", "CONDITIONING", "NEW", "HEAT", "PUMP", "UNIT"}
        ac_m = re.search(r'(?:ac|condenser|air condition(?:er|ing)?).*?\b([A-Za-z0-9]{4,10})\b', text_lower)
        if ac_m and ac_m.group(1).upper() not in ac_stop and re.search(r'\d', ac_m.group(1)):
            ac_model = ac_m.group(1).upper()
        elif detected_brand == "American Standard":
            ac_model = "4A7A"
        elif detected_brand == "Trane":
            ac_model = "4TTR4"
        elif detected_brand == "Carrier":
            ac_model = "24SCA5"
        elif detected_brand == "Bosch":
            ac_model = "BOVA-36" if tonnage <= 3.0 else "BOVA-60"
        elif detected_brand == "Goodman":
            ac_model = "GSX14"
        elif detected_brand in ["Rheem", "Ruud"]:
            ac_model = "RA14"
        elif detected_brand == "Lennox":
            ac_model = "ML14XC1"

    coil_model = ""
    if "4pxc" in text_lower or "4px" in text_lower:
        coil_model = "4PXC"
    elif "cnpv" in text_lower:
        coil_model = "CNPV"
    elif "cx35" in text_lower:
        coil_model = "CX35"
    elif "chpf" in text_lower:
        coil_model = "CHPF"
    elif detected_brand in ["American Standard", "Trane"]:
        coil_model = "4PXC"
    elif detected_brand == "Carrier":
        coil_model = "CNPV"
    elif detected_brand == "Lennox":
        coil_model = "CX35"
    elif detected_brand in ["Goodman", "Daikin"]:
        coil_model = "CHPF"

    # Pre-lookup verified technical specs and direct PDF manuals
    furnace_specs = lookup_equipment_specs(furnace_model or "Furnace", brand=detected_brand, model=furnace_model, furnace_btu=furnace_btu, furnace_eff=furnace_eff) if is_furnace else {}
    ac_specs = lookup_equipment_specs(ac_model or "Condenser", brand=detected_brand, model=ac_model, tonnage=tonnage) if (is_ac or is_heatpump) else {}
    coil_specs = lookup_equipment_specs(coil_model or "Coil", brand=detected_brand, model=coil_model, tonnage=tonnage) if (is_ac or is_heatpump) else {}

    # 13. Build Modular Equipment List
    equipment = []
    brand_prefix = detected_brand if detected_brand != "HVAC System" else ""
    
    if system_type == "furnace-only":
        f_name = f"{brand_prefix} {furnace_btu} {furnace_eff} {furnace_model} Furnace" if furnace_model else f"{brand_prefix} {furnace_btu} {furnace_eff} Furnace".strip()
        equipment.append({
            "id": "eq-furnace",
            "name": f_name or f"{furnace_btu} {furnace_eff} Gas Furnace",
            "model_code": furnace_model,
            "qty": "1 Unit",
            "badge": furnace_eff,
            "desc": f"Single-stage gas furnace • {furnace_btu} input • 120V",
            "model_search": furnace_model or f_name,
            "specs": furnace_specs,
            "manual_url": furnace_specs.get("manual_url", ""),
            "manual_title": furnace_specs.get("manual_title", ""),
            "secondary_url": furnace_specs.get("secondary_url", ""),
            "google_search_url": furnace_specs.get("google_search_url", "")
        })
    elif system_type == "ac-only":
        ac_name = f"{brand_prefix} {tonnage}-Ton Condenser ({ac_model} • {seer})" if ac_model else f"{brand_prefix} {tonnage}-Ton Condenser ({seer})".strip()
        c_name = f"{brand_prefix} {tonnage}-Ton Cased Coil ({coil_model})" if coil_model else f"{brand_prefix} {tonnage}-Ton Cased Coil".strip()
        equipment.append({
            "id": "eq-ac",
            "name": ac_name,
            "model_code": ac_model,
            "qty": "1 Unit",
            "badge": f"{tonnage}T Sizing",
            "desc": f"Outdoor AC Condenser • Factory charged • {seer}",
            "model_search": ac_model or ac_name,
            "specs": ac_specs,
            "manual_url": ac_specs.get("manual_url", ""),
            "manual_title": ac_specs.get("manual_title", ""),
            "secondary_url": ac_specs.get("secondary_url", ""),
            "google_search_url": ac_specs.get("google_search_url", "")
        })
        equipment.append({
            "id": "eq-coil",
            "name": c_name,
            "model_code": coil_model,
            "qty": "1 Unit",
            "badge": "Factory TXV",
            "desc": "Indoor cased evaporator coil",
            "model_search": coil_model or c_name,
            "specs": coil_specs,
            "manual_url": coil_specs.get("manual_url", ""),
            "manual_title": coil_specs.get("manual_title", ""),
            "secondary_url": coil_specs.get("secondary_url", ""),
            "google_search_url": coil_specs.get("google_search_url", "")
        })
    elif system_type == "heatpump":
        hp_name = f"{brand_prefix} {tonnage}-Ton Heat Pump Condenser ({ac_model} • {seer})" if ac_model else f"{brand_prefix} {tonnage}-Ton Heat Pump Condenser ({seer})".strip()
        equipment.append({
            "id": "eq-hp",
            "name": hp_name,
            "model_code": ac_model,
            "qty": "1 Unit",
            "badge": f"{tonnage}T Heat Pump",
            "desc": f"Inverter / Heat Pump outdoor unit • {seer}",
            "model_search": ac_model or hp_name,
            "specs": ac_specs,
            "manual_url": ac_specs.get("manual_url", ""),
            "manual_title": ac_specs.get("manual_title", ""),
            "secondary_url": ac_specs.get("secondary_url", ""),
            "google_search_url": ac_specs.get("google_search_url", "")
        })
        if is_furnace:
            c_name = f"{brand_prefix} {tonnage}-Ton Cased Coil ({coil_model})" if coil_model else f"{brand_prefix} {tonnage}-Ton Cased Coil".strip()
            f_name = f"{brand_prefix} {furnace_btu} {furnace_eff} {furnace_model} Furnace (Dual Fuel)" if furnace_model else f"{brand_prefix} {furnace_btu} {furnace_eff} Furnace (Dual Fuel)".strip()
            equipment.append({
                "id": "eq-coil",
                "name": c_name,
                "model_code": coil_model,
                "qty": "1 Unit",
                "badge": "Heat Pump TXV",
                "desc": "Indoor cased coil for dual-fuel system",
                "model_search": coil_model or c_name,
                "specs": coil_specs,
                "manual_url": coil_specs.get("manual_url", ""),
                "manual_title": coil_specs.get("manual_title", "")
            })
            equipment.append({
                "id": "eq-furnace",
                "name": f_name,
                "model_code": furnace_model,
                "qty": "1 Unit",
                "badge": furnace_eff,
                "desc": "Auxiliary gas furnace backup",
                "model_search": furnace_model or f_name,
                "specs": furnace_specs,
                "manual_url": furnace_specs.get("manual_url", ""),
                "manual_title": furnace_specs.get("manual_title", "")
            })
        else:
            ah_name = f"{brand_prefix} {tonnage}-Ton Multi-Position Air Handler"
            equipment.append({
                "id": "eq-air-handler",
                "name": ah_name,
                "qty": "1 Unit",
                "badge": "ECM Blower",
                "desc": "Indoor electric air handler unit",
                "model_search": ah_name
            })
    elif system_type == "mini-split":
        equipment.append({
            "id": "eq-minisplit-od",
            "name": f"{brand_prefix} {tonnage}-Ton Ductless Inverter Heat Pump",
            "model_code": "MSZ/MUZ",
            "qty": "1 Unit",
            "badge": f"{tonnage}T Inverter",
            "desc": "Variable-speed outdoor ductless condenser",
            "model_search": "Mitsubishi",
            "specs": ac_specs,
            "manual_url": ac_specs.get("manual_url", "")
        })
        equipment.append({
            "id": "eq-minisplit-id",
            "name": f"{brand_prefix} High-Wall Ductless Indoor Air Handler",
            "qty": "1 Unit",
            "badge": "Wall Mount",
            "desc": "Whisper-quiet indoor evaporator head + remote",
            "model_search": f"{brand_prefix} Ductless Indoor Unit".strip()
        })
    else: # Full System
        condenser_title = f"{brand_prefix} {tonnage}-Ton Condenser ({ac_model} • {seer})" if ac_model else f"{brand_prefix} {tonnage}-Ton Condenser ({seer})".strip()
        furnace_title = f"{brand_prefix} {furnace_btu} {furnace_eff} {furnace_model} Furnace" if furnace_model else f"{brand_prefix} {furnace_btu} {furnace_eff} Furnace".strip()
        coil_title = f"{brand_prefix} {tonnage}-Ton Cased Coil ({coil_model})" if coil_model else f"{brand_prefix} {tonnage}-Ton Cased Coil".strip()
        
        equipment.append({
            "id": "eq-ac",
            "name": condenser_title,
            "model_code": ac_model,
            "qty": "1 Unit",
            "badge": f"{tonnage}T Sizing",
            "desc": f"Outdoor AC Condenser • Factory charged • {seer}",
            "model_search": ac_model or condenser_title,
            "specs": ac_specs,
            "manual_url": ac_specs.get("manual_url", ""),
            "manual_title": ac_specs.get("manual_title", ""),
            "secondary_url": ac_specs.get("secondary_url", ""),
            "google_search_url": ac_specs.get("google_search_url", "")
        })
        equipment.append({
            "id": "eq-furnace",
            "name": furnace_title,
            "model_code": furnace_model,
            "qty": "1 Unit",
            "badge": furnace_eff,
            "desc": f"Single-stage gas furnace • {furnace_btu} input",
            "model_search": furnace_model or furnace_title,
            "specs": furnace_specs,
            "manual_url": furnace_specs.get("manual_url", ""),
            "manual_title": furnace_specs.get("manual_title", ""),
            "secondary_url": furnace_specs.get("secondary_url", ""),
            "google_search_url": furnace_specs.get("google_search_url", "")
        })
        equipment.append({
            "id": "eq-coil",
            "name": coil_title,
            "model_code": coil_model,
            "qty": "1 Unit",
            "badge": "Factory TXV",
            "desc": "Indoor cased evaporator coil",
            "model_search": coil_model or coil_title,
            "specs": coil_specs,
            "manual_url": coil_specs.get("manual_url", ""),
            "manual_title": coil_specs.get("manual_title", ""),
            "secondary_url": coil_specs.get("secondary_url", ""),
            "google_search_url": coil_specs.get("google_search_url", "")
        })

    # Subtitle build
    sub_parts = []
    if system_type == "furnace-only":
        f_str = f"Furnace {furnace_btu} {furnace_eff}"
        if "s9x1" in text_lower:
            f_str += " S9X1"
        sub_parts.append(f_str)
    elif system_type == "ac-only":
        sub_parts.append(f"AC {seer} {tonnage}-Ton")
    elif system_type == "heatpump":
        sub_parts.append(f"Heat Pump {seer} {tonnage}-Ton")
        if is_furnace:
            sub_parts.append(f"Furnace {furnace_btu} {furnace_eff}")
    elif system_type == "mini-split":
        sub_parts.append(f"Mini-Split {tonnage}-Ton Inverter")
    else:
        sub_parts.append(f"AC {seer} {tonnage}-Ton")
        f_str = f"Furnace {furnace_btu} {furnace_eff}"
        if "s9x1" in text_lower:
            f_str += " S9X1"
        sub_parts.append(f_str)

    title = f"{detected_brand} {type_title}".strip() if detected_brand != "HVAC System" else type_title
    sub = " • ".join(sub_parts) if sub_parts else f"{tonnage}-Ton System"

    return {
        "job_number": job_number,
        "customer_name": customer_name,
        "job_title": job_title,
        "title": title,
        "subtitle": sub,
        "profile": system_type,
        "brand": detected_brand,
        "tonnage": tonnage,
        "has_new_lines": has_new_lines,
        "reusing_lineset": reusing_lineset,
        "has_removal": has_removal,
        "is_condensing_90plus": is_condensing_90plus,
        "furnace_btu": furnace_btu,
        "furnace_eff": furnace_eff,
        "seer": seer,
        "is_furnace": is_furnace,
        "is_ac": is_ac,
        "is_heatpump": is_heatpump,
        "is_minisplit": is_minisplit,
        "equipment": equipment,
        "specs": {
            "lineset": lineset_size,
            "lineset_note": lineset_note,
            "venting": venting_spec,
            "venting_note": venting_note,
            "electrical": elec_spec,
            "electrical_note": elec_note,
            "pad": pad_spec,
            "pad_note": pad_note,
            "drainage": '3/4" Schedule 40 PVC + SS2 Float Switch' if (is_ac or is_heatpump) else '3/4" Schedule 40 PVC Condensate Trap',
            "drainage_note": "Furnace secondary trap + evaporator overflow protection" if (is_ac or is_heatpump) else "Furnace flue condensate trap",
            "tearout": "Recovery Machine + A2L Tank + Appliance Dolly" if has_removal else "Standard Dolly",
            "tearout_note": '"Removal of old equipment" specified' if has_removal else "Standard install"
        },
        "raw_text_preview": text[:400]
    }
