import nbformat as nbf

nb_path = 'notebooks/01_demand_patterns.ipynb'
with open(nb_path, 'r') as f:
    nb = nbf.read(f, as_version=4)

cell_md1 = nbf.v4.new_markdown_cell("""## Section 3: The Money Chart — When Is Surge Paid vs. When Does Demand Peak?

If surge is meant to incentivize riders during peak demand, the surge 
curve should track the demand curve. Does it?""")

cell_code = nbf.v4.new_code_cell(r"""hourly = df.groupby('hour').agg(
    orders=('order_id', 'count'),
    surge_count=('surge_applied', 'sum')
)
hourly['surge_rate'] = hourly['surge_count'] / hourly['orders'] * 100
hourly['demand_pct_of_day'] = hourly['orders'] / hourly['orders'].sum() * 100

# Two-panel figure
fig, (ax1, ax3) = plt.subplots(2, 1, figsize=(14, 7),
                                gridspec_kw={'height_ratios': [3, 1]},
                                sharex=True)

# Top panel: demand bars + surge rate line
color_demand = '#4f46e5'
ax1.bar(hourly.index, hourly['orders'], color=color_demand, alpha=0.7,
        label='Orders/hour (demand)')
ax1.set_ylabel('Orders per Hour', color=color_demand, fontsize=11,
               weight='semibold')
ax1.tick_params(axis='y', labelcolor=color_demand)
ax1.set_xticks(range(24))
ax1.set_xticklabels(range(24), fontsize=9)
ax1.grid(axis='y', alpha=0.2)

ax2 = ax1.twinx()
color_surge = '#dc2626'
ax2.plot(hourly.index, hourly['surge_rate'], color=color_surge, marker='o',
         linewidth=2.5, markersize=7, label='Surge rate (%)', zorder=10)
ax2.set_ylabel('Surge Rate (% of orders)', color=color_surge, fontsize=11,
               weight='semibold')
ax2.tick_params(axis='y', labelcolor=color_surge)
ax2.set_ylim(0, max(hourly['surge_rate']) * 1.15)

# Annotation 1: dinner ramp
ax1.annotate(
    'Hours 17-18 — dinner is ramping up\n(1,832 to 3,683 orders/hour)\nbut surge stays in "off" mode (~6%)',
    xy=(17.5, hourly.loc[17, 'orders']),
    xytext=(14, hourly['orders'].max() * 0.78),
    fontsize=9, color='#dc2626', weight='semibold',
    arrowprops=dict(arrowstyle='->', color='#dc2626', lw=1.5),
    ha='center'
)

# Annotation 2: lunch
ax1.annotate(
    'Lunch peak\n(~29% surge,\nonly 13% below dinner demand)',
    xy=(12.5, hourly.loc[12, 'orders']),
    xytext=(9, hourly['orders'].max() * 0.55),
    fontsize=9, color='#0e7490', weight='semibold',
    arrowprops=dict(arrowstyle='->', color='#0e7490', lw=1.2)
)

# Annotation 3: dinner peak
ax1.annotate(
    'Dinner peak\n(~53% surge)',
    xy=(19.5, hourly.loc[19, 'orders']),
    xytext=(22, hourly['orders'].max() * 0.85),
    fontsize=9, color='#1e40af', weight='semibold',
    arrowprops=dict(arrowstyle='->', color='#1e40af', lw=1.2)
)

ax1.set_title('Demand (bars) vs. Surge Rate (line) — Where the Spend Misaligns',
              fontsize=13, weight='semibold', pad=12)

# Bottom panel: zones of inefficiency
ax3.set_xlim(-0.5, 23.5)
ax3.set_ylim(0, 1)
ax3.set_xticks(range(24))
ax3.set_xticklabels(range(24), fontsize=9)
ax3.set_yticks([])
ax3.set_xlabel('Hour of Day', fontsize=11, weight='semibold')
ax3.spines['left'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.spines['top'].set_visible(False)
ax3.grid(False)

ax3.axvspan(16.5, 18.5, alpha=0.5, color='#dc2626',
            label='Finding 1: dinner-ramp under-coverage (17-18h)')
ax3.axvspan(11.5, 13.5, alpha=0.25, color='#0e7490',
            label='Finding 2: lunch under-incentivized')
ax3.axvspan(20.5, 21.5, alpha=0.4, color='#f59e0b',
            label='Finding 3: tail-surge waste (21h)')

ax3.legend(loc='upper center', ncol=3, bbox_to_anchor=(0.5, -0.4),
           fontsize=9, frameon=False)
ax3.set_title('Three Zones of Misaligned Spend', fontsize=10, pad=8,
              color='#525252')

plt.tight_layout()
plt.savefig('../docs/03_surge_mismatch.png', dpi=150, bbox_inches='tight')
plt.show()

# ============ Waste calculation ============
print("\n=== Quantified Waste ===\n")

SURGE_COST_PER_ORDER = 15
print(f"Assumption: Rs {SURGE_COST_PER_ORDER} incentive per surged order\n")

hour_21_orders = df[df['hour'] == 21]
tail_surge_count_h21 = hour_21_orders['surge_applied'].sum()
excess_tail_surge = int(tail_surge_count_h21 * 0.7)
excess_cost_per_month = (excess_tail_surge / 3) * SURGE_COST_PER_ORDER

print("Finding 3 (tail-surge waste at 21h):")
print(f"  Total surge orders at 21h over 90 days: {tail_surge_count_h21:,}")
print(f"  Estimated excess (70% of tail surge): {excess_tail_surge:,}")
print(f"  Estimated wasted spend per month: Rs {excess_cost_per_month:,.0f}\n")

lunch_surge = df[df['hour'].isin([12, 13])]['surge_applied'].mean() * 100
dinner_surge = df[df['hour'].isin([19, 20])]['surge_applied'].mean() * 100
lunch_demand = df[df['hour'].isin([12, 13])].shape[0]
dinner_demand = df[df['hour'].isin([19, 20])].shape[0]
demand_gap = (dinner_demand - lunch_demand) / dinner_demand * 100

print("Finding 2 (lunch under-incentivized):")
print(f"  Lunch surge: {lunch_surge:.1f}%, dinner surge: {dinner_surge:.1f}%")
print(f"  Demand gap: lunch is only {demand_gap:.1f}% below dinner")
print(f"  Surge differential is {dinner_surge/lunch_surge:.1f}x — disproportionate\n")

print("Finding 1 (dinner-ramp blind spot at 17-18h):")
print(f"  Redirecting {excess_tail_surge:,} surge orders from 21h to 17-18h")
print(f"  is cost-neutral. Expected delivery-time improvement: measure in pilot.\n")

print(f"=== Combined estimated savings: Rs {excess_cost_per_month:,.0f}/month ===")""")

cell_md2 = nbf.v4.new_markdown_cell("""**So what — THE HEADLINE:** Surge is binary (on at ~52% or off at 
~6%) but demand is continuous. Three specific mismatches result: 
(1) Hours 17-18 see a demand ramp from 1,832 → 3,683 orders/hour 
but surge stays "off" until 19h — riders are short-supplied when 
dinner orders flood in; (2) lunch surge averages 29% while dinner 
averages 52%, despite lunch demand being only 13% below dinner; 
(3) Hour 21 still carries 52.8% surge while demand has dropped 32% 
from peak. The fix isn't more surge spend — it's redistributing what 
we already pay. Estimated savings: Rs [X]/month (calculated above) 
plus a delivery-time improvement we'll measure in the pilot.""")

nb.cells.extend([cell_md1, cell_code, cell_md2])

with open(nb_path, 'w') as f:
    nbf.write(nb, f)

print("Notebook updated successfully.")
