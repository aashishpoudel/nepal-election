import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

from nepal_election_constants import *
from nepal_election_base import *
from helper_functions.chart_helpers import *

# (Optional) Nepali font (only needed if you put Nepali text in chart)
font_path = "/Library/Fonts/NotoSansDevanagari-Regular.ttf"
nepali_font = fm.FontProperties(fname=font_path)

FILE_PATH = "./2026_Nepal_Election_FTPT_candidates.xlsx"


# -----------------------------
# Fixed Generation Colors (Always Same)
# -----------------------------
GENERATION_COLORS = {
    "Gen Beta (age 0 to 1)": "#E0FFFF",              # Light Cyan
    "Gen Alpha (age 2 to 13)": "#87CEFA",            # Light Sky Blue
    "Gen Z (age 14 to 29)": "#20B2AA",               # Light Sea Green
    "Millennials (Gen Y) (age 30 to 45)": "#FFD700", # Golden Yellow
    "Gen X (age 46 to 61)": "#FF8C00",               # Dark Orange
    "Baby Boomers (age 62 to 80)": "#4169E1",        # Royal Blue
    "Silent Generation (age 81 to 98)": "#4B0082",   # Indigo
    "Not Available": "#D3D3D3",                      # Light Gray
}


# Fixed order you want (kept together)
ORDER = [
    "Gen Beta (age 0 to 1)",
    "Gen Alpha (age 2 to 13)",
    "Gen Z (age 14 to 29)",
    "Millennials (Gen Y) (age 30 to 45)",
    "Gen X (age 46 to 61)",
    "Baby Boomers (age 62 to 80)",
    "Silent Generation (age 81 to 98)",
    "Not Available",
]


def label_fmt(pct, all_vals):
    absolute = int(round(pct / 100.0 * sum(all_vals)))
    # return f"{pct:.1f}%\n({absolute})"
    return f"{pct:.1f}%"


def build_party_pie_chart(df: pd.DataFrame, party_name_np: str) -> None:
    """Build + save the age-generation pie chart for a single party."""

    # -----------------------------
    # 1) Filter by Party
    # -----------------------------
    df_filtered = df[df["राजनीतिक दल / स्वतन्त्र"] == party_name_np].copy()

    # -----------------------------
    # 2) Build Age Generation Group + stats
    # -----------------------------
    ages_numeric = df_filtered["उमेर"].apply(to_number)
    ages_valid = ages_numeric.dropna()

    if len(ages_valid) == 0:
        age_min = age_max = age_median = age_mean = None
    else:
        age_min = int(ages_valid.min())
        age_max = int(ages_valid.max())
        age_median = float(ages_valid.median())
        age_mean = float(ages_valid.mean())

    nepal_election_processor = NepalElectionDataProcessor()
    age_series = df_filtered["उमेर"].apply(to_number).apply(nepal_election_processor.age_to_generation)

    # Count + force order
    age_counts = age_series.value_counts().reindex(ORDER, fill_value=0)
    # Optional: drop categories with 0 for cleaner chart
    age_counts = age_counts[age_counts > 0]

    # -----------------------------
    # 3) Pie Chart
    # -----------------------------
    plt.figure(figsize=(10, 8))
    _ = list(plt.get_cmap("tab20").colors)  # kept to retain previous behavior/deps

    # Colors based on fixed generation mapping
    color_list = [GENERATION_COLORS[label] for label in age_counts.index]

    wedges, texts, autotexts = plt.pie(
        age_counts,
        labels=age_counts.index,
        autopct=lambda pct: label_fmt(pct, age_counts),
        startangle=140,
        colors=color_list,
        pctdistance=0.82,
        wedgeprops={"edgecolor": "white"},
    )

    plt.setp(autotexts, size=10, weight="bold", color="black")
    plt.setp(texts, size=11)

    # Title (English). If you switch to Nepali title, add: fontproperties=nepali_font
    eng_name = PARTIES.get(party_name_np, {}).get("eng_name", party_name_np)
    plt.title(
        f"Age Generations\n(2026 $\\bf{{{eng_name}}}$ Candidates - FPTP)\n",
        fontsize=15,
        pad=20,
    )

    if age_min is None:
        stats_text = (
            r"Age $\bf{Max}$ - NA" "\n"
            r"Age $\bf{Min}$ - NA" "\n"
            r"Age $\bf{Median}$ - NA" "\n"
            r"Age $\bf{Average}$ - NA"
        )
    else:
        age_median = int(round(age_median))
        age_mean = int(round(age_mean))
        stats_text = (
            rf"Age $\bf{{Max}}$ - {age_max}" "\n"
            rf"Age $\bf{{Min}}$ - {age_min}" "\n"
            rf"Age $\bf{{Median}}$ - $\bf{{{age_median}}}$" "\n"
            rf"Age $\bf{{Average}}$ - $\bf{{{age_mean}}}$" "\n\n"
            rf"Total Candidates - {len(ages_numeric)}"
        )

    fig = plt.gcf()
    fig.text(
        0.82, 0.55,
        stats_text,
        ha="left",
        va="center",
        fontsize=12,
    )

    # -----------------------------
    # Footer (bottom right)
    # -----------------------------
    footer_text = "Design: visualnepal.com\nData Source: election.gov.np"
    fig.text(
        0.98, 0.02,                 # (x, y) bottom-right corner
        footer_text,
        ha="right",
        va="bottom",
        fontsize=9,
        color="gray",
    )

    plt.axis("equal")
    # Ensure visuals folder exists (repo root level)
    VISUALS_DIR = "visuals"
    os.makedirs(VISUALS_DIR, exist_ok=True)

    # Build filename
    filename = f"2026_nepal_election_age_generation_piechart_{eng_name.replace(' ', '_')}.png"

    # Full output path
    out_path = os.path.join(VISUALS_DIR, filename)

    # Save
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"Saved: {out_path}")

    plt.show()
    plt.close(fig)

if __name__ == "__main__":
    # Read the Excel file once
    df = pd.read_excel(FILE_PATH)

    # Loop through ALL parties defined in nepal_election_constants.py
    # (Skips any party not present in the Excel, without breaking the run.)
    parties_in_data = set(df["राजनीतिक दल / स्वतन्त्र"].dropna().unique().tolist())
    for party_np in PARTIES.keys():
        if party_np not in parties_in_data:
            continue
        build_party_pie_chart(df, party_np)