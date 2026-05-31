#!/usr/bin/env python3
"""
sync_copula.py — Gaussian-copula synthetic population sampler.

Adapted from the SYNC / SynC method (Li, Zhao & Fu, 2020):
  paper:  https://arxiv.org/abs/2009.09471  (ICDMW 2020)
          https://arxiv.org/abs/1904.07998  (journal version)
  ref R:  https://github.com/winstonll/SynC

Fits a Gaussian copula to real survey microdata — preserving each variable's
*marginal* distribution and the cross-variable *dependence* structure — then
draws N synthetic respondents from the fitted joint distribution. Each output
row is a statistically-plausible respondent that the persona-copula skill turns
into one persona doc.

What it does NOT do: the SYNC paper's neural-net step for merging multiple
overlapping *aggregated* sources (census downscaling). This implements the core
copula fit + sample on a single microdata table, which is the common case for
turning a survey into a synthetic persona population. For aggregate-only inputs,
see the --marginals mode notes in the skill.

Dependencies: numpy, scipy, pandas   ->   pip install numpy scipy pandas

Usage:
  python3 sync_copula.py --input survey.csv --n 12 --out synthetic.csv \
      --report report.json [--categorical col1,col2] [--ordinal col3,col4] \
      [--include colA,colB,...] [--seed 42]
"""
import argparse
import json
import sys

import numpy as np
import pandas as pd
from scipy.stats import norm, ks_2samp, rankdata


# ----------------------------------------------------------------------------- fitting

def column_kind(series, name, forced_cat, forced_ord, cat_unique_threshold=12):
    """Decide continuous | ordinal | nominal for a column."""
    if name in forced_ord:
        return "ordinal"
    if name in forced_cat:
        return "nominal"
    if pd.api.types.is_numeric_dtype(series):
        # numeric with few distinct values is probably a coded category;
        # treat as continuous otherwise.
        if series.nunique(dropna=True) > cat_unique_threshold:
            return "continuous"
        return "ordinal"  # few-valued numeric -> ordered codes
    return "nominal"


def category_order(series, kind):
    """Stable category ordering: natural sort for ordinal, freq-desc for nominal."""
    if kind == "ordinal":
        return sorted(series.dropna().unique().tolist())
    # nominal: order by descending frequency (consistent, arbitrary direction)
    counts = series.value_counts(dropna=True)
    return counts.index.tolist()


def fit_column(series, kind):
    """Return a marginal model + the per-observation latent normal scores z."""
    n = series.notna().sum()
    if kind == "continuous":
        vals = series.dropna().to_numpy(dtype=float)
        # van der Waerden normal scores from average ranks
        ranks = rankdata(series.fillna(series.median()), method="average")
        u = ranks / (len(series) + 1.0)
        z = norm.ppf(u)
        model = {"kind": "continuous", "sorted": np.sort(vals),
                 "integer": bool(np.all(np.equal(np.mod(vals, 1), 0)))}
        return model, z

    # categorical (ordinal or nominal): map categories -> probability intervals,
    # latent score = inverse-normal of each category's interval midpoint.
    cats = category_order(series, kind)
    probs = np.array([(series == c).sum() for c in cats], dtype=float)
    probs = probs / probs.sum()
    edges = np.concatenate([[0.0], np.cumsum(probs)])           # 0 .. 1
    mids = (edges[:-1] + edges[1:]) / 2.0
    cat_score = {c: norm.ppf(m) for c, m in zip(cats, mids)}
    fallback = float(np.mean(list(cat_score.values())))
    z = series.map(cat_score).fillna(fallback).to_numpy(dtype=float)
    model = {"kind": kind, "cats": list(cats), "edges": edges.tolist()}
    return model, z


def nearest_pd_correlation(R):
    """Clip eigenvalues to make R positive-definite, renormalise to unit diagonal."""
    vals, vecs = np.linalg.eigh((R + R.T) / 2.0)
    vals = np.clip(vals, 1e-6, None)
    R2 = vecs @ np.diag(vals) @ vecs.T
    d = np.sqrt(np.diag(R2))
    R2 = R2 / np.outer(d, d)
    np.fill_diagonal(R2, 1.0)
    return R2


# ----------------------------------------------------------------------------- sampling

def invert_column(u, model):
    """Map uniform draws back to the original variable scale via the marginal."""
    if model["kind"] == "continuous":
        s = np.asarray(model["sorted"], dtype=float)
        out = np.quantile(s, np.clip(u, 0.0, 1.0), method="linear")
        if model["integer"]:
            out = np.rint(out).astype(int)
        return out
    cats = model["cats"]
    edges = np.asarray(model["edges"], dtype=float)
    idx = np.clip(np.searchsorted(edges, u, side="right") - 1, 0, len(cats) - 1)
    return np.array([cats[i] for i in idx], dtype=object)


# ----------------------------------------------------------------------------- validation

def tv_distance(real, synth):
    """Total-variation distance between two categorical frequency distributions."""
    cats = set(real.dropna().unique()) | set(synth.dropna().unique())
    pr = real.value_counts(normalize=True)
    ps = synth.value_counts(normalize=True)
    return 0.5 * sum(abs(pr.get(c, 0.0) - ps.get(c, 0.0)) for c in cats)


def spearman_matrix(df, kinds):
    """Numeric-encode every column (categoricals -> ordered index) then Spearman."""
    enc = pd.DataFrame(index=df.index)
    for col in df.columns:
        if kinds[col] == "continuous":
            enc[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            order = category_order(df[col], "ordinal")
            lut = {c: i for i, c in enumerate(order)}
            enc[col] = df[col].map(lut)
    return enc.corr(method="spearman")


# ----------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="Gaussian-copula synthetic population sampler (SYNC method).")
    ap.add_argument("--input", required=True, help="Survey microdata CSV (one row per real respondent).")
    ap.add_argument("--n", type=int, required=True, help="Number of synthetic respondents to draw.")
    ap.add_argument("--out", required=True, help="Output CSV path for synthetic respondents.")
    ap.add_argument("--report", default=None, help="Optional JSON fidelity report path.")
    ap.add_argument("--include", default=None, help="Comma-separated columns to model (default: all).")
    ap.add_argument("--categorical", default="", help="Comma-separated columns to force NOMINAL.")
    ap.add_argument("--ordinal", default="", help="Comma-separated columns to force ORDINAL (ordered).")
    ap.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    df = pd.read_csv(args.input)
    if args.include:
        cols = [c.strip() for c in args.include.split(",") if c.strip()]
        df = df[cols]
    forced_cat = {c.strip() for c in args.categorical.split(",") if c.strip()}
    forced_ord = {c.strip() for c in args.ordinal.split(",") if c.strip()}

    # drop rows with any missing in modelled columns; report the loss
    n_before = len(df)
    df = df.dropna(axis=0, how="any").reset_index(drop=True)
    dropped = n_before - len(df)
    if len(df) < 10:
        print(f"WARNING: only {len(df)} complete rows — the copula fit will be very "
              f"directional. More respondents = a more faithful joint distribution.", file=sys.stderr)

    # classify + drop constant columns (no usable variance)
    kinds, constant = {}, []
    for c in df.columns:
        if df[c].nunique(dropna=True) <= 1:
            constant.append(c)
            continue
        kinds[c] = column_kind(df[c], c, forced_cat, forced_ord)
    if constant:
        print(f"NOTE: dropping constant column(s): {', '.join(constant)}", file=sys.stderr)
        df = df.drop(columns=constant)

    columns = list(kinds.keys())
    if len(columns) < 2:
        sys.exit("ERROR: need at least 2 non-constant columns to model dependence.")

    # fit marginals + build latent Gaussian matrix
    models, Z = {}, np.zeros((len(df), len(columns)))
    for j, c in enumerate(columns):
        models[c], Z[:, j] = fit_column(df[c], kinds[c])

    R = nearest_pd_correlation(np.corrcoef(Z, rowvar=False))
    L = np.linalg.cholesky(R)

    # sample: latent normal -> uniform -> inverse marginal
    G = rng.standard_normal((args.n, len(columns))) @ L.T
    U = norm.cdf(G)
    synth = pd.DataFrame({c: invert_column(U[:, j], models[c]) for j, c in enumerate(columns)})
    synth.to_csv(args.out, index=False)

    # ---- fidelity report
    marg = {}
    for c in columns:
        if kinds[c] == "continuous":
            ks = ks_2samp(pd.to_numeric(df[c]), pd.to_numeric(synth[c])).statistic
            marg[c] = {"kind": "continuous", "ks_distance": round(float(ks), 4),
                       "real_mean": round(float(df[c].mean()), 4),
                       "synth_mean": round(float(synth[c].mean()), 4)}
        else:
            marg[c] = {"kind": kinds[c], "tv_distance": round(float(tv_distance(df[c], synth[c])), 4)}

    sr = spearman_matrix(df[columns], kinds).to_numpy()
    ss = spearman_matrix(synth[columns], kinds).to_numpy()
    off = ~np.eye(len(columns), dtype=bool)
    corr_delta = np.abs(sr - ss)[off]
    report = {
        "input": args.input, "n_real_rows": int(len(df)), "rows_dropped_missing": int(dropped),
        "n_synth_rows": int(args.n), "seed": args.seed,
        "columns": {c: kinds[c] for c in columns},
        "marginal_fidelity": marg,
        "dependence_fidelity": {
            "spearman_mean_abs_delta": round(float(np.nanmean(corr_delta)), 4),
            "spearman_max_abs_delta": round(float(np.nanmax(corr_delta)), 4),
        },
    }

    print(f"Fit {len(df)} real rows -> sampled {args.n} synthetic rows -> {args.out}")
    if dropped:
        print(f"  ({dropped} rows dropped for missing values)")
    print("  Marginal fidelity (lower = closer to real):")
    for c, m in marg.items():
        metric = f"KS={m['ks_distance']}" if m["kind"] == "continuous" else f"TV={m['tv_distance']}"
        print(f"    - {c} [{m['kind']}]: {metric}")
    print(f"  Dependence fidelity (Spearman corr): "
          f"mean Δ={report['dependence_fidelity']['spearman_mean_abs_delta']}, "
          f"max Δ={report['dependence_fidelity']['spearman_max_abs_delta']}")

    if args.report:
        with open(args.report, "w") as f:
            json.dump(report, f, indent=2)
        print(f"  Report written to {args.report}")


if __name__ == "__main__":
    main()
