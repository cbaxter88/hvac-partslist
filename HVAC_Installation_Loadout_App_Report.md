# HVAC Installation Loadout & Inventory System
## Finalized Operational Architecture & Field Deployment Guide

**Document Version:** 2.0.0 (Finalized Specification)  
**Target Device:** Mobile (iPhone Safari PWA / Native Web App)  
**Storage Architecture:** 100% Offline-First (`localStorage` + In-Memory Cache)  
**File Location:** `/Users/corybaxter/Desktop/AI/projects/HVAC-partslist/HVAC_Installation_Loadout_App_Report.md`  
**Web App Location:** `/Users/corybaxter/Desktop/AI/projects/HVAC-partslist/index.html`

---

## 1. System Overview & Core Philosophy

This system is engineered specifically for residential and light-commercial HVAC replacement crews to completely eliminate **unplanned supply house runs** during an install.

### Key Operational Rules:
1. **The "Two-Bucket" Inventory Rule:**
   * **Bucket 1 (High-Value Units & Major Parts):** Disconnects, whips, line sets, float switches, thermostats, pads, equipment. Tracked by unit count. Auto-deducted at the end of the day based on the job recipe.
   * **Bucket 2 (Bulk Consumables):** Zip screws, wire nuts, zip ties, PVC glue, electrical tape, mastic. Never counted by piece. Tracked purely by **Traffic Light Status** (🟢 Full / 🟡 Low / 🔴 Empty).
2. **100% Offline-First Reliability:**
   * Operates seamlessly without cellular or Wi-Fi in basements, rural sites, and metal warehouse bays.
   * All images, checklists, gotcha tips, and truck inventory data are stored locally on the iPhone.
3. **Hybrid Site-Condition Tagging:**
   * Takes photo inputs from the iPhone Camera or Photo Library (sent by comfort advisors/sales).
   * Works 100% offline via quick 1-tap site condition tags (`+ Concrete Wall`, `+ Vinyl Siding`, `+ Reusing Line Set`) to inject specialty bits, anchors, and flush kits.
4. **Leftover / Return Tracking:**
   * Prevents false inventory depletion by allowing installers to flag unused parts before completing the job.

---

## 2. Complete Workflow Map

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DAILY INSTALLER LIFECYCLE                       │
└────────────────────────────────────────────────────────────────────────┘

  6:30 AM (Shop Loadout)
  ─────────────────────
  1. Open App on iPhone (Saved to Home Screen)
  2. Select Job Profile: [ AC + 90% Gas Furnace ] or [ Heat Pump ]
  3. Toggle Site Conditions: [ Reusing Existing Line Set? ] [ Concrete Wall? ]
  4. Work through the Rapid Clipboard:
     • Tap checkbox to confirm loaded item.
     • Tap (i) on any unfamiliar item for photo, connection point, and Gotcha warning.
     • Review Consumables Traffic Lights (🟢/🟡/🔴).
  5. Missing an item? Tap [ 🚨 1-Tap Text Warehouse ] to send pre-formatted SMS.

  8:00 AM – 3:30 PM (Job Site Execution)
  ──────────────────────────────────────
  • App remains in phone memory offline.
  • Reference (i) cards if questioning wiring, fuse sizing, or float switch placement.

  4:00 PM (Job Wrap-Up)
  ────────────────────
  1. Tap [ Mark Job Complete ]
  2. Review "Parts Actually Used":
     • Toggle [ Returned to Truck ] for any unused boxes/line set.
  3. App auto-deducts used major parts from truck stock.
  4. Quick 10-second glance at Consumables traffic lights to flag replenishment for tomorrow.
