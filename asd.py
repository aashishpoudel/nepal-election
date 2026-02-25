import re
import pandas as pd
import matplotlib.pyplot as plt

# Optional: Nepali Unicode font support (only needed if you put Nepali in title/labels)
# If you don't need Nepali text, you can delete this whole block.
import matplotlib.font_manager as fm

FONT_PATH = "/Library/Fonts/NotoSansDevanagari-Regular.ttf"  # macOS example
try:
    nepali_font = fm.FontProperties(fname=FONT_PATH)
except Exception:
    nepali_font = None


# -----------------------------
# Config
# -----------------------------
file_path = "/Users/aashishpoudel/Downloads/2022_nepal_house_candidates_enriched_edu.xlsx"

party_col = "राजनीतिक दल / स्वतन्त्र"
age_col = "उमेर"

selected_party = "नेपाली काँग्रेस"  # <-- CHANGE THIS to any party in your sheet

# Fixed order (kept together)
ORDER = [
    "Gen Beta",
    "Gen Alpha",
    "Gen Z",
    "Millennials (Gen Y)",
    "Gen X",
    "Baby Boomers",
    "Silent Generation",
    "Not Available",
]


# -----------------------------
# Helpers
# -----------------------------
def to_number(x):
    """Safely convert age to int; return None if not possible."""
    if pd.isna(x):
        return None
    s = str(x).strip()
    if not s:
        return None

    # Try direct numeric conversion
    n = pd.to_numeric(s, errors="coerce")
    if pd.notna(n):
        return int(n)

    # Fallback: extract first number in the string
    m = re.search(r"\d+", s)
    return int(m.group()) if m else None


def age_to_generation(age):
    if age is None:
        return "Not Available"

    if 0 <= age <= 1:
        return "Gen Beta"
    if 2 <= age <= 13:
        return "Gen Alpha"
    if 14 <= age <= 29:
        return "Gen Z"
    if 30 <= age <= 45:
        return "Millennials (Gen Y)"
    if 46 <= age <= 61:
        return "Gen X"
    if 62 <= age <= 80:
        return "Baby Boomers"
    if 81 <= age <= 98:
        return "Silent Generation"

    return "Not Available"


def label_fmt(pct, all_vals):
    absolute = int(round(pct / 100.0 * sum(all_vals)))
    return f"{pct:.1f}%\n({absolute})"


# -----------------------------
# Load + Filter
# -----------------------------
df = pd.read_excel(file_path)

df_filtered = df[df[party_col] == selected_party].copy()

# Numeric age series for stats
ages_numeric = df_filtered[age_col].apply(to_number)
ages_valid = ages_numeric.dropna()

if len(ages_valid) == 0:
    age_min = age_max = age_median = age_mean = None
else:
    age_min = int(ages_valid.min())
    age_max = int(ages_valid.max())
    age_median = float(ages_valid.median())
    age_mean = float(ages_valid.mean())

# Build generation buckets
gen_series = ages_numeric.apply(age_to_generation)

# Count + force the order (kept together)
gen_counts = gen_series.value_counts().reindex(ORDER, fill_value=0)

# Optional: remove 0-count categories to reduce clutter
gen_counts = gen_counts[gen_counts > 0]


# -----------------------------
# Plot
# -----------------------------
plt.figure(figsize=(11, 8))  # a bit wider to make room for the stats text
plt.subplots_adjust(right=0.78)  # leave white space on the right

base_colors = list(plt.get_cmap("tab20").colors)

color_list = []
for label in gen_counts.index:
    if label in ["Not Available", "NA"]:
        color_list.append("#B0B0B0")  # gray
    else:
        color_list.append(base_colors[len(color_list) % len(base_colors)])

wedges, texts, autotexts = plt.pie(
    gen_counts,
    labels=gen_counts.index,
    autopct=lambda pct: label_fmt(pct, gen_counts),
    startangle=140,
    colors=color_list,
    pctdistance=0.82,
    wedgeprops={"edgecolor": "white"},
)

# Style slice labels + % labels
plt.setp(texts, size=11)
plt.setp(autotexts, size=10, weight="bold", color="black")

# Title (use Nepali if you want; if rectangles appear, install a Devanagari font and set nepali_font)
title_text = f"Age Generations\n({selected_party} Candidates)"
if nepali_font:
    plt.title(title_text, fontsize=15, pad=20, fontproperties=nepali_font)
else:
    plt.title(title_text, fontsize=15, pad=20)

plt.axis("equal")

# Sidebar stats text (in the white space)
if age_min is None:
    stats_text = (
        r"Age $\bf{Max}$ - NA" "\n"
        r"Age $\bf{Min}$ - NA" "\n"
        r"Age $\bf{Median}$ - NA" "\n"
        r"Age $\bf{Average}$ - NA"
    )
else:
    stats_text = (
        rf"Age $\bf{{Max}}$ - {age_max}" "\n"
        rf"Age $\bf{{Min}}$ - {age_min}" "\n"
        rf"Age $\bf{{Median}}$ - {int(round(age_median))}" "\n"
        rf"Age $\bf{{Average}}$ - {age_mean:.1f}"
    )

fig = plt.gcf()
if nepali_font:
    fig.text(
        0.82, 0.55,
        stats_text,
        ha="left",
        va="center",
        fontsize=12,
        fontweight="bold",
        fontproperties=nepali_font,
    )
else:
    fig.text(
        0.82, 0.55,
        stats_text,
        ha="left",
        va="center",
        fontsize=12,
        fontweight="bold",
    )

# Save + show
output_png = "age_generation_piechart_with_stats.png"
plt.savefig(output_png, bbox_inches="tight", dpi=300)
plt.show()

print(f"Saved: {output_png}")