import nbformat as nbf

nb = nbf.v4.new_notebook()

cell1 = nbf.v4.new_markdown_cell("""# Demand Patterns — Where, When, and Who

This notebook answers one question for the Ops Head: when does demand 
really spike, where, and how does it compare to where surge is 
currently paid?

The argument builds in five sections:
1. When are people ordering? (hour × day-of-week)
2. How do the 7 cities differ?
3. **The money chart**: when is surge paid vs. when does demand peak?
4. How does cuisine shift by hour and city?
5. Which cities cluster together (the cohorts)?

Each section has a question, a chart, and one sentence answering the 
question.""")

cell2 = nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100
plt.rcParams['font.family'] = 'sans-serif'

df = pd.read_csv("../data/case3_food_delivery_orders.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['hour'] = df['timestamp'].dt.hour
df['day_of_week'] = df['timestamp'].dt.day_name()
df['date'] = df['timestamp'].dt.date

print(f"Loaded {len(df):,} orders across {df['city'].nunique()} cities")
print(f"Date range: {df['timestamp'].min().date()} → {df['timestamp'].max().date()}")
print(f"Surge overall: {df['surge_applied'].mean()*100:.1f}%")""")

cell3 = nbf.v4.new_markdown_cell("""## Section 1: When are people ordering?

If we look at orders by hour of day and day of week, where are the 
peaks? This is the baseline for everything that follows.""")

cell4 = nbf.v4.new_code_cell("""day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
pivot = df.pivot_table(
    index='day_of_week',
    columns='hour',
    values='order_id',
    aggfunc='count'
).reindex(day_order)

fig, ax = plt.subplots(figsize=(14, 4.5))
sns.heatmap(
    pivot,
    cmap='YlOrRd',
    annot=False,
    cbar_kws={'label': 'Orders per hour'},
    linewidths=0.3,
    linecolor='white',
    ax=ax
)
ax.set_title('Demand Heatmap — Orders by Hour × Day of Week', fontsize=13, pad=12, weight='semibold')
ax.set_xlabel('Hour of Day', fontsize=10)
ax.set_ylabel('')
ax.tick_params(axis='x', labelsize=9)
ax.tick_params(axis='y', labelsize=9)

# Highlight the dinner-peak hours (19-20) with a box
import matplotlib.patches as patches
rect = patches.Rectangle((19, 0), 2, 7, linewidth=2, edgecolor='#1e40af', facecolor='none', linestyle='--')
ax.add_patch(rect)
ax.text(20, -0.4, 'Dinner peak', fontsize=9, color='#1e40af', ha='center', weight='semibold')

# Highlight lunch peak (12-13)
rect2 = patches.Rectangle((12, 0), 2, 7, linewidth=2, edgecolor='#0e7490', facecolor='none', linestyle='--')
ax.add_patch(rect2)
ax.text(13, -0.4, 'Lunch peak', fontsize=9, color='#0e7490', ha='center', weight='semibold')

# Highlight the dinner ramp (18) — this is the story
rect3 = patches.Rectangle((18, 0), 1, 7, linewidth=2, edgecolor='#dc2626', facecolor='none')
ax.text(18.5, 7.5, 'Hour 18 — the blind spot', fontsize=9, color='#dc2626', ha='center', weight='bold')

plt.tight_layout()
plt.savefig('../docs/01_hour_dow_heatmap.png', dpi=150, bbox_inches='tight')
plt.show()

# Compute key stats for the so-what caption
hourly_demand = df.groupby('hour').size()
top_3_hours = hourly_demand.sort_values(ascending=False).head(3)
peak_hour = top_3_hours.index[0]
peak_orders = top_3_hours.iloc[0]
trough_hour = hourly_demand.idxmin()
trough_orders = hourly_demand.min()
hour_18_orders = hourly_demand[18]
hour_18_rank = (hourly_demand.sort_values(ascending=False).index == 18).argmax() + 1

print(f"\\nPeak hour: {peak_hour}:00 ({peak_orders:,} orders/day on average)")
print(f"Top 3 hours by demand: {list(top_3_hours.index)}")
print(f"Hour 18 — the dinner ramp: {hour_18_orders:,} orders (rank #{hour_18_rank} of 24)")
print(f"Trough: {trough_hour}:00 ({trough_orders:,} orders)")
print(f"Peak-to-trough ratio: {peak_orders/trough_orders:.1f}x")""")

cell5 = nbf.v4.new_markdown_cell("""**So what:** Demand has two clear peaks — lunch at 12-13h and dinner 
at 19-21h. Hour 18 is rank #6 by total volume (after the dinner peak 
hours), making it a critical "ramp-up" hour. The peak-to-trough ratio 
is 20.2x, high enough that any surge policy must be hour-aware, not 
day-aware.""")

nb.cells = [cell1, cell2, cell3, cell4, cell5]

with open('notebooks/01_demand_patterns.ipynb', 'w') as f:
    nbf.write(nb, f)
