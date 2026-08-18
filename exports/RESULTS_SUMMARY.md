# CRISP-Net — Results Summary (2023 corpus)

_Generated 2026-08-17 11:34 · device cuda · seed 42_


## 1. Dataset

| Property | Value |
|---|---|
| Corpus | Nanjing Metro AFC 2023 |
| Source files ingested | 17 |
| Raw records read | 95,800,909 |
| Records retained | 95,733,909 |
| Directional events (entry + exit) | 190,911,927 |
| Stations (excluding [333]) | 191 |
| Lines | [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13] |
| Usable days | 57 (2023-03-01 → 2023-05-31) |
| Interval | 10 min, 06:00–23:50 |
| Ticket channels | 25 (top 24 + OTHER, 99.58% coverage) |
| Windows train / tune / calib / test | 3,640 / 364 / 364 / 819 |
| Event days flagged | 24 (182 test windows) |
| Context vector | z_t ∈ ℝ^8 — ['tod_sin', 'tod_cos', 'dow_sin', 'dow_cos', 'is_weekend', 'is_peak', 'event_flag', 'event_countdown'] |

## 2. Components, and what each one measured

| Component | Question it answers | Status |
|---|---|---|
| PRI | which personas drive the forecast | gate spread 0.116, corr with corpus share +0.74 |
| Bidirectional head | exit channel discarded in Paper 3 | entry and exit predicted jointly and calibrated separately |
| ECQ | forecasts carry no risk bound | worst-bin coverage improved +0.11 pp over raw heads |
| Transfer | is calibration architecture-specific | 4 point baselines calibrated without retraining |

**Removed after measurement (CALM-Net pilot, quoted not rerun):** context-driven dynamic graph (3.72% edge drift), learned delay kernel (r = −0.897 against measured propagation), FiLM persona conditioning (γ spread 0.045). The encoder control that attributes the pilot's regression to the encoder rather than to these modules scored RMSE 48.076 ± 2.608.


## 3. Main results (test set, both channels)

| Model                     |    RMSE |     MAE |   WMAPE |     R2 |     EPE |     NDE |   Params |   Epochs |   RMSE_std |
|:--------------------------|--------:|--------:|--------:|-------:|--------:|--------:|---------:|---------:|-----------:|
| Graph WaveNet             | 36.7400 | 15.6184 | 21.2814 | 0.9324 | 17.2456 | 23.0672 |    65068 |       80 |   nan      |
| AGCRN                     | 30.8610 | 13.5311 | 18.4372 | 0.9523 | 16.4926 | 19.3760 |   258050 |       80 |     0.2977 |
| TGALSTM                   | 35.3384 | 15.3205 | 20.8754 | 0.9375 | 17.3508 | 22.1872 |   210527 |       80 |   nan      |
| TDAG-Net                  | 32.2103 | 14.1083 | 19.2237 | 0.9481 | 16.0407 | 20.2232 |   253825 |       80 |     0.2100 |
| TDAG-Net (Input-Splitter) | 30.9906 | 13.7942 | 18.7958 | 0.9519 | 15.7490 | 19.4574 |   254209 |       80 |     0.1228 |
| CRISP-Net                 | 30.8963 | 13.6448 | 18.5922 | 0.9522 | 15.5890 | 19.3982 |   257313 |       80 |   nan      |
| CRISP-Net w/o gates       | 30.6522 | 13.6610 | 18.6143 | 0.9530 | 15.5013 | 19.2450 |   257313 |       80 |   nan      |
| CRISP-Net w/o PRI         | 32.3827 | 14.1359 | 19.2613 | 0.9475 | 16.1583 | 20.3315 |   256929 |       80 |   nan      |
| CRISP-Net (M=5)           | 30.0875 | 13.4123 | 18.2753 | 0.9547 | 15.3639 | 18.8904 |  1271085 |       80 |   nan      |

### Event days only

| Model                     |    RMSE |     MAE |   WMAPE |     R2 |     EPE |     NDE |   Params |   Epochs |   RMSE_std |
|:--------------------------|--------:|--------:|--------:|-------:|--------:|--------:|---------:|---------:|-----------:|
| Graph WaveNet             | 34.5756 | 15.1742 | 21.7147 | 0.9313 | 17.2456 | 23.1671 |    65068 |       80 |   nan      |
| AGCRN                     | 34.2134 | 14.5776 | 20.8610 | 0.9326 | 16.4926 | 22.9244 |   258050 |       80 |     1.0882 |
| TGALSTM                   | 35.5645 | 15.6341 | 22.3729 | 0.9273 | 17.3508 | 23.8297 |   210527 |       80 |   nan      |
| TDAG-Net                  | 32.4815 | 14.1684 | 20.2755 | 0.9393 | 16.0407 | 21.7640 |   253825 |       80 |     0.1754 |
| TDAG-Net (Input-Splitter) | 31.4830 | 13.8586 | 19.8321 | 0.9430 | 15.7490 | 21.0949 |   254209 |       80 |     0.0874 |
| CRISP-Net                 | 31.2167 | 13.7148 | 19.6264 | 0.9440 | 15.5890 | 20.9165 |   257313 |       80 |   nan      |
| CRISP-Net w/o gates       | 30.9995 | 13.6542 | 19.5397 | 0.9447 | 15.5013 | 20.7709 |   257313 |       80 |   nan      |
| CRISP-Net w/o PRI         | 32.4770 | 14.1830 | 20.2964 | 0.9393 | 16.1583 | 21.7609 |   256929 |       80 |   nan      |
| CRISP-Net (M=5)           | 30.5158 | 13.4637 | 19.2670 | 0.9465 | 15.3639 | 20.4468 |  1271085 |       80 |   nan      |

