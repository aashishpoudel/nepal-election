import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
# from matplotlib import rcParams
from nepal_election_constants import *
# # Use a Devanagari-supporting font
# rcParams['font.family'] = 'Noto Sans Devanagari'

font_path = "/Library/Fonts/NotoSansDevanagari-Regular.ttf"
nepali_font = fm.FontProperties(fname=font_path)

# File path to the Excel file
file_path = '/Users/aashishpoudel/Downloads/2022_nepal_house_candidates_enriched_edu.xlsx'

# Read the Excel file
df = pd.read_excel(file_path)

# Filter out 'नेपाली काँग्रेस' from 'राजनीतिक दल / स्वतन्त्र'
selected_party = 'राष्ट्रिय स्वतन्त्र पार्टी'
df_filtered = df[df['राजनीतिक दल / स्वतन्त्र'] == selected_party]

# Normalize label: NA -> Not Available
edu_series = df_filtered['शैक्षिक योग्यता समूह'].fillna("Not Available").replace({"NA": "Not Available"})

# Fixed order you want
order = ["PhD", "Masters", "Bachelors", "Intermediate", "SLC", "<10 class", "Not Available"]

# Count + force the order, keeping missing categories as 0
edu_counts = edu_series.value_counts().reindex(order, fill_value=0)

# (Optional) If you want to remove categories that are 0 for this party:
edu_counts = edu_counts[edu_counts > 0]
# Helper function to display both percentage and raw count on the chart
def label_fmt(pct, all_vals):
    absolute = int(round(pct/100. * sum(all_vals)))
    return f"{pct:.1f}%\n({absolute})"

# Create the colorful pie chart
plt.figure(figsize=(10, 8))
base_colors = list(plt.get_cmap('tab20').colors)

color_list = []
for label in edu_counts.index:
    if label == "Not Available":
        color_list.append("#B0B0B0")  # gray
    else:
        color_list.append(base_colors[len(color_list) % len(base_colors)])

wedges, texts, autotexts = plt.pie(
    edu_counts,
    labels=edu_counts.index,
    autopct=lambda pct: label_fmt(pct, edu_counts),
    startangle=140,
    colors=color_list,
    pctdistance=0.82,
    wedgeprops={'edgecolor': 'white'}
)

# Style text for readability
plt.setp(autotexts, size=10, weight="bold", color="black")
plt.setp(texts, size=11)

plt.title(f'Educational Qualification\n (2026 {PARTIES[selected_party]["eng_name"]} Candidates)', fontsize=15, pad=20)
# plt.title('Educational Qualification\n (२०८२ Nepali Congress Candidates)', fontsize=15, pad=20, fontproperties=nepali_font)
# plt.title('शैक्षिक योग्यता\n (२०८२ नेपाली कांग्रेसका उम्मेदवारहरू)', fontsize=15, pad=20, fontproperties=nepali_font)
plt.axis('equal')

# Save and display the visualization
plt.savefig('edu_piechart_final.png', bbox_inches='tight', dpi=300)
plt.show()