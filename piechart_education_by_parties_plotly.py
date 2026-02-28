import os
import re
from typing import Dict, List

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from nepal_election_constants import PARTIES
from helper_functions import filter_by_parties

# -----------------------------
# Config
# -----------------------------
FILE_PATH = "./data/2026_Nepal_Election_FTPT_candidates.xlsx"
VISUALS_DIR = "visuals"

FOOTER_TEXT = "Design: visualnepal.com<br>Data Source: election.gov.np"

# Fixed order (consistent everywhere)
EDU_ORDER = [
    "PhD",
    "Masters",
    "Bachelors",
    "Intermediate",
    "SLC / 10",
    "< 10 Class",
    "Not Available",
]

# Fixed Education Colors (Always Same)
EDU_COLORS = {
    "PhD": "#003366",           # Deep Navy Blue
    "Masters": "#2A6099",       # Royal Blue
    "Bachelors": "#4682B4",     # Steel Blue
    "Intermediate": "#87CEEB",  # Sky Blue
    "SLC / 10": "#B0E0E6",      # Pale Blue
    "< 10 Class": "#E0F2F7",    # Soft Powder Blue
    "Not Available": "#E0E0E0", # Light Grey
}

EDU_COL_NAME = "शैक्षिक योग्यता समूह"
PARTY_COL_NAME = "राजनीतिक दल / स्वतन्त्र"


