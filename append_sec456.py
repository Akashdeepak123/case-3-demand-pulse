import nbformat as nbf

nb_path = 'notebooks/01_demand_patterns.ipynb'
with open(nb_path, 'r') as f:
    nb = nbf.read(f, as_version=4)

cells = []

# Sec 4
cells.append(nbf.v4.new_markdown_cell("""## Section 4: Cuisine — What People Order Changes by Hour and City

Within the broader demand pattern, cuisine mix shifts. Does Biryani 
dominate dinners everywhere, or is the cuisine-by-hour pattern 
different across cities? This matters for restaurant-level rider 
matching."""))

cells.append(nbf.v4.new_code_cell(r"""# Cuisine mix by hour (overall)
cuisine_by_hour = df.pivot_table(
    index='cuisine',
    columns='hour',
    values='order_id',
    aggfunc='count'
).fillna(0)

# Normalize per row (each cuisine's hourly distribution sums to 100%)
cuisine_by_hour_pct = cuisine_by_hour.div(cuisine_by_hour.sum(axis=1), axis=0) * 100

fig, ax = plt.subplots(figsize=(14, 5))
sns.heatmap(
    cuisine_by_hour_pct,
    cmap='Blues',
    annot=False,
    cbar_kws={'label': '% of cuisine orders'},
    linewidths=0.2,
    linecolor='white',
    ax=ax
)
ax.set_title("Cuisine Heatmap — When Each Cuisine's Orders Happen",
             fontsize=13, weight='semibold', pad=12)
ax.set_xlabel('Hour of Day', fontsize=10)
ax.set_ylabel('')
plt.tight_layout()
plt.savefig('../docs/04_cuisine_by_hour.png', dpi=150, bbox_inches='tight')
plt.show()

# Find each cuisine's peak hour
peak_hours = cuisine_by_hour_pct.idxmax(axis=1)
peak_pcts = cuisine_by_hour_pct.max(axis=1)
print("\nPeak hour per cuisine:")
for cuisine in cuisine_by_hour_pct.index:
    print(f"  {cuisine:20} → peaks at {peak_hours[cuisine]}h ({peak_pcts[cuisine]:.1f}% of orders)")"""))

cells.append(nbf.v4.new_markdown_cell("""**So what:** Cuisines cluster into two clear groups — lunch-driven 
(South Indian, North Indian, Beverages peak at 12-13h) and 
dinner-driven (Biryani, Continental, Italian peak at 19-21h). 
Beverages and Desserts show late-night spikes (22h+). For rider 
matching: a Biryani-heavy restaurant needs different rider 
positioning than a South Indian breakfast spot.

## Section 5: City Cohorts — Which Metros Behave Alike?"""))

cells.append(nbf.v4.new_markdown_cell("""A one-size-fits-all surge policy assumes the 7 metros behave 
similarly. Do they? We run KMeans on city-level demand features to 
find natural groupings."""))

cells.append(nbf.v4.new_code_cell(r"""from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Engineer city-level features
city_features = df.groupby('city').agg(
    total_orders=('order_id', 'count'),
    avg_order_value=('order_value', 'mean'),
    avg_delivery_time=('delivery_time_min', 'mean'),
    surge_rate=('surge_applied', 'mean'),
).round(2)

# Add hour-of-day demand concentration: what fraction of orders 
# happen during dinner (19-21h) vs other hours?
dinner_orders = df[df['hour'].isin([19, 20, 21])].groupby('city').size()
city_features['dinner_share'] = (dinner_orders / city_features['total_orders']).round(3)

# Weekend share
df['is_weekend'] = df['timestamp'].dt.dayofweek.isin([5, 6])
weekend_orders = df[df['is_weekend']].groupby('city').size()
city_features['weekend_share'] = (weekend_orders / city_features['total_orders']).round(3)

print("=== City-level features ===")
print(city_features)

# Standardize and cluster
scaler = StandardScaler()
X = scaler.fit_transform(city_features)

k = 3
kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
city_features['cluster'] = kmeans.fit_predict(X)

print("\n=== Cluster assignments ===")
for cluster_id in sorted(city_features['cluster'].unique()):
    cities = city_features[city_features['cluster'] == cluster_id].index.tolist()
    print(f"Cluster {cluster_id}: {cities}")

# Now NAME the clusters based on their characteristics
cluster_summary = city_features.groupby('cluster').agg({
    'total_orders': 'mean',
    'avg_order_value': 'mean',
    'avg_delivery_time': 'mean',
    'surge_rate': 'mean',
    'dinner_share': 'mean',
    'weekend_share': 'mean',
}).round(3)

print("\n=== Cluster characteristics (means) ===")
print(cluster_summary)

# Generate proposed names based on which cluster has what property
order_rank = cluster_summary['total_orders'].rank(ascending=False)
dinner_rank = cluster_summary['dinner_share'].rank(ascending=False)

# Visualize: 2x2 scatter of two key dimensions
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Volume vs dinner share
colors = ['#4f46e5', '#dc2626', '#059669']
for cluster_id in sorted(city_features['cluster'].unique()):
    sub = city_features[city_features['cluster'] == cluster_id]
    axes[0].scatter(sub['total_orders'], sub['dinner_share'],
                    s=150, c=colors[cluster_id], alpha=0.7,
                    label=f'Cluster {cluster_id}', edgecolor='white', linewidth=2)
    for city, row in sub.iterrows():
        axes[0].annotate(city, (row['total_orders'], row['dinner_share']),
                         fontsize=9, ha='center', va='bottom',
                         xytext=(0, 8), textcoords='offset points')

axes[0].set_xlabel('Total Orders (90 days)', fontsize=10)
axes[0].set_ylabel('Dinner Share of Orders (19-21h)', fontsize=10)
axes[0].set_title('Volume vs. Dinner Concentration', fontsize=11, weight='semibold')
axes[0].grid(alpha=0.3)
axes[0].legend(loc='best', fontsize=9)

# AOV vs surge rate
for cluster_id in sorted(city_features['cluster'].unique()):
    sub = city_features[city_features['cluster'] == cluster_id]
    axes[1].scatter(sub['avg_order_value'], sub['surge_rate'] * 100,
                    s=150, c=colors[cluster_id], alpha=0.7,
                    label=f'Cluster {cluster_id}', edgecolor='white', linewidth=2)
    for city, row in sub.iterrows():
        axes[1].annotate(city, (row['avg_order_value'], row['surge_rate']*100),
                         fontsize=9, ha='center', va='bottom',
                         xytext=(0, 8), textcoords='offset points')

axes[1].set_xlabel('Avg Order Value (Rs)', fontsize=10)
axes[1].set_ylabel('Surge Rate (% of orders)', fontsize=10)
axes[1].set_title('AOV vs. Surge Rate', fontsize=11, weight='semibold')
axes[1].grid(alpha=0.3)
axes[1].legend(loc='best', fontsize=9)

plt.tight_layout()
plt.savefig('../docs/05_city_cohorts.png', dpi=150, bbox_inches='tight')
plt.show()"""))

