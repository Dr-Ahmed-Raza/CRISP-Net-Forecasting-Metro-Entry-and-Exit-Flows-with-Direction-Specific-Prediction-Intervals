<div align="center">

# CRISP-Net

### Forecasting Metro Entry and Exit Flows with Direction-Specific Prediction Intervals

[![Python](https://img.shields.io/badge/Python-≥3.10-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-≥2.0-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![License](https://img.shields.io/badge/License-Academic_Use-blue.svg)](#-license)
[![Dataset](https://img.shields.io/badge/Dataset-Nanjing_Metro_AFC_2023-green.svg)](#-dataset)

---

**CRISP-Net** (Conformal Risk-Informed Station-level Prediction Network) predicts both **entry and exit** passenger flows at every metro station and attaches **calibrated prediction intervals** to each forecast — for example, *"between 420 and 610 passengers"* — with a statistical guarantee that the true value falls inside that range **90% of the time**.

Unlike existing models that output a single number, CRISP-Net provides **direction-aware conformal risk bounds** that adapt dynamically to normal and event conditions, giving metro controllers actionable upper limits for real-time operational decisions.

</div>

---

## 📌 Highlights

| | |
|:---|:---|
| 🎯 **Point Accuracy** | RMSE **30.90** — matches the best baselines while uniquely providing calibrated ranges |
| 🛡️ **Event Resilience** | Error rises only **+1.0%** on event days (vs. **+10.9%** for the strongest competitor) |
| 📏 **Peak Coverage** | **91.0% PCR** — upper bounds contain actual demand during critical peaks (baselines: ~70%) |
| 🔀 **Bidirectional** | Separate calibration for entry vs. exit flows (exit margins are **4.2× wider** than entry) |
| 📊 **Uncertainty** | Three methods compared: native quantile heads, MC-Dropout, Deep Ensemble + conformal transfer |
| ⚡ **Efficiency** | **257K parameters** · 80 training epochs · full pipeline in a single notebook |

---

## 🌟 Key Contributions

### 1. Direction-Specific Prediction Intervals
Entry and exit flows require fundamentally different uncertainty margins. Exit ranges need corrections **~4.2× wider** than entry ranges during quiet periods, and they adjust in **opposite directions** during event-day peaks. CRISP-Net learns these asymmetries end-to-end.

### 2. Peak Containment Rate (PCR) — A New Evaluation Metric
Standard coverage metrics (PICP) show that many methods achieve 90% overall hit rates. However, they conceal catastrophic failures during the moments that matter most. Our proposed **PCR** reveals that baseline methods differ by up to **20 percentage points** in coverage during critical event peaks — exactly when operators need reliable bounds.

### 3. Conformal Transfer Across Architectures
We demonstrate that CRISP-Net's conformal calibration can be **transferred to any existing point-forecast model** (AGCRN, Graph WaveNet, TDAG-Net, TGALSTM) without retraining, achieving valid 90% coverage. However, only CRISP-Net maintains high **peak** coverage because it learns station- and time-specific uncertainty during training.

### 4. Persona-Aware Encoding (PRI Module)
Separating passengers into distinct behavioral types (commuters, casual riders, tourists, students) and standardizing each channel independently yields a **1.49 RMSE improvement** — demonstrating that who rides matters as much as how many ride.

---

## 📊 Benchmark Results

### Point Forecast Accuracy

> 191 stations · 819 test windows · 10-minute resolution · entry + exit channels

| Model | RMSE ↓ | MAE ↓ | WMAPE ↓ | R² ↑ | Params |
|:---|:---:|:---:|:---:|:---:|:---:|
| Graph WaveNet | 36.740 | 15.618 | 21.28% | 0.9324 | 65,068 |
| TGALSTM | 35.338 | 15.321 | 20.88% | 0.9375 | 210,527 |
| TDAG-Net | 32.210 ± 0.210 | 14.108 | 19.22% | 0.9481 | 253,825 |
| TDAG-Net (Input-Splitter) | 30.991 ± 0.123 | 13.794 | 18.80% | 0.9519 | 254,209 |
| AGCRN | 30.861 ± 0.298 | 13.531 | 18.44% | 0.9523 | 258,050 |
| **CRISP-Net** | **30.896** | **13.645** | **18.59%** | **0.9522** | **257,313** |
| **CRISP-Net (M=5 Ensemble)** | **30.088** | **13.412** | **18.28%** | **0.9547** | **1,271,085** |

### Event-Day Resilience

> 24 flagged event days · 182 test windows · Concerts, sports, and holiday surges

| Model | Normal RMSE | Event RMSE | Δ Change | Verdict |
|:---|:---:|:---:|:---:|:---|
| AGCRN | 30.861 | 34.213 ± 1.088 | **+10.9%** | ❌ Significant degradation |
| TGALSTM | 35.338 | 35.565 | +0.6% | Stable but high baseline error |
| TDAG-Net | 32.210 | 32.482 | +0.8% | Good resilience |
| **CRISP-Net** | **30.896** | **31.217** | **+1.0%** | ✅ Best accuracy + resilience |

### Uncertainty Quantification & Conformal Prediction

> α = 0.10 (target 90% coverage) · Per-channel Mondrian calibration

| Method | PICP ↑ | MPIW ↓ | Winkler ↓ | PCR ↑ | PICP (uncal.) |
|:---|:---:|:---:|:---:|:---:|:---:|
| 🏆 **CRISP-Net** | **90.01** | **61.45** | **80.19** | **90.97** | 89.71 |
| CRISP-Net w/o gates | 90.08 | 62.87 | 80.06 | 90.90 | 90.60 |
| CRISP-Net w/o PRI | 89.94 | 65.54 | 82.98 | 91.45 | 90.40 |
| MC-Dropout | 90.97 | 58.20 | 110.92 | 72.05 | 23.79 |
| Deep Ensemble (M=5) | 90.33 | 54.55 | 109.75 | 70.41 | 19.24 |

> **Key insight:** MC-Dropout and Deep Ensemble achieve valid overall coverage *only after* conformal correction, but their **peak coverage collapses** to ~70% — they cannot distinguish uncertain from certain windows. CRISP-Net's native quantile heads maintain **91% peak coverage** because uncertainty is learned during training.

### Conditional Coverage by Regime (Mondrian Bins)

| Regime | Windows | PICP | MPIW | Winkler |
|:---|:---:|:---:|:---:|:---:|
| Normal · Off-peak | 469 | 90.02 | 49.73 | 66.64 |
| Normal · Peak | 168 | 89.98 | 96.52 | 119.42 |
| Event · Off-peak | 134 | 90.39 | 55.69 | 74.06 |
| Event · Peak | 48 | 88.96 | 69.26 | 92.40 |

### Ablation Study

| Variant | RMSE | Δ RMSE | Key Finding |
|:---|:---:|:---:|:---|
| **CRISP-Net (Full)** | **30.896** | — | Complete architecture |
| w/o PRI (persona inputs) | 32.383 | +1.49 | Persona decomposition is critical for accuracy |
| w/o gates (fusion gates) | 30.652 | −0.24 | Gates slightly regularize; negligible impact on point accuracy |
| Encoder-only control | 48.076 ± 2.61 | +17.18 | Confirms improvements come from the modules, not the encoder |

---

## 📁 Repository Structure

```
CRISP-Net/
│
├── 📄 README.md                          # This file
│
├── 📂 Coding File/
│   └── CRISP_Net_Complete_Coding_File.ipynb    # Self-contained Jupyter notebook
│                                               # (data processing → training → evaluation
│                                               #  → conformal calibration → visualization)
│
├── 📂 data/                              # Processed dataset tensors & metadata
│   └── metadata/                         #   Station/line mappings, ticket code lookups
│
├── 📂 figures/                           # 34 publication-quality figures
│   ├── INDEX.csv                         #   Master figure catalog & metadata
│   ├── 01_corpus/                        #   F01–F07: Dataset audit & ingestion
│   ├── 02_persona/                       #   F08–F12: Persona profiles & context
│   ├── 03_graph/                         #   F13–F16: Graph topology & spatial flow
│   ├── 04_event/                         #   F17–F19: Event surge analysis
│   ├── 05_training/                      #   F20: Training convergence curves
│   ├── 06_results/                       #   F21–F28: Benchmarks & ablation
│   └── 07_uncertainty/                   #   F29–F34: Conformal prediction & intervals
│
├── 📂 results/                           # Quantitative evaluation outputs
│   ├── conformal/                        #   Conformal calibration artifacts (.npz, .csv)
│   ├── metrics/                          #   Per-model JSON metric files
│   ├── predictions/                      #   Prediction arrays (.npz)
│   └── tables/                           #   CSV & LaTeX benchmark tables
│
├── 📂 runs/                              # Model training checkpoints (selected v2 models)
│   ├── 2023__v2__CRISP-Net*/             #   CRISP-Net variants & cross-conf folds
│   ├── 2023__v2__Ensemble_member_*/      #   5-member deep ensemble
│   ├── 2023__v2__MC-Dropout*/            #   MC-Dropout + cross-conf folds
│   ├── 2023__v2__AGCRN*/                 #   AGCRN baseline (3 seeds + transfer)
│   ├── 2023__v2__TDAG-Net*/              #   TDAG-Net baseline (3 seeds + transfer)
│   ├── 2023__v2__Graph_WaveNet/          #   Graph WaveNet baseline
│   └── 2023__v2__TGALSTM/               #   TGALSTM baseline
│
├── 📂 exports/                           # Exported results & summaries
│   └── RESULTS_SUMMARY.md               #   Machine-generated results digest
│
└── 📂 logs/                              # Training logs & execution traces
```

---

## 🖼️ Figure Catalog

All 34 figures are provided in **PNG**, **PDF**, and **CSV** (underlying data) formats.

<details>
<summary><b>📂 01_corpus — Dataset & Ingestion Audit (F01–F07)</b></summary>

| ID | Title |
|:---|:---|
| F01 | Ingestion Audit & Data Retention across Source Files |
| F02 | Longitudinal Network Ridership by Direction with Flagged Event Days |
| F03 | Service-Hour Completeness & Data Availability |
| F04 | Ticket-Code Volume Distribution & Cumulative Coverage |
| F05 | Diurnal Temporal Signature of Each Ticket Code |
| F06 | Spatial Demand Concentration across the Network |
| F07 | Entry-to-Exit Propagation: Empirical Basis for the BFC Delay Kernel |

</details>

<details>
<summary><b>📂 02_persona — Persona Profiles & Context (F08–F12)</b></summary>

| ID | Title |
|:---|:---|
| F08 | Passenger Personas in Behavioural Feature Space |
| F09 | Diurnal Persona Profiles — Weekday vs. Weekend |
| F10 | Soft-Assignment Prior Matrix P₀ (inherited from Paper 3) |
| F11 | PMC Conditioning Signal: Persona Mix Trajectory |
| F12 | Exogenous Context Vector z_t and Its Regime Partition |

</details>

<details>
<summary><b>📂 03_graph — Graph Topology & Spatial Flow (F13–F16)</b></summary>

| ID | Title |
|:---|:---|
| F13 | Inferred Metro Topology (colored by line, sized by ridership) |
| F14 | Correlation Topology & CDG Sparsity Mask M |
| F15 | Empirical Delay-Lagged Adjacency A(δ) Supporting the BFC Kernel |
| F16 | Spatio-Temporal Flow Heatmap by Direction |

</details>

<details>
<summary><b>📂 04_event — Event Surge Analysis (F17–F19)</b></summary>

| ID | Title |
|:---|:---|
| F17 | Station-Level Robust Z-Score Surge Scan |
| F18 | Anatomy of the Largest Detected Surge |
| F19 | Event Days vs. Normal Days: Demand & Mix |

</details>

<details>
<summary><b>📂 05_training — Training Convergence (F20)</b></summary>

| ID | Title |
|:---|:---|
| F20 | Training Convergence & Loss Curves |

</details>

<details>
<summary><b>📂 06_results — Benchmarks & Ablation (F21–F28)</b></summary>

| ID | Title |
|:---|:---|
| F21 | Benchmark Comparison across All Six Accuracy Metrics |
| F22 | Accuracy Decomposed by Flow Direction |
| F23 | Error Growth over the Forecast Horizon |
| F24 | Observed vs. Predicted Flow at Representative Stations |
| F25 | Event-Window Behaviour & Peak Forecasting Resilience |
| F26 | Ablation of the CRISP-Net Components |
| F27 | Conditional Coverage under Three Calibration Regimes |
| F28 | Residual Diagnostics & Per-Station Error |

</details>

<details>
<summary><b>📂 07_uncertainty — Conformal Prediction & Intervals (F29–F34)</b></summary>

| ID | Title |
|:---|:---|
| F29 | Interval Quality across Uncertainty Methods |
| F30 | Conditional Coverage & Per-Direction Corrections |
| F31 | Peak Containment on Event Days |
| F32 | Prediction Intervals through an Event Day |
| F33 | Conformal Transfer across Architectures |
| F34 | Learned Persona Weights & Deviation from Initialisation |

</details>

---

## ⚙️ Getting Started

### Prerequisites

```
Python       ≥ 3.10
PyTorch      ≥ 2.0.0  (CUDA recommended)
NumPy        ≥ 1.24
Pandas       ≥ 2.0
SciPy        ≥ 1.10
scikit-learn ≥ 1.2
Matplotlib   ≥ 3.7
Seaborn      ≥ 0.12
```

### Quick Start

```bash
# Clone the repository
git clone https://github.com/usshamsuddeen/CRISP-Net-Forecasting-Metro-Entry-and-Exit-Flows-with-Direction-Specific-Prediction-Intervals.git
cd CRISP-Net-Forecasting-Metro-Entry-and-Exit-Flows-with-Direction-Specific-Prediction-Intervals

# Launch the notebook
jupyter notebook "Coding File/CRISP_Net_Complete_Coding_File.ipynb"
```

### Notebook Execution Guide

The notebook is fully self-contained — from raw data processing through final figure generation:

| Cell | Action | Time |
|:---|:---|:---|
| **Data Pipeline** | Loads and preprocesses AFC transactions | ~30 seconds |
| **Model Training** | Trains CRISP-Net + all baselines (80 epochs each) | ~6 hours (GPU) |
| **Conformal Calibration** | Calibrates intervals for all uncertainty methods | ~1 minute |
| **Results & Figures** | Generates all 34 figures + benchmark tables | ~3 minutes |

> 💡 **Tip:** Cached results and pretrained checkpoints are included in `runs/` and `results/`. You can skip training and jump directly to evaluation and visualization.

---

## 📝 Training Configuration

| Hyperparameter | Value | Notes |
|:---|:---|:---|
| Sequence length | 12 steps (2 hours) | Lookback window |
| Forecast horizon | 6 steps (1 hour) | Multi-step ahead |
| Batch size | 32 | |
| Epochs | 80 | |
| Learning rate | 3 × 10⁻⁴ | |
| Weight decay | 1 × 10⁻⁴ | |
| Loss: Huber δ | 1.0 | Robust to outliers |
| Loss: Pinball weight | 0.3 | Quantile regression term |
| Gradient clipping | 5.0 | |
| Early stopping patience | 15 epochs | |
| Conformal α | 0.10 | Target 90% coverage |
| Quantiles | (0.05, 0.50, 0.95) | Lower, median, upper |
| Calibration fraction | 0.50 | |
| Ensemble members (M) | 5 | For Deep Ensemble variant |
| Per-channel conformal | ✅ Enabled | Separate entry/exit calibration |
| Seed | 42 | |

---

## 📚 Citation

If you use this code, data, or methodology in your research, please cite:

```bibtex
@article{crispnet2026,
  title     = {CRISP-Net: Forecasting Metro Entry and Exit Flows with
               Direction-Specific Prediction Intervals},
  author    = {Shamsuddeen, Usman},
  year      = {2026},
  note      = {Under review}
}
```

---

## 📄 License

This repository is provided for **academic and research purposes only**. All passenger data has been anonymized using cryptographic SHA-256 hashing to preserve privacy.

---

<div align="center">

**Built with** ❤️ **using PyTorch**

</div>
