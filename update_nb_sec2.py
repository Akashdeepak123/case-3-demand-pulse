import pandas as pd
import numpy as np
import nbformat as nbf

# 1. Compute stats
df = pd.read_csv("data/case3_food_delivery_orders.csv")

city_stats = df.groupby('city').agg(
    total_orders=('order_id', 'count'),
    avg_order_value=('order_value', 'mean'),
    avg_delivery_time=('delivery_time_min', 'mean'),
    surge_rate=('surge_applied', 'mean')
).round(2).sort_values('total_orders', ascending=False)

volume_ratio = city_stats['total_orders'].max() / city_stats['total_orders'].min()
aov_spread = city_stats['avg_order_value'].max() - city_stats['avg_order_value'].min()
surge_spread = (city_stats['surge_rate'].max() - city_stats['surge_rate'].min()) * 100
delivery_spread = city_stats['avg_delivery_time'].max() - city_stats['avg_delivery_time'].min()
surge_avg = city_stats['surge_rate'].mean() * 100

print(f"Volume ratio: {volume_ratio:.1f}x")
print(f"AOV spread: {aov_spread:.0f}")
print(f"Delivery time spread: {delivery_spread:.1f}")
print(f"Surge rate spread: {surge_spread:.1f}")
print(f"Surge average: {surge_avg:.1f}")

# 2. Update Notebook
nb_path = 'notebooks/01_demand_patterns.ipynb'
with open(nb_path, 'r') as f:
    nb = nbf.read(f, as_version=4)

cell_md1 = nbf.v4.new_markdown_cell("""## Section 2: How do the 7 cities differ?

We have 7 metros. Are they running the same business with different 
volumes, or are they fundamentally different operations? A 
one-size-fits-all surge policy assumes the former.""")

cell_code = nbf.v4.new_code_cell("""city_stats = df.groupby('city').agg(
    total_orders=('order_id', 'count'),
    avg_order_value=('order_value', 'mean'),
    avg_delivery_time=('delivery_time_min', 'mean'),
    surge_rate=('surge_applied', 'mean')
).round(2).sort_values('total_orders', ascending=False)

print(city_stats)

# Visualize as small multiples
fig, axes = plt.subplots(1, 4, figsize=(16, 4))
fig.suptitle('Seven Metros — Four Dimensions At A Glance', fontsize=13, weight='semibold', y=1.02)

# 1. Order volume
axes[0].barh(city_stats.index, city_stats['total_orders'], color='#4f46e5')
axes[0].set_title('Total orders (90 days)', fontsize=10, weight='semibold')
axes[0].invert_yaxis()
axes[0].grid(axis='x', alpha=0.3)
for i, v in enumerate(city_stats['total_orders']):
    axes[0].text(v + 100, i, f'{v:,}', va='center', fontsize=8, color='#4f46e5')

# 2. AOV
axes[1].barh(city_stats.index, city_stats['avg_order_value'], color='#059669')
axes[1].set_title('Avg order value (₹)', fontsize=10, weight='semibold')
axes[1].invert_yaxis()
axes[1].set_yticklabels([])
axes[1].grid(axis='x', alpha=0.3)
for i, v in enumerate(city_stats['avg_order_value']):
    axes[1].text(v + 5, i, f'₹{v:.0f}', va='center', fontsize=8, color='#059669')

# 3. Delivery time
axes[2].barh(city_stats.index, city_stats['avg_delivery_time'], color='#d97706')
axes[2].set_title('Avg delivery time (min)', fontsize=10, weight='semibold')
axes[2].invert_yaxis()
axes[2].set_yticklabels([])
axes[2].grid(axis='x', alpha=0.3)
for i, v in enumerate(city_stats['avg_delivery_time']):
    axes[2].text(v + 0.3, i, f'{v:.1f}', va='center', fontsize=8, color='#d97706')

# 4. Surge rate
axes[3].barh(city_stats.index, city_stats['surge_rate'] * 100, color='#dc2626')
axes[3].set_title('Surge rate (% of orders)', fontsize=10, weight='semibold')
axes[3].invert_yaxis()
axes[3].set_yticklabels([])
axes[3].grid(axis='x', alpha=0.3)
for i, v in enumerate(city_stats['surge_rate'] * 100):
    axes[3].text(v + 0.3, i, f'{v:.1f}%', va='center', fontsize=8, color='#dc2626')

plt.tight_layout()
plt.savefig('../docs/02_city_differences.png', dpi=150, bbox_inches='tight')
plt.show()

# Quick spread stats for the so-what
volume_ratio = city_stats['total_orders'].max() / city_stats['total_orders'].min()
aov_spread = city_stats['avg_order_value'].max() - city_stats['avg_order_value'].min()
surge_spread = (city_stats['surge_rate'].max() - city_stats['surge_rate'].min()) * 100
delivery_spread = city_stats['avg_delivery_time'].max() - city_stats['avg_delivery_time'].min()

print(f"\\n--- Spreads ---")
print(f"Volume ratio (largest/smallest): {volume_ratio:.1f}x")
print(f"AOV spread: ₹{aov_spread:.0f}")
print(f"Delivery time spread: {delivery_spread:.1f} min")
print(f"Surge rate spread: {surge_spread:.1f} percentage points")
print(f"\\nTop volume city (forecast target): {city_stats.index[0]}")""")

so_what_text = f"""**So what:** Volume varies {volume_ratio:.1f}x across cities, but AOV, delivery 
time, and surge rate are remarkably flat. The surge rate is 
~{surge_avg:.0f}% everywhere — implying a uniform policy that ignores city-level 
differences. The volume ratio justifies city-specific rider planning; 
the flat surge rate suggests we're not doing it."""

cell_md2 = nbf.v4.new_markdown_cell(so_what_text)

nb.cells.extend([cell_md1, cell_code, cell_md2])

with open(nb_path, 'w') as f:
    nbf.write(nb, f)

print("Notebook updated successfully.")