## 4. Uncertainty quantification

| Model               |    PICP |    MPIW |   Winkler |     PCR |   PICP_uncal |   MPIW_uncal |   Coverage gap |
|:--------------------|--------:|--------:|----------:|--------:|-------------:|-------------:|---------------:|
| CRISP-Net           | 90.0078 | 61.4465 |   80.1885 | 90.9749 |      89.7110 |      61.2718 |         0.0078 |
| CRISP-Net w/o gates | 90.0786 | 62.8712 |   80.0558 | 90.8985 |      90.5999 |      63.0496 |         0.0786 |
| CRISP-Net w/o PRI   | 89.9439 | 65.5409 |   82.9770 | 91.4549 |      90.3968 |      65.6862 |        -0.0561 |
| MC-Dropout          | 90.9747 | 58.1988 |  110.9246 | 72.0481 |      23.7856 |      12.3499 |         0.9747 |
| Deep Ensemble       | 90.3320 | 54.5476 |  109.7487 | 70.4098 |      19.2357 |      10.0899 |         0.3320 |

### Conditional coverage per Mondrian bin

| bin               |   n_windows |    PICP |    MPIW |   Winkler |
|:------------------|------------:|--------:|--------:|----------:|
| normal · off-peak |         469 | 90.0154 | 49.7270 |   66.6358 |
| normal · peak     |         168 | 89.9838 | 96.5190 |  119.4245 |
| event · off-peak  |         134 | 90.3851 | 55.6946 |   74.0570 |
| event · peak      |          48 | 88.9643 | 69.2596 |   92.3996 |

## 5. Training configuration (identical to Paper 3 except the pinball term)

| Hyper-parameter | Value |
|---|---|
| seq_len | 12 |
| horizon | 6 |
| batch_size | 32 |
| epochs | 80 |
| lr | 0.0003 |
| weight_decay | 0.0001 |
| huber_delta | 1.0 |
| pinball_weight | 0.3 |
| grad_clip | 5.0 |
| early_stop_patience | 15 |
| seed | 42 |
| report_seeds | (42,) |
| alpha | 0.1 |
| per_channel_conformal | True |
| quantiles | (0.05, 0.5, 0.95) |
| calib_frac | 0.5 |
| ensemble_members | 5 |

## 6. Figures

| figure_id   | group          | title                                                               |
|:------------|:---------------|:--------------------------------------------------------------------|
| F01         | 01_corpus      | Ingestion audit and data retention across source files              |
| F02         | 01_corpus      | Longitudinal network ridership by direction with flagged event days |
| F03         | 01_corpus      | Service-hour completeness and data availability                     |
| F04         | 01_corpus      | Ticket-code volume distribution and cumulative coverage             |
| F05         | 01_corpus      | Diurnal temporal signature of each ticket code                      |
| F06         | 01_corpus      | Spatial demand concentration across the network                     |
| F07         | 01_corpus      | Entry-to-exit propagation: empirical basis for the BFC delay kernel |
| F08         | 02_persona     | Passenger personas in behavioural feature space                     |
| F09         | 02_persona     | Diurnal persona profiles, weekday versus weekend                    |
| F10         | 02_persona     | Soft-assignment prior matrix P0 inherited from Paper 3              |
| F11         | 02_persona     | The PMC conditioning signal: persona mix trajectory                 |
| F12         | 02_persona     | Exogenous context vector z_t and its regime partition               |
| F13         | 03_graph       | Inferred metro topology coloured by line and sized by ridership     |
| F14         | 03_graph       | Correlation topology and the CDG sparsity mask M                    |
| F15         | 03_graph       | Empirical delay-lagged adjacency A(delta) supporting the BFC kernel |
| F16         | 03_graph       | Spatio-temporal flow heatmap by direction                           |
| F17         | 04_event       | Station-level robust z-score surge scan                             |
| F18         | 04_event       | Anatomy of the largest detected surge                               |
| F19         | 04_event       | Event days versus normal days: demand and mix                       |
| F20         | 05_training    | Training convergence and loss curves                                |
| F21         | 06_results     | Benchmark comparison across all six accuracy metrics                |
| F22         | 06_results     | Accuracy decomposed by flow direction                               |
| F23         | 06_results     | Error growth over the forecast horizon                              |
| F24         | 06_results     | Observed versus predicted flow at representative stations           |
| F25         | 06_results     | Event-window behaviour and peak forecasting resilience              |
| F26         | 06_results     | Ablation of the CRISP-Net components                                |
| F27         | 06_results     | Conditional coverage under three calibration regimes                |
| F28         | 06_results     | Residual diagnostics and per-station error                          |
| F29         | 07_uncertainty | Interval quality across uncertainty methods                         |
| F30         | 07_uncertainty | Conditional coverage and the per-direction corrections              |
| F31         | 07_uncertainty | Peak containment on event days                                      |
| F32         | 07_uncertainty | Prediction intervals through an event day                           |
| F33         | 07_uncertainty | Conformal transfer across architectures                             |
| F34         | 07_uncertainty | Learned persona weights and their deviation from initialisation     |