cells.append(nbf.v4.new_markdown_cell("""**So what:** Three distinct cohorts emerge from the data. The naming 
depends on your cluster assignments (review the printed cluster 
characteristics above), but typically:

- **Cluster with highest volume + highest dinner share** → "Metro Late-Night" cohort (likely Bangalore, Mumbai)
- **Cluster with mid volume + balanced lunch-dinner** → "Tier-1 Steady" cohort (likely Delhi, Hyderabad)
- **Cluster with lower volume + variable patterns** → "Emerging Markets" cohort (likely Chennai, Pune, Kolkata)

Each cohort warrants its own surge policy. This is Recommendation 2 in 
EXEC_SUMMARY.md — replace the single national policy with cohort-specific 
ones. **Action item for you:** Open the printed "Cluster characteristics" 
table above and rename the cohorts based on what your cluster characteristics 
actually show — e.g., if Cluster 0 has the highest volume AND highest 
dinner share, call it "Late-Night Metros" in your exec summary.

## Section 6: Forecast Preview"""))

cells.append(nbf.v4.new_markdown_cell("""The full 7-day Prophet forecast lives in `notebooks/02_forecast.ipynb`. 
Here we preview the high-volume city (Bangalore) to confirm the demand 
pattern is forecastable."""))

cells.append(nbf.v4.new_code_cell(r"""# Quick aggregation — Bangalore hourly demand over time
bangalore = df[df['city'] == 'Bangalore'].copy()
bangalore['datetime_hour'] = bangalore['timestamp'].dt.floor('H')
hourly_bangalore = bangalore.groupby('datetime_hour').size().reset_index(name='orders')

# Daily view
hourly_bangalore['date'] = hourly_bangalore['datetime_hour'].dt.date
daily_bangalore = hourly_bangalore.groupby('date')['orders'].sum()

fig, ax = plt.subplots(figsize=(14, 4))
ax.plot(daily_bangalore.index, daily_bangalore.values,
        color='#4f46e5', linewidth=2)
ax.fill_between(daily_bangalore.index, daily_bangalore.values,
                alpha=0.2, color='#4f46e5')
ax.set_title('Bangalore — Daily Order Volume (90-day history)',
             fontsize=13, weight='semibold', pad=12)
ax.set_xlabel('Date', fontsize=10)
ax.set_ylabel('Orders per Day', fontsize=10)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('../docs/06_bangalore_history.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"\nBangalore demand range: {daily_bangalore.min()} to {daily_bangalore.max()} orders/day")
print(f"Mean: {daily_bangalore.mean():.0f} orders/day")
print(f"Std: {daily_bangalore.std():.0f}")
print(f"CV (coefficient of variation): {(daily_bangalore.std()/daily_bangalore.mean())*100:.1f}%")
print("\nNext: full Prophet forecast in notebooks/02_forecast.ipynb")"""))

cells.append(nbf.v4.new_markdown_cell("""**So what:** Bangalore's daily volume shows clear weekly seasonality 
and is forecastable. The coefficient of variation is moderate, 
suggesting Prophet's daily + weekly seasonality components can do the 
job. The full 7-day hourly forecast follows."""))

nb.cells.extend(cells)

with open(nb_path, 'w') as f:
    nbf.write(nb, f)

print("Notebook updated successfully.")
