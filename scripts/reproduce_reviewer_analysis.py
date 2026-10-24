"""
CRISP-Net — Reviewer Analysis and Companion Metrics Generator
============================================================
This script implements the quantitative additions requested in the reviewer report:
1. Item A3: PCR for uncalibrated quantile heads and companion clock-defined event-peak containment.
2. Item A4: Bootstrap confidence intervals for test RMSE, event-day RMSE, and PCR.
3. Item A5: Lei et al. (2018) normalized conformal prediction baseline (|y - ŷ| / sqrt(ŷ + 1)).
4. Updates result tables and exports them to results/tables/.
"""

import os
import pickle
import numpy as np
import pandas as pd

def run_all_analyses(base_dir=r'd:\Research_NG\CRISP-Net'):
    print("=" * 70, flush=True)
    print("CRISP-Net Reviewer Quantitative Reproducibility Pipeline", flush=True)
    print("=" * 70, flush=True)

    # 1. Load Windows and Metadata
    win_path = os.path.join(base_dir, 'cache', 'tensors', 'windows__2023__5b7a3a5529.pkl')
    exo_path = os.path.join(base_dir, 'cache', 'tensors', 'exogenous__2023__c29b8b64eb.pkl')
    
    with open(win_path, 'rb') as f:
        windows = pickle.load(f)
    with open(exo_path, 'rb') as f:
        exo = pickle.load(f)

    split = np.array(windows['split'])
    starts = np.array(windows['starts'])
    Z = exo['Z']

    # Splits: 0=Train, 1=Tune, 3=Calibration (364), 2=Test (819)
    test_mask = (split == 2)
    cal_mask = (split == 3)
    
    test_starts = starts[test_mask]
    cal_starts = starts[cal_mask]

    # Regimes on Test (determined by first prediction horizon step t+12)
    t_idx_te = test_starts + 12
    ev_test = Z[t_idx_te, 6] > 0.5
    pk_test = Z[t_idx_te, 5] > 0.5
    ev_pk_test = ev_test & pk_test

    # Regimes on Calibration
    t_idx_cal = cal_starts + 12
    ev_cal = Z[t_idx_cal, 6] > 0.5
    pk_cal = Z[t_idx_cal, 5] > 0.5

    print(f"Test split windows  : {len(test_starts)} (Event: {ev_test.sum()}, Event-Peak: {ev_pk_test.sum()})", flush=True)
    print(f"Calib split windows : {len(cal_starts)} (Event: {ev_cal.sum()}, Event-Peak: {(ev_cal & pk_cal).sum()})", flush=True)

    # -------------------------------------------------------------------------
    # 2. Companion Uncertainty Numbers (Reviewer A3)
    # -------------------------------------------------------------------------
    print("\n[1/3] Computing companion uncertainty metrics (Item A3)...", flush=True)
    models = [
        ('CRISP-Net', '2023__v2__CRISP-Net.npz'),
        ('CRISP-Net w/o gates', '2023__v2__CRISP-Net_w_o_gates.npz'),
        ('CRISP-Net w/o PRI', '2023__v2__CRISP-Net_w_o_PRI.npz'),
        ('MC-Dropout', '2023__v2__MC-Dropout.npz'),
        ('Deep Ensemble', '2023__v2__Deep_Ensemble.npz'),
    ]

    uncert_rows = []
    alpha = 0.10

    for name, fname in models:
        p = os.path.join(base_dir, 'results', 'predictions', fname)
        data = np.load(p)
        yt = data['y_true'][:]
        yp = data['y_pred'][:]
        hi_cal = data['hi'][:]
        lo_cal = data['lo'][:]
        has_raw = ('hi_raw' in data and 'lo_raw' in data)

        # Standard metrics
        picp = 100 * ((yt >= lo_cal) & (yt <= hi_cal)).mean()
        mpiw = (hi_cal - lo_cal).mean()
        w = (hi_cal - lo_cal) + (2.0 / alpha) * np.clip(lo_cal - yt, 0, None) + (2.0 / alpha) * np.clip(yt - hi_cal, 0, None)
        winkler = w.mean()

        # Realized surge PCR (top decile of observed demand on event days)
        yt_ev = yt[ev_test]
        hi_cal_ev = hi_cal[ev_test]
        thr = np.quantile(yt_ev, 0.9)
        m = yt_ev >= max(thr, 1.0)
        pcr_cal = 100 * (yt_ev[m] <= hi_cal_ev[m]).mean()

        if has_raw:
            hi_raw = data['hi_raw'][:]
            lo_raw = data['lo_raw'][:]
            hi_raw_ev = hi_raw[ev_test]
            pcr_uncal = 100 * (yt_ev[m] <= hi_raw_ev[m]).mean()
            picp_uncal = 100 * ((yt >= lo_raw) & (yt <= hi_raw)).mean()
            mpiw_uncal = (hi_raw - lo_raw).mean()
        else:
            pcr_uncal = np.nan
            picp_uncal = np.nan
            mpiw_uncal = np.nan

        # Clock-defined event-peak containment (without conditioning on outcome)
        yt_clock = yt[ev_pk_test]
        hi_clock = hi_cal[ev_pk_test]
        lo_clock = lo_cal[ev_pk_test]
        clock_ub_contain = 100 * (yt_clock <= hi_clock).mean()
        clock_picp = 100 * ((yt_clock >= lo_clock) & (yt_clock <= hi_clock)).mean()

        uncert_rows.append({
            'Model': name,
            'PICP': picp,
            'MPIW': mpiw,
            'Winkler': winkler,
            'PCR': pcr_cal,
            'PCR_uncal': pcr_uncal,
            'Clock_UB_Contain': clock_ub_contain,
            'Clock_PICP': clock_picp,
            'PICP_uncal': picp_uncal,
            'MPIW_uncal': mpiw_uncal
        })

    df_uncert = pd.DataFrame(uncert_rows)
    out_uncert = os.path.join(base_dir, 'results', 'tables', 'uncertainty_results_expanded_v3.csv')
    df_uncert.to_csv(out_uncert, index=False)
    print(df_uncert.to_string(index=False), flush=True)
    print(f"Saved expanded uncertainty table to: {out_uncert}", flush=True)

    # -------------------------------------------------------------------------
    # 3. Lei et al. (2018) Normalized Conformal Prediction Baseline (Item A5)
    # -------------------------------------------------------------------------
    print("\n[2/3] Evaluating Lei et al. (2018) normalized conformal baseline (Item A5)...", flush=True)
    p_crisp_cal = os.path.join(base_dir, 'results', 'conformal', '2023__v2__CRISP-Net_calib.npz')
    p_crisp_te = os.path.join(base_dir, 'results', 'predictions', '2023__v2__CRISP-Net.npz')
    
    cal_data = np.load(p_crisp_cal)
    te_data = np.load(p_crisp_te)
    
    yt_cal = cal_data['y_true'][:]
    yp_cal = cal_data['y_pred'][:]
    yt_te = te_data['y_true'][:]
    yp_te = te_data['y_pred'][:]

    # Nonconformity score: s = |y - ŷ| / sqrt(max(ŷ, 0) + 1)
    s_norm_cal = np.abs(yt_cal - yp_cal) / np.sqrt(np.maximum(yp_cal, 0) + 1.0)
    n_cal = s_norm_cal.size
    q_level = min(1.0, (1 - alpha) * (1 + 1.0 / n_cal))
    
    # 3a. Global pooled normalized quantile
    q_norm_global = np.quantile(s_norm_cal, q_level)
    scale_te = np.sqrt(np.maximum(yp_te, 0) + 1.0)
    lo_lei_global = np.maximum(0, yp_te - q_norm_global * scale_te)
    hi_lei_global = yp_te + q_norm_global * scale_te

    # 3b. Per-channel normalized quantiles
    lo_lei_ch = np.zeros_like(yp_te)
    hi_lei_ch = np.zeros_like(yp_te)
    q_lei_chs = []
    for c in range(2):
        s_c = s_norm_cal[..., c].ravel()
        qc = np.quantile(s_c, q_level)
        q_lei_chs.append(qc)
        lo_lei_ch[..., c] = np.maximum(0, yp_te[..., c] - qc * scale_te[..., c])
        hi_lei_ch[..., c] = yp_te[..., c] + qc * scale_te[..., c]

    # Evaluate
    def eval_suite(y, lo, hi):
        p = 100 * ((y >= lo) & (y <= hi)).mean()
        m = (hi - lo).mean()
        w = ((hi - lo) + (2.0 / alpha) * np.clip(lo - y, 0, None) + (2.0 / alpha) * np.clip(y - hi, 0, None)).mean()
        
        y_e = y[ev_test]
        h_e = hi[ev_test]
        th = np.quantile(y_e, 0.9)
        pk_m = y_e >= max(th, 1.0)
        pcr = 100 * (y_e[pk_m] <= h_e[pk_m]).mean()
        return p, m, w, pcr

    p_glob, m_glob, w_glob, pcr_glob = eval_suite(yt_te, lo_lei_global, hi_lei_global)
    p_ch, m_ch, w_ch, pcr_ch = eval_suite(yt_te, lo_lei_ch, hi_lei_ch)

    transfer_csv = os.path.join(base_dir, 'results', 'tables', 'conformal_transfer_2023_v2.csv')
    df_trans = pd.read_csv(transfer_csv)
    
    new_rows = [
        {'Model': 'CRISP-Net (Point) + Lei Normalized (Pooled)', 'PICP': p_glob, 'MPIW': m_glob, 'Winkler': w_glob, 'PCR': pcr_glob, 'retrained': 'no'},
        {'Model': 'CRISP-Net (Point) + Lei Normalized (Per-Channel)', 'PICP': p_ch, 'MPIW': m_ch, 'Winkler': w_ch, 'PCR': pcr_ch, 'retrained': 'no'}
    ]
    df_trans_expanded = pd.concat([df_trans, pd.DataFrame(new_rows)], ignore_index=True)
    out_trans = os.path.join(base_dir, 'results', 'tables', 'conformal_transfer_expanded_v3.csv')
    df_trans_expanded.to_csv(out_trans, index=False)
    print(df_trans_expanded.to_string(index=False), flush=True)
    print(f"Saved expanded conformal transfer table to: {out_trans}", flush=True)

    # -------------------------------------------------------------------------
    # 4. Bootstrap Confidence Intervals (Item A4)
    # -------------------------------------------------------------------------
    print("\n[3/3] Generating Bootstrap 95% Confidence Intervals (Item A4)...", flush=True)
    np.random.seed(42)
    B = 500  # 500 iterations is statistically ample for 95% CIs
    n_te = len(yt_te)
    
    # Pre-extract arrays in memory
    hi_te_all = te_data['hi'][:]
    hir_te_all = te_data['hi_raw'][:]
    
    def get_point_metrics(idx):
        y_t = yt_te[idx]
        y_p = yp_te[idx]
        ev_m = ev_test[idx]
        
        rmse_all = np.sqrt(np.mean((y_t - y_p) ** 2))
        rmse_norm = np.sqrt(np.mean((y_t[~ev_m] - y_p[~ev_m]) ** 2))
        rmse_event = np.sqrt(np.mean((y_t[ev_m] - y_p[ev_m]) ** 2))
        
        y_te_ev = y_t[ev_m]
        hi_te_ev = hi_te_all[idx][ev_m]
        hir_te_ev = hir_te_all[idx][ev_m]
        
        th = np.quantile(y_te_ev, 0.9)
        pk_m = y_te_ev >= max(th, 1.0)
        pcr_c = 100 * (y_te_ev[pk_m] <= hi_te_ev[pk_m]).mean()
        pcr_r = 100 * (y_te_ev[pk_m] <= hir_te_ev[pk_m]).mean()
        return rmse_all, rmse_norm, rmse_event, pcr_c, pcr_r

    pt_all, pt_norm, pt_event, pt_pcr_c, pt_pcr_r = get_point_metrics(np.arange(n_te))
    
    boot_res = []
    for _ in range(B):
        b_idx = np.random.choice(n_te, size=n_te, replace=True)
        boot_res.append(get_point_metrics(b_idx))
    boot_res = np.array(boot_res)

    metric_names = ['RMSE_all', 'RMSE_normal', 'RMSE_event', 'PCR_calibrated', 'PCR_uncalibrated']
    pts = [pt_all, pt_norm, pt_event, pt_pcr_c, pt_pcr_r]
    boot_rows = []
    for i, m_name in enumerate(metric_names):
        ci = np.percentile(boot_res[:, i], [2.5, 97.5])
        boot_rows.append({
            'Metric': m_name,
            'Point_Estimate': pts[i],
            'CI95_Lower': ci[0],
            'CI95_Upper': ci[1]
        })
    df_boot = pd.DataFrame(boot_rows)
    out_boot = os.path.join(base_dir, 'results', 'tables', 'bootstrap_ci_2023_v3.csv')
    df_boot.to_csv(out_boot, index=False)
    print(df_boot.to_string(index=False), flush=True)
    print(f"Saved bootstrap CI table to: {out_boot}", flush=True)

    print("\n" + "=" * 70, flush=True)
    print("[SUCCESS] All reviewer-requested quantitative tasks successfully computed!", flush=True)
    print("=" * 70, flush=True)

if __name__ == '__main__':
    run_all_analyses()