# -----------------------------
# Normalization / Mapping
# -----------------------------
def normalize_education(value) -> str:
    """Normalize various education text variants into one of EDU_ORDER labels."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "Not Available"

    s = str(value).strip()
    if not s:
        return "Not Available"

    s_low = s.lower()

    # Common "not available" signals
    if s_low in {"na", "n/a", "not available", "unknown", "null", "none", "-"}:
        return "Not Available"

    # Use regex/contains to be robust to minor variations
    # PhD
    if re.search(r"\bph\.?d\b", s_low) or "doctor" in s_low:
        return "PhD"

    # Masters
    if "master" in s_low or re.search(r"\bm\.?a\b", s_low) or re.search(r"\bm\.?s\b", s_low) or "msc" in s_low or "mba" in s_low:
        return "Masters"

    # Bachelors
    if "bachelor" in s_low or re.search(r"\bb\.?a\b", s_low) or re.search(r"\bb\.?s\b", s_low) or "bsc" in s_low or "be" in s_low or "btech" in s_low:
        return "Bachelors"

    # Intermediate
    if "intermediate" in s_low or "10+2" in s_low or "+2" in s_low or "plus 2" in s_low:
        return "Intermediate"

    # < 10 Class  (MOVE THIS UP before SLC / 10)
    if "<" in s_low or "below" in s_low or "under" in s_low or "less than" in s_low:
        return "< 10 Class"
    if "class" in s_low:
        m = re.search(r"class\s*(\d+)", s_low)
        if m:
            n = int(m.group(1))
            if 1 <= n <= 9:
                return "< 10 Class"

    # SLC / 10  (comes AFTER)
    if "slc" in s_low or re.search(r"\bclass\s*10\b", s_low) or re.search(r"(?<!<)\b10\b", s_low):
        return "SLC / 10"

    # If the value is already one of the canonical labels, keep it
    if s in EDU_ORDER:
        return s

    # Default fallback
    return "Not Available"


# -----------------------------
# Core computations
# -----------------------------
def build_education_counts(df_party: pd.DataFrame) -> pd.Series:
    edu_series = df_party[EDU_COL_NAME].apply(normalize_education)
    counts = edu_series.value_counts().reindex(EDU_ORDER, fill_value=0)
    # Optional: drop 0 slices for cleaner party pies
    counts = counts[counts > 0]
    return counts


def compute_education_stats(df_party: pd.DataFrame) -> Dict[str, float]:
    """
    Keep a simple "stats box" like your age chart:
    - Total candidates
    - Higher Education share (Bachelors+)
    - Not Available count
    """
    edu_series = df_party[EDU_COL_NAME].apply(normalize_education)
    total = int(len(edu_series))

    if total == 0:
        return {"total": 0, "higher_ed_pct": None, "na_count": None}

    higher = edu_series.isin(["Bachelors", "Masters", "PhD"]).sum()
    na_count = (edu_series == "Not Available").sum()
    higher_pct = (higher / total) * 100.0

    return {"total": total, "higher_ed_pct": float(higher_pct), "na_count": int(na_count)}


# -----------------------------
# Figure builders
# -----------------------------
def make_party_figure(
    eng_name: str,
    sign_icon: str,
    edu_counts: pd.Series,
    stats: Dict[str, float],
) -> go.Figure:
    labels = list(edu_counts.index)
    values = list(edu_counts.values)
    colors = [EDU_COLORS.get(lbl, "#CCCCCC") for lbl in labels]

    fig = go.Figure(
        data=[
            go.Pie(
                domain=dict(x=[0.0, 0.55], y=[0.0, 1.0]),
                labels=labels,
                values=values,
                sort=False,
                direction="clockwise",
                rotation=140,
                marker=dict(colors=colors, line=dict(color="white", width=1)),
                textinfo="percent",
                texttemplate="%{percent:.1%}",
                textfont=dict(size=12),
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text=f"Education<br>(2026 <b>{eng_name} {sign_icon}</b> Candidates - FPTP)",
            x=0.5,
            xanchor="center",
            yanchor="top",
            font=dict(size=22),
        ),
        showlegend=True,
        legend=dict(
            orientation="v",
            x=0.90,
            y=0.98,
            xanchor="left",
            yanchor="top",
            font=dict(size=10),  # <-- legend font size line
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="rgba(0,0,0,0.15)",
            borderwidth=1,
        ),
        margin=dict(l=60, r=260, t=110, b=90),
    )

    # Stats box (right-side whitespace). Bold the key insight.
    if stats.get("total", 0) == 0:
        stats_html = (
            "Total Candidates - NA<br>"
            "Higher Ed - NA<br>"
            f"(Bachelor & Above)"
        )
    else:
        stats_html = (
            f"Total Candidates - {stats['total']}<br>"
            f"<b>Higher Ed - {stats['higher_ed_pct']:.1f}%</b><br>"
            f"(Bachelor & Above)"
        )

    fig.add_annotation(
        x=0.90,
        y=0.45,
        xref="paper",
        yref="paper",
        text=stats_html,
        showarrow=False,
        xanchor="left",
        align="left",
        font=dict(size=11, color="black"),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="rgba(0,0,0,0.15)",
        borderwidth=1,
        borderpad=8,
    )

    # Footer bottom-right
    fig.add_annotation(
        x=1.0,
        y=-0.15,
        xref="paper",
        yref="paper",
        text=FOOTER_TEXT,
        showarrow=False,
        xanchor="left",
        yanchor="bottom",
        align="right",
        font=dict(size=8, color="gray"),
    )

    return fig


def make_composite_figure(party_items: List[dict]) -> go.Figure:
    """
    Horizontal composite of party pies + one shared legend.
    Legend is built from dummy Scatter traces so it is always consistent
    even if some parties have missing categories.
    """
    n = len(party_items)
    if n == 0:
        raise ValueError("No parties to plot in composite chart.")

    legend_col_w = 0.12
    fig = make_subplots(
        rows=1,
        cols=n,
        specs=[[{"type": "domain"}] * n],
        horizontal_spacing=0.10,  # your spacing
    )
    fig.update_xaxes(showgrid=False, visible=False)
    fig.update_yaxes(showgrid=False, visible=False)

    # Only show legend items that appear in at least one party in this composite
    used_labels = set()
    for item in party_items:
        try:
            used_labels.update(list(item["edu_counts"].index))
        except Exception:
            continue
    used_edus = [e for e in EDU_ORDER if e in used_labels]

    for edu_label in used_edus:
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker=dict(size=12, color=EDU_COLORS.get(edu_label, "#CCCCCC")),
                name=edu_label,
                showlegend=True,
                hoverinfo="skip",
            )
        )

    def _stats_html(stats: Dict[str, float]) -> str:
        if stats.get("total", 0) == 0:
            return (
                "Total Candidates - NA<br>"
                "Higher Ed - NA<br>"
                f"(Bachelor & Above)"
            )
        return (
            f"Total Candidates - {stats['total']}<br>"
            f"<b>Higher Ed - {stats['higher_ed_pct']:.1f}%</b><br>"
            f"(Bachelor & Above)"
        )

    for i, item in enumerate(party_items, start=1):
        sign = item["sign"]
        edu_counts = item["edu_counts"]
        stats = item["stats"]
        eng_acronym = item["eng_acronym"]

        labels = list(edu_counts.index)
        values = list(edu_counts.values)
        colors = [EDU_COLORS.get(lbl, "#CCCCCC") for lbl in labels]

        fig.add_trace(
            go.Pie(
                labels=labels,
                values=values,
                sort=False,
                direction="clockwise",
                rotation=140,
                marker=dict(colors=colors, line=dict(color="white", width=1)),
                textinfo="percent",
                texttemplate="%{percent:.1%}",
                textfont=dict(size=11),
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
                showlegend=False,
            ),
            row=1,
            col=i,
        )

        x_center = (i - 0.5) / n

        # Party name ABOVE its pie
        fig.add_annotation(
            x=x_center,
            y=1.08,
            xref="paper",
            yref="paper",
            text=f"<b>{eng_acronym} {sign}</b>",
            showarrow=False,
            xanchor="center",
            yanchor="bottom",
            font=dict(size=14, color="black"),
        )

        # Stats box BELOW its pie
        fig.add_annotation(
            x=x_center,
            y=-0.14,
            xref="paper",
            yref="paper",
            text=_stats_html(stats),
            showarrow=False,
            xanchor="center",
            yanchor="top",
            align="left",
            font=dict(size=8, color="black"),
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="rgba(0,0,0,0.15)",
            borderwidth=1,
            borderpad=6,
        )

    fig.update_layout(
        title=dict(
            text="Education Qualification (2026 Election FPTP Candidates)\n",
            x=0.5,
            xanchor="center",
            yanchor="top",
            font=dict(size=24),
        ),

        showlegend=True,

        legend=dict(
            orientation="v",
            x=1.25,
            y=0.98,
            xanchor="left",
            yanchor="top",
            font=dict(size=8),
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="rgba(0,0,0,0.15)",
            borderwidth=1,
        ),

        # 👇 REMOVE GRID / BACKGROUND
        template=None,
        plot_bgcolor="white",
        paper_bgcolor="white",

        margin=dict(l=40, r=230, t=120, b=230),
    )

    # Footer bottom-right
    fig.add_annotation(
        x=1.5,
        y=-0.52,
        xref="paper",
        yref="paper",
        text=FOOTER_TEXT,
        showarrow=False,
        xanchor="right",
        yanchor="bottom",
        align="right",
        font=dict(size=8, color="gray"),
    )

    return fig


def save_figure(fig: go.Figure, out_path_png: str) -> None:
    out_path_png = str(out_path_png)
    out_path_html = os.path.splitext(out_path_png)[0] + ".html"

    try:
        fig.write_image(out_path_png, scale=3)  # requires kaleido
        print(f"Saved: {out_path_png}")
    except Exception as e:
        fig.write_html(out_path_html, include_plotlyjs="cdn")
        print(f"PNG export failed ({type(e).__name__}: {e})")
        print(f"Saved HTML instead: {out_path_html}")
        print("To enable PNG export, install kaleido: pip install -U kaleido")


def main() -> None:
    os.makedirs(VISUALS_DIR, exist_ok=True)

    df = pd.read_excel(FILE_PATH)

    filtered_output_path = os.path.join(
        VISUALS_DIR,
        "2026_Nepal_Election_FPTP_candidates_PARTIES_only.xlsx"
    )

    df = filter_by_parties(
        df=df,
        party_column=PARTY_COL_NAME,
        parties_dict=PARTIES,
        output_path=filtered_output_path
    )

    # Safety check: required columns
    for col in [PARTY_COL_NAME, EDU_COL_NAME]:
        if col not in df.columns:
            raise KeyError(f"Missing required column in Excel: {col}")

    party_items: List[dict] = []

    for party_np, meta in PARTIES.items():
        eng_name = meta.get("eng_name", party_np)
        sign = meta.get("sign", "")
        eng_acronym = meta.get("eng_acronym", "")

        df_party = df[df[PARTY_COL_NAME] == party_np].copy()
        if df_party.empty:
            print(f"Skipping (no rows): {eng_name} / {party_np}")
            continue

        edu_counts = build_education_counts(df_party)
        stats = compute_education_stats(df_party)

        party_items.append(
            {
                "eng_name": eng_name,
                "edu_counts": edu_counts,
                "stats": stats,
                "sign": sign,
                "eng_acronym": eng_acronym,
            }
        )

        fig = make_party_figure(
            eng_name=eng_name,
            sign_icon=sign,
            edu_counts=edu_counts,
            stats=stats,
        )

        filename = f"2026_nepal_election_education_piechart_{eng_name.replace(' ', '_')}.png"
        out_path = os.path.join(VISUALS_DIR, filename)
        save_figure(fig, out_path)

    if party_items:
        composite = make_composite_figure(party_items)
        composite_filename = "2026_nepal_election_education_by_parties.png"
        composite_out_path = os.path.join(VISUALS_DIR, composite_filename)
        save_figure(composite, composite_out_path)


if __name__ == "__main__":
    main()