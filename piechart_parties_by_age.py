import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from nepal_election_constants import *

# (Optional) Nepali font (only needed if you put Nepali text in chart)
font_path = "/Library/Fonts/NotoSansDevanagari-Regular.ttf"
nepali_font = fm.FontProperties(fname=font_path)

# File path to the Excel file
file_path = "/Users/aashishpoudel/Downloads/2022_nepal_house_candidates_enriched_edu.xlsx"

# Read the Excel file
df = pd.read_excel(file_path)

# -----------------------------
# 1) Filter by Party
# -----------------------------
selected_party = 'राष्ट्रिय स्वतन्त्र पार्टी'   # नेपाल कम्युनिष्ट पार्टी (एकीकृत मार्क्सवादी लेनिनवादी), नेपाली काँग्रेस, नेपाली कम्युनिष्ट पार्टी, राष्ट्रिय स्वतन्त्र पार्टी
df_filtered = df[df["राजनीतिक दल / स्वतन्त्र"] == selected_party].copy()
print(f"{PARTIES.keys()}")

# -----------------------------
# 2) Build Age Generation Group
# -----------------------------
def to_number(x):
    """Safely convert age to int; return None if not possible."""
    if pd.isna(x):
        return None
    s = str(x).strip()
    if not s:
        return None
    # Extract first number if the cell contains extra text
    m = pd.to_numeric(s, errors="coerce")
    if pd.notna(m):
        return int(m)
    # fallback: regex extract
    import re
    mm = re.search(r"\d+", s)
    return int(mm.group()) if mm else None


def age_to_generation(age):
    if age is None:
        return "Not Available"
    # Your requested bins:
    if 0 <= age <= 1:
        return "Gen Beta (age 0 to 1)"
    if 2 <= age <= 13:
        return "Gen Alpha (age 2 to 13)"
    if 14 <= age <= 29:
        return "Gen Z (age 14 to 29)"
    if 30 <= age <= 45:
        return "Millennials (Gen Y) (age 30 to 45)"
    if 46 <= age <= 61:
        return "Gen X (age 46 to 61)"
    if 62 <= age <= 80:
        return "Baby Boomers (age 62 to 80)"
    if 81 <= age <= 98:
        return "Silent Generation (age 81 to 98)"
    # Anything outside your defined ranges:
    return "Not Available"


ages_numeric = df_filtered["उमेर"].apply(to_number)
ages_valid = ages_numeric.dropna()

if len(ages_valid) == 0:
    age_min = age_max = age_median = age_mean = None
else:
    age_min = int(ages_valid.min())
    age_max = int(ages_valid.max())
    age_median = float(ages_valid.median())
    age_mean = float(ages_valid.mean())


age_series = df_filtered["उमेर"].apply(to_number).apply(age_to_generation)

# Fixed order you want (kept together)
order = [
    "Gen Beta (age 0 to 1)",
    "Gen Alpha (age 2 to 13)",
    "Gen Z (age 14 to 29)",
    "Millennials (Gen Y) (age 30 to 45)",
    "Gen X (age 46 to 61)",
    "Baby Boomers (age 62 to 80)",
    "Silent Generation (age 81 to 98)",
    "Not Available",
]

# Count + force order
age_counts = age_series.value_counts().reindex(order, fill_value=0)

# Optional: drop categories with 0 for cleaner chart
age_counts = age_counts[age_counts > 0]

# -----------------------------
# 3) Pie Chart
# -----------------------------
def label_fmt(pct, all_vals):
    absolute = int(round(pct / 100.0 * sum(all_vals)))
    # return f"{pct:.1f}%\n({absolute})"
    return f"{pct:.1f}%"

plt.figure(figsize=(10, 8))
base_colors = list(plt.get_cmap("tab20").colors)

color_list = []
for label in age_counts.index:
    if label == "Not Available":
        color_list.append("#B0B0B0")  # gray for NA
    else:
        color_list.append(base_colors[len(color_list) % len(base_colors)])

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
plt.title(
    f"Age Generations\n(2026 {PARTIES[selected_party]['eng_name']} Candidates)\n",
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
    stats_text = (
        rf"Age $\bf{{Max}}$ - {age_max}" "\n"
        rf"Age $\bf{{Min}}$ - {age_min}" "\n"
        rf"Age $\bf{{Median}}$ - {int(round(age_median))}" "\n"
        rf"Age $\bf{{Average}}$ - {age_mean:.1f}"
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
    ha="right",                 # align right
    va="bottom",                # align to bottom
    fontsize=9,
    color="gray"
)


plt.axis("equal")
plt.savefig(f"2026_nepal_election_age_generation_piechart_{PARTIES[selected_party]['eng_name'].replace(" ", "_")}.png", bbox_inches="tight", dpi=300)
plt.show()