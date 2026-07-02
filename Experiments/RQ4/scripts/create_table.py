#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path

from scipy.stats import spearmanr

SCRIPT_DIR = Path(__file__).resolve().parent
IN_PATH = SCRIPT_DIR / "conciseness_correctness_scores.jsonl"
CSV_PATH = SCRIPT_DIR.parent / "results" / "sensitivity_table.csv"

MODELS = ["qwen", "olmo"]
MODEL_LABELS = {"qwen": "Qwen", "olmo": "OLMo"}


def _rho_mad(gs, ns):
    rho, _ = spearmanr(gs, ns)
    mad = sum(abs(n - g) for g, n in zip(gs, ns)) / len(gs)
    return rho, mad


def main():
    groups = defaultdict(list)
    with open(IN_PATH) as f:
        for line in f:
            r = json.loads(line)
            groups[(r["alt_model"], r["condition"])].append(r)

                                                                                 
                                                                                 
    rows = []
    for model in MODELS:
                                                                        
        g_rows = groups[(model, "altG_geminiP")]
        g_rho, g_mad = _rho_mad([r["correctness_gemini"] for r in g_rows],
                                 [r[f"correctness_{model}"] for r in g_rows])
        rows.append(["Correctness", MODEL_LABELS[model], g_mad, g_rho, "N/A", "N/A"])

    for model in MODELS:
        g_rows = groups[(model, "altG_geminiP")]
        p_rows = groups[(model, "geminiG_altP")]
        g_rho, g_mad = _rho_mad([r["conciseness_gemini"] for r in g_rows],
                                 [r["conciseness_new"] for r in g_rows])
        p_rho, p_mad = _rho_mad([r["conciseness_gemini"] for r in p_rows],
                                 [r["conciseness_new"] for r in p_rows])
        rows.append(["Conciseness", MODEL_LABELS[model], g_mad, g_rho, p_mad, p_rho])

    header = ["Dimension", "Alt. Model", "G_MAD", "G_rho", "P_MAD", "P_rho"]
    print(f"{header[0]:<13}{header[1]:<7}{header[2]:>8}{header[3]:>8}{header[4]:>8}{header[5]:>8}")
    print("-" * 44)
    for d, m, g_mad, g_rho, p_mad, p_rho in rows:
        g_mad_s = f"{g_mad:.3f}"
        g_rho_s = f"{g_rho:.3f}"
        p_mad_s = f"{p_mad:.3f}" if p_mad != "N/A" else "N/A"
        p_rho_s = f"{p_rho:.3f}" if p_rho != "N/A" else "N/A"
        print(f"{d:<13}{m:<7}{g_mad_s:>8}{g_rho_s:>8}{p_mad_s:>8}{p_rho_s:>8}")

    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for d, m, g_mad, g_rho, p_mad, p_rho in rows:
            writer.writerow([d, m,
                              f"{g_mad:.3f}", f"{g_rho:.3f}",
                              f"{p_mad:.3f}" if p_mad != "N/A" else "N/A",
                              f"{p_rho:.3f}" if p_rho != "N/A" else "N/A"])
    print(f"\n[+] CSV written to {CSV_PATH}")


if __name__ == "__main__":
    main()