```

---

## 3. Categorized Master Checklist & Equipment Database

### A. Electrical & Power (Line & Control Voltage)
* **60A NEMA 3R Outdoor Disconnect Box** (Fused vs. Non-Fused)
* **RK5 Time-Delay Dual-Element Fuses** (30A, 35A, 40A, 50A, 60A - never fast-acting)
* **1/2" or 3/4" Liquid-Tight Flexible Conduit Whip (6ft)** + 90° and Straight fittings
* **Panel Circuit Breaker** (Matched to panel brand: Square D QO/Homeline, Siemens, Eaton BR/CH)
* **High-Voltage Wire:** 10/2, 8/2, or 6/2 UF/Romex
* **Thermostat & Wall Goof Plate** (18/5 or 18/8 solid copper wire)
* **Inline 3A Blade Fuse + Waterproof Holder** (Mandatory low-voltage board protection)

### B. Refrigerant, Piping & Modern A2L Transition Tools
* **Pre-Insulated Copper Line Set** (3/8" x 3/4", 7/8", or 1-1/8")
* **A2L Reverse-Thread Tank Adapter** (1/4" LH Female Flare to 1/4" RH Male Flare for R-454B / R-32)
* **A2L Indoor Leak Detection Sensor Harness & Mitigation Board**
* **Nylog Blue Synthetic Gasket & Thread Lubricant**
* **15% Silver Brazing Rods (Sil-Fos 15)** + Wet Heat-Shield Rag / Gel
* **Dry Nitrogen Bottle (Min 800 PSI)** + 0-600 PSI Test Regulator
* **High-Temp PTFE Replacement Schrader Cores** + Valve Core Removal Tools
* **Rx11-Flush Kit & Step-Down Copper Reducers** (Required when reusing existing line sets)

### C. Drainage, Venting & Safety
* **3/4" Schedule 40 Solid Core PVC Pipe** (Two 10ft sticks) + 90s, 45s, couplings
* **3/4" PVC P-Trap Assembly** with Cleanout Tee & Dust Cap
* **Safe-T Switch SS2** (Inline magnetic float switch for coil auxiliary drain port)
* **Secondary Emergency Drain Pan & Pan Float Switch** (For attic/finished space installs)
* **Condensate Pump + 3/8" ID Clear Vinyl Tubing** + Stainless hose clamps
* **Purple Primer & Medium Clear PVC Cement**
* **Venting (90%+):** System 1738 / Sch 40 PVC + Concentric Vent Kit or Sidewall Screens
* **Venting (80%):** Type B-vent double-wall pipe + adjustable elbows + storm collar

### D. Bulk Consumables (Traffic Light Tracking: 🟢/🟡/🔴)
* 1/2" Hex-Head #8 Self-Piercing Zip Screws
* 1" Hex-Head #10 Heavy Gauge Screws
* UL-181A/B Cold-Weather Rated Foil Tape
* Water-Based Duct Mastic (Pookie) + Chip Brushes
* 100% RTV Silicone (Clear & White) + Caulk Gun
* 36" UV-Rated Plenum Duct Ties + 8"/14" Cable Ties
* Plumber's Galvanized Perforated Hanger Strap

### E. Tear-Out, Recovery & Mounting
* Certified Refrigerant Recovery Tank (A2L compatible) + Digital Refrigerant Scale
* A2L-Rated Non-Sparking Recovery Machine & Spark-Free Vacuum Pump
* Heavy-Duty Appliance Dolly & Stair-Climbing Moving Straps
* Composite Equipment Pad (36x36 or 40x40) + Leveling Shims
* 3" or 6" Snow Legs / Heat Pump Pump-Up Risers

---

## 4. Verification & Testing

The standalone application is packaged as a single zero-dependency file at `/Users/corybaxter/Desktop/AI/projects/HVAC-partslist/index.html`.
* **Zero build steps or npm installations required.**
* **Can be loaded directly in iOS Safari and added to the iPhone Home Screen.**
* **Tested with `localStorage` persistence across sessions.**

---

## 5. In-App Multi-Page Receipt Scanner & Purchasing Habit Intelligence

To allow installers to build a company-specific truck catalog based on real buying habits rather than guesswork, the app features an integrated multi-page receipt management and learning loop:
1. **Multi-Page Photo Capture**: Invoices and counter tickets from **Johnstone Supply** and **Duncan Supply** often span 2 to 4 pages. Installers can snap multiple pages sequentially or select multiple photos at once. Photos are compressed into a thumbnail gallery with `Page 1 of 2`, `Page 2 of 2` badges and an inline `[+ Add Another Page]` button.
2. **Line Item Extraction Across Pages**: Consolidates line items from all pages into a unified review card (SKU, brand description, price, unit of measure, category).
3. **Purchasing Habit Frequency Counter**: Tracks repeat purchases. Items purchased 2+ times across tickets are tagged with a `🔥 Top Staple` badge and automatically promoted to the permanent morning truck loadout checklist.
4. **Smart Kit Detection**: Detects correlated purchases (e.g., mini-split wall brackets + 14/4 tray cable + line-hide) to suggest automated job kits.
5. **Receipt Archive**: Stores multi-page receipt images, invoice numbers, dates, and total job costs for billing proof and tax record keeping.

---

## 6. Jobber Work Order / Dispatch Ticket Auto-Configurator

Installers receive daily work orders through **Jobber** (e.g., *American Standard 13-SEER2 2.5-Ton AC + 60k Single Stage 95% S9X1 Furnace*). The app automatically translates sales proposals into physical truck build sheets:
* **Tonnage Mapping (2.5-Ton)**: Auto-configures **3/8" x 3/4" line set**, **30A 2-pole breaker**, **10/2 Romex wire**, and **36" x 36" composite pad**.
* **Condensing Furnace Intelligence (95% S9X1)**: Automatically hides metal B-vent and stages **2" Schedule 40 solid-core PVC pipe with sweep 90 elbows**, plus primary and secondary condensate drain lines.
* **Scope Keyword Triggers**:
  * Detecting *"New refrigerant lines"* stages a full 50ft line set coil and disables the line-flush kit.
  * Detecting *"Removal of old equipment"* automatically stages the spark-free A2L recovery machine, certified recovery cylinder, and heavy-duty stair-climber appliance dolly.
* **1-Tap "Apply to Morning Loadout"**: Syncs the Jobber equipment specs directly into Truck 4's checklist in 2 seconds.

---

## 7. User-Side Customization & Odds and Ends Drawer

* **Hide Unused Items**: Installers can toggle any default item off with a 1-tap `[🚫 Hidden]` button under "My Truck".
* **Dedicated Odds & Ends Section**: Real-time traffic-light tracking (🟢 Good / 🟡 Low / 🔴 Empty) for 8" black UV ties, 14" heavy-duty ties, 36" plenum ratchet ties, Tapcon masonry screws, and thumb gum / duct seal compound.
* **1-Tap Add Custom Item**: Add company-specific odds and ends directly on the phone with custom supply house part numbers, gotchas, and counter phrases.
* **Multi-Truck Sync**: Lead installers can tap `Export` to share their customized catalog with other trucks via JSON text or message.

