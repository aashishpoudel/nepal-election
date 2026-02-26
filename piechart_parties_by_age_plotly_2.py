import os
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

from nepal_election_constants import PARTIES
from nepal_election_base import NepalElectionDataProcessor
from helper_functions.chart_helpers import to_number

# -----------------------------
# Config
# -----------------------------
FILE_PATH = "./2026_Nepal_Election_FTPT_candidates.xlsx"
VISUALS_DIR = "visuals"

# Fixed order you want (kept together)
GEN_ORDER = [
    "Gen Beta (age 0 to 1)",
    "Gen Alpha (age 2 to 13)",
    "Gen Z (age 14 to 29)",
    "Millennials (Gen Y) (age 30 to 45)",
    "Gen X (age 46 to 61)",
    "Baby Boomers (age 62 to 80)",
    "Silent Generation (age 81 to 98)",
    "Not Available",
]

# Fixed Generation Colors (Always Same)
GENERATION_COLORS = {
    "Gen Beta (age 0 to 1)": "#E0FFFF",              # Light Cyan
    "Gen Alpha (age 2 to 13)": "#87CEFA",            # Light Sky Blue
    "Gen Z (age 14 to 29)": "#20B2AA",               # Light Sea Green
    "Millennials (Gen Y) (age 30 to 45)": "#ADD0E6", # Light Blue
    "Gen X (age 46 to 61)": "#FFF59D",               # Light Yellow
    "Baby Boomers (age 62 to 80)": "#FFB3B3",        # Light Red
    "Silent Generation (age 81 to 98)": "#4B0082",   # Indigo
    "Not Available": "#D3D3D3",                      # Light Gray
}

FOOTER_TEXT = "Design: visualnepal.com<br>Data Source: election.gov.np"


def compute_age_stats(df_party: pd.DataFrame) -> dict:
    """Compute age stats (min/max/median/mean) from the party subset."""
    ages_numeric = df_party["उमेर"].apply(to_number)
    ages_valid = ages_numeric.dropna()

    if len(ages_valid) == 0:
        return {"min": None, "max": None, "median": None, "mean": None}

    return {
        "min": int(ages_valid.min()),
        "max": int(ages_valid.max()),
        # median: whole number (per your requirement)
        "median": int(round(float(ages_valid.median()))),
        "mean": float(ages_valid.mean()),
    }


def build_age_counts(df_party: pd.DataFrame) -> pd.Series:
    """Convert ages to generations and return counts in fixed order."""
    processor = NepalElectionDataProcessor()
    age_series = df_party["उमेर"].apply(to_number).apply(processor.age_to_generation)

    counts = age_series.value_counts().reindex(GEN_ORDER, fill_value=0)
    # Optional: drop categories with 0 for cleaner chart
    counts = counts[counts > 0]
    return counts


def make_party_figure(eng_name: str, age_counts: pd.Series, stats: dict) -> go.Figure:
    labels = list(age_counts.index)
    values = list(age_counts.values)
    colors = [GENERATION_COLORS.get(lbl, "#CCCCCC") for lbl in labels]

    # Constrain the pie to the left portion to create right-side whitespace for legend + stats
    fig = go.Figure(
        data=[
            go.Pie(
                domain=dict(x=[0.0, 0.62], y=[0.0, 1.0]),
                labels=labels,
                values=values,
                sort=False,              # keep your order
                direction="clockwise",
                rotation=140,            # similar to matplotlib startangle
                marker=dict(colors=colors, line=dict(color="white", width=1)),
                textinfo="percent",
                texttemplate="%{percent:.1%}",
                textfont=dict(size=12),
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
            )
        ]
    )

    # Title with proper line breaks + bold party name (Unicode-safe)
    fig.update_layout(
        title=dict(
            text=f"Age Generations<br>(2026 <b>{eng_name}</b> Candidates - FPTP)",
            x=0.5,
            xanchor="center",
            yanchor="top",
            font=dict(size=22),
        ),
        showlegend=True,
        # Legend stays with this pie (inside the same figure), positioned in the whitespace area
        legend=dict(
            orientation="v",
            x=0.66,
            y=0.98,
            xanchor="left",
            yanchor="top",
            font=dict(size=12),
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="rgba(0,0,0,0.15)",
            borderwidth=1,
        ),
        margin=dict(l=60, r=260, t=110, b=90),
    )

    # Stats (right-side whitespace). Only Mean/Median are bolded (label + value).
    if stats["min"] is None:
        stats_html = (
            "Age Max - NA<br>"
            "Age Min - NA<br>"
            "<b>Age Median - NA</b><br>"
            "<b>Age Average - NA</b>"
        )
    else:
        stats_html = (
            f"Age Max - {stats['max']}<br>"
            f"Age Min - {stats['min']}<br>"
            f"<b>Age Median - {stats['median']}</b><br>"
            f"<b>Age Average - {stats['mean']:.1f}</b>"
        )

    fig.add_annotation(
        x=0.66,
        y=0.55,
        xref="paper",
        yref="paper",
        text=stats_html,
        showarrow=False,
        align="left",
        font=dict(size=14, color="black"),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="rgba(0,0,0,0.15)",
        borderwidth=1,
        borderpad=8,
    )

    # Footer bottom-right (as far down/right as Plotly margins allow)
    fig.add_annotation(
        x=1.0,
        y=-0.15,
        xref="paper",
        yref="paper",
        text=FOOTER_TEXT,
        showarrow=False,
        xanchor="right",
        yanchor="bottom",
        font=dict(size=11, color="gray"),
    )

    return fig


def save_figure(fig: go.Figure, out_path_png: str) -> None:
    """Save PNG if possible; otherwise save HTML as a fallback."""
    out_path_png = str(out_path_png)
    out_path_html = os.path.splitext(out_path_png)[0] + ".html"

    try:
        # Requires kaleido in most environments: pip install -U kaleido
        fig.write_image(out_path_png, scale=3)
        print(f"Saved: {out_path_png}")
    except Exception as e:
        # Fallback: always works
        fig.write_html(out_path_html, include_plotlyjs="cdn")
        print(f"PNG export failed ({type(e).__name__}: {e})")
        print(f"Saved HTML instead: {out_path_html}")
        print("To enable PNG export, install kaleido: pip install -U kaleido")


def main() -> None:
    os.makedirs(VISUALS_DIR, exist_ok=True)

    df = pd.read_excel(FILE_PATH)

    # Generate for every party in PARTIES (skip if party not present in the Excel)
    for party_np, meta in PARTIES.items():
        eng_name = meta.get("eng_name", party_np)

        df_party = df[df["राजनीतिक दल / स्वतन्त्र"] == party_np].copy()
        if df_party.empty:
            print(f"Skipping (no rows): {eng_name} / {party_np}")
            continue

        age_counts = build_age_counts(df_party)
        stats = compute_age_stats(df_party)

        fig = make_party_figure(eng_name=eng_name, age_counts=age_counts, stats=stats)

        filename = f"2026_nepal_election_age_generation_piechart_{eng_name.replace(' ', '_')}.png"
        out_path = os.path.join(VISUALS_DIR, filename)

        save_figure(fig, out_path)


if __name__ == "__main__":
    main()
