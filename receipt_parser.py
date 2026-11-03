#!/usr/bin/env python3
import re
import os
from jobber_parser import run_vision_ocr, OCR_TOOL_PATH

SIMPLIFIED_RULES = [
    # Custom Job Transitions / Filters
    {
        'pattern': r'16\s*[x×]\s*25.*(?:to\s*)?24\s*[x×]\s*10.*RETURN.*ELBOW|TTS1625',
        'name': '16"x25" to 24"x10" Return Air Drop Elbow',
        'type': 'job_specific',
        'bin': 'Job Staging',
        'pkg': 'Pre-fabricated galvanized transition elbow'
    },
    {
        'pattern': r'F100F1625|CLEANER\s*AIR\s*MEDIA\s*16\s*[xX]\s*25|L94-053',
        'name': '16"x25" Honeywell Media Air Filter (F100F)',
        'type': 'job_specific',
        'bin': 'Job Staging',
        'pkg': 'Cardboard boxed 16x25x4 filter media'
    },
    {
        'pattern': r'36\s*[x×]\s*96.*26GA.*GALVANIZED|FLAT\s*SHEET',
        'name': '26-Gauge Galvanized Sheet Metal (36" x 96")',
        'type': 'job_specific',
        'bin': 'Van Sheet Rack',
        'pkg': 'Full 3ft x 8ft flat metal sheet'
    },
    # Gas Piping (1/2" Black Iron)
    {
        'pattern': r'1/2"?\s*BLACK.*(?:90\s*deg\s*)?ELBOW|312E90-12',
        'name': '1/2" Black Iron 90° Elbow',
        'type': 'truck_restock',
        'bin': 'Gas Piping Bin',
        'pkg': 'Heavy black malleable iron fitting'
    },
    {
        'pattern': r'1/2"?\s*BLACK.*(?:BANDED\s*)?COUPLING|312CO-12',
        'name': '1/2" Black Iron Banded Coupling',
        'type': 'truck_restock',
        'bin': 'Gas Piping Bin',
        'pkg': 'Heavy black iron threaded coupling'
    },
    {
        'pattern': r'1/2"?\s*BLACK.*CAP|310CA-12',
        'name': '1/2" Black Iron Pipe Cap',
        'type': 'truck_restock',
        'bin': 'Gas Piping Bin',
        'pkg': 'Black iron female pipe cap'
    },
    {
        'pattern': r'1/2"?\s*BLACK.*TEE|312T-12',
        'name': '1/2" Black Iron Pipe Tee',
        'type': 'truck_restock',
        'bin': 'Gas Piping Bin',
        'pkg': 'Black iron 3-way threaded tee'
    },
    {
        'pattern': r'1/2"?\s*BLACK.*UNION|310U-12',
        'name': '1/2" Black Iron Ground Joint Union',
        'type': 'truck_restock',
        'bin': 'Gas Piping Bin',
        'pkg': '3-piece ground joint black iron union'
    },
    {
        'pattern': r'1/2\s*x\s*12"?\s*BLACK.*NIPPLE|30212X12',
        'name': '1/2" x 12" Black Iron Pipe Nipple',
        'type': 'truck_restock',
        'bin': 'Gas Piping Bin',
        'pkg': '12-inch threaded black iron nipple'
    },
    # PVC Drain & Venting
    {
        'pattern': r'3/4"?\s*PVC.*ELBOW\s*SxS|406-007',
        'name': '3/4" PVC 90° Elbow (Slip x Slip)',
        'type': 'truck_restock',
        'bin': 'PVC Drain Kit',
        'pkg': 'Schedule 40 PVC fitting'
    },
    {
        'pattern': r'3/4"?\s*PVC.*STREET\s*ELBOW|409-007',
        'name': '3/4" PVC Street 90° Elbow (Slip x Spigot)',
        'type': 'truck_restock',
        'bin': 'PVC Drain Kit',
        'pkg': 'Schedule 40 PVC street elbow'
    },
    {
        'pattern': r'3/4"?\s*PVC.*MALE\s*ADAPT|436-007',
        'name': '3/4" PVC Male Adapter (MIPT x Slip)',
        'type': 'truck_restock',
        'bin': 'PVC Drain Kit',
        'pkg': 'Schedule 40 male threaded adapter'
    },
    {
        'pattern': r'3/4"?\s*PVC.*TEE\s*SxSxS|401-007',
        'name': '3/4" PVC Tee (Slip x Slip x Slip)',
        'type': 'truck_restock',
        'bin': 'PVC Drain Kit',
        'pkg': 'Schedule 40 PVC tee'
    },
    {
        'pattern': r'RECTORSEAL.*ARCTIC.*616|COLD\s*WEATHER\s*PVC\s*CEMENT|55919',
        'name': 'RectorSeal Arctic 616 Cold Weather PVC Cement (16oz)',
        'type': 'truck_restock',
        'bin': 'PVC Drain Kit',
        'pkg': '1-pint blue/white metal can with dauber'
    },
    # Fasteners & Consumables
    {
        'pattern': r'MALCO.*(?:500pk|BT133T|BIT\s*-?TIP|8-18X3/4)',
        'name': 'Malco #8 x 3/4" Zip Screws (500 Box)',
        'type': 'truck_restock',
        'bin': 'Hardware & Fasteners',
        'pkg': 'Red/white 500-count cardboard box'
    },
    {
        'pattern': r'CLEAR\s*SILICONE|08011|RTV\s*SILICONE',
        'name': 'Clear 100% RTV Silicone (10.3 oz Tube)',
        'type': 'truck_restock',
        'bin': 'Hardware & Fasteners',
        'pkg': '10.3 oz cartridge tube'
    },
    # Torches & Gases
    {
        'pattern': r'FULL\s*TANK\s*MC.*ACETYLENE|10ACIC',
        'name': 'Full MC Acetylene Tank (10CF Swap)',
        'type': 'truck_restock',
        'bin': 'Torches & Tanks',
        'pkg': '10 cu ft red/grey steel cylinder'
    },
    {
        'pattern': r'EMPTY\s*TANK\s*MC.*ACETYLENE|\*?\*?RTN.*ACETYLENE',
        'name': 'Empty MC Acetylene Tank Return (Credit)',
        'type': 'truck_restock',
        'bin': 'Torches & Tanks',
        'pkg': 'Empty tank deposit refund'
    },
    # Electrical
    {
        'pattern': r'HOM230|Q230|2-POLE.*(?:30|40)A',
        'name': '30A 2-Pole Circuit Breaker',
        'type': 'truck_restock',
        'bin': 'High Voltage Bin',
        'pkg': 'Molded case 2-pole breaker clamshell'
    },
    {
        'pattern': r'DDS-60U|DISCONNECT.*60A',
        'name': '60A Non-Fused Disconnect Box',
        'type': 'truck_restock',
        'bin': 'High Voltage Bin',
        'pkg': 'NEMA 3R gray metal enclosure'
    },
    {
        'pattern': r'WHIP.*(?:1/2|6ft|LIQUID-TIGHT)',
        'name': '1/2" x 6ft Liquid-Tight Electrical Whip',
        'type': 'truck_restock',
        'bin': 'High Voltage Bin',
        'pkg': 'Pre-wired flexible conduit kit'
    }
]

def simplify_line_item(raw_desc):
    clean_desc = raw_desc.replace('\n', ' ').strip()
    for rule in SIMPLIFIED_RULES:
        if re.search(rule['pattern'], clean_desc, re.IGNORECASE):
            return {
                'simplified_name': rule['name'],
                'type': rule['type'],
                'target_bin': rule['bin'],
                'package_desc': rule['pkg']
            }
    
    # Generic fallback cleaner
    simplified = clean_desc
    # Strip random location / code prefixes like SW0102J R54-118
    simplified = re.sub(r'^[A-Z0-9]{5,7}\s+[A-Z0-9-]{5,8}\s+', '', simplified)
    simplified = re.sub(r'\s+', ' ', simplified).strip()
    return {
        'simplified_name': simplified,
        'type': 'truck_restock',
        'target_bin': 'General Truck Stock',
        'package_desc': 'Standard supply packaging'
    }

def parse_receipt_text(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    supplier = "Johnstone Supply" if "johnstone" in text.lower() or "jswmi" in text.lower() else "Supply House"
    
    # Order / Invoice #
    inv_match = re.search(r'(?:order\s*number|ship\s*ticket|invoice)[^A-Z0-9]*([A-Z0-9\.\-]+)', text, re.IGNORECASE)
    if not inv_match:
        inv_match = re.search(r'\b([S0-9]{8,12}\.[0-9]{3})\b', text)
    inv_num = inv_match.group(1) if inv_match else "#JS-" + str(abs(hash(text)) % 90000 + 10000)
    
    # Customer PO / Job Name
    po_match = re.search(r'(?:customer\s*po|po\s*\/|release\s*number)[^A-Za-z0-9]*([A-Za-z0-9\-_ ]{3,20})', text, re.IGNORECASE)
    job_name = po_match.group(1).strip() if po_match else "General Truck Stock"
    if "c.o.d" in job_name.lower() or "ordered" in job_name.lower():
        # Look for standalone Pitcher
        if "pitcher" in text.lower():
            job_name = "PITCHER"
        else:
            job_name = "Jobber Active Job"

    # Total Amount
    total_match = re.search(r'(?:charge\s*amount|total|subtotal)[^$0-9]*\$?\s*([0-9]+\.[0-9]{2})', text, re.IGNORECASE)
    total_cost = f"${total_match.group(1)}" if total_match else "$0.00"

    items = []
    
    # Multi-line chunking: scan for lines that have pricing or quantities
    # Typical line: [QTY] [SKU] [DESC...] [PRICE] [EXTENDED]
    full_text_flat = " ".join(lines)
    
    # Split by item rows (e.g. "1 ea", "5ea", "2ea", "- 1 ca", "1 pk")
    item_chunks = re.split(r'(?=\b(?:\d+\s*(?:ea|pk|ft|rl|bx|can|tub)|-\s*\d+\s*(?:ea|ca|pk))\b)', full_text_flat, flags=re.IGNORECASE)
    
    idx = 1
    for chunk in item_chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        
        # Check if chunk contains a price
        price_match = re.findall(r'(-?\d+\.\d{2})', chunk)
        if not price_match:
            continue
            
        qty_match = re.match(r'^(-?\s*\d+\s*(?:ea|ca|pk|ft|rl|bx|can|tub)?)', chunk, re.IGNORECASE)
        qty = qty_match.group(1).strip() if qty_match else "1 ea"
        
        # Extended price is usually last or second to last
        ext_price = f"${price_match[-1]}"
        unit_price = f"${price_match[-2]}" if len(price_match) >= 2 else ext_price
        
        # Clean description
        desc_part = chunk
        if qty_match:
            desc_part = desc_part[len(qty_match.group(0)):].strip()
        # Remove trailing prices
        desc_part = re.sub(r'(-?\d+\.\d{2,3}\s*)+$', '', desc_part).strip()
        
        # Skip shipping instructions or terms
        if "shipping instructions" in desc_part.lower() or "counter.sales" in desc_part.lower() or len(desc_part) < 4:
            continue
            
        # Extract SKU if present
        sku_match = re.search(r'\b([A-Z0-9]{5,8}(?:-[A-Z0-9]+)?)\b', desc_part)
        sku = sku_match.group(1) if sku_match else "MISC-ITEM"
        
        meta = simplify_line_item(desc_part)
        
        items.append({
            'id': f'item-{idx}',
            'sku': sku,
            'raw_desc': desc_part,
            'simplified_name': meta['simplified_name'],
            'qty': qty,
            'price': ext_price,
            'unit_price': unit_price,
            'type': meta['type'],
            'target_bin': meta['target_bin'],
            'package_desc': meta['package_desc']
        })
        idx += 1

    return {
        'supplier': supplier,
        'inv_num': inv_num,
        'job_name': job_name,
        'total_cost': total_cost,
        'items': items
    }

