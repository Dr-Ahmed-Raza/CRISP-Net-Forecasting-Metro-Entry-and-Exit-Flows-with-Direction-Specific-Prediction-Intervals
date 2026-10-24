import json, os

nb_path = r'd:\Research_NG\CRISP-Net\Coding File\CRISP_Net_Complete_Coding_File.ipynb'

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"Loaded notebook with {len(nb['cells'])} cells.")

# 1. Update Cell 0: Header & Authors
cell0_lines = nb['cells'][0]['source']
updated_cell0 = []
for line in cell0_lines:
    if "Shamsuddeen" in line:
        updated_cell0.append(line.replace("Shamsuddeen", "Ahmed Raza, Guangjie Liu, Jie Cheng, Ghulam Muhayyu Din, Umer Bashir"))
    elif "4.2× wider" in line:
        updated_cell0.append("CRISP-Net produces calibrated, instance-adaptive prediction intervals with native quantile heads and modest conformal adjustments (≤ 0.33 pass/10 min).\n")
    else:
        updated_cell0.append(line)
nb['cells'][0]['source'] = updated_cell0

# 2. Update Cell 39 / 40 (Exogenous context & Node features)
cell39_src = ''.join(nb['cells'][39]['source'])
if "event_station" not in cell39_src:
    nb['cells'][39]['source'].append("\n> **Note on Station-Level Inputs (Reviewer Item A1):** In addition to the global 8-dimensional temporal context $z_t$, the model incorporates three station-level features: `transfer_ratio`, `venue_proximity`, and an `event_station` surge indicator (flagged when a station's daily peak flow exceeds robust $z \\ge 4$).\n")

# 3. Update Cell 65 (Metrics markdown: PCR and EPE formal definitions)
cell65_lines = nb['cells'][65]['source']
cell65_lines.append("\n\n### Metric Formal Definitions (Reviewer Item A3)\n"
                   "- **Peak Containment Rate (PCR)**: Evaluated on $\\mathcal{P}$, defined as the **top decile (90th percentile) of observed demand** among all station, direction, and horizon samples on event days in the test split.\n"
                   "- **Event-Day Peak Error (EPE)**: The Weighted Mean Absolute Percentage Error (WMAPE) evaluated specifically across the samples in $\\mathcal{P}$.\n"
                   "- **Clock-Defined Event Peak Containment**: The unconditional proportion of samples where demand falls below the upper bound during scheduled peak hours on event days (07:00–09:30 and 17:00–19:30; 48 test windows).\n")
nb['cells'][65]['source'] = cell65_lines

# Save back to notebook file
with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Successfully updated notebook documentation and definitions.")
