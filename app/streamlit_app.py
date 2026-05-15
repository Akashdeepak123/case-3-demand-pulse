"""
Demand Pulse — Interactive Ops Console.

Single-page Streamlit dashboard for the Ops Head. Three sections:
1. Surge-demand mismatch overview
2. Interactive what-if surge calculator (move the slider, see new savings)
3. 7-day forecast for Bangalore
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Demand Pulse — Ops Console",
    page_icon="⚡",
    layout="wide",
)

# Constants
SURGE_COST_PER_ORDER = 60  # Rs

# Load data
@st.cache_data
def load_data():
    data_path = Path(__file__).parent.parent / "data" / "case3_food_delivery_orders.csv"
    df = pd.read_csv(data_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.day_name()
    return df


@st.cache_data
def load_forecast():
    fc_path = Path(__file__).parent.parent / "data" / "forecast_output.csv"
    if fc_path.exists():
        return pd.read_csv(fc_path, parse_dates=['datetime_hour'])
    return None


df = load_data()
forecast_df = load_forecast()

# ============ HEADER ============
st.markdown("# ⚡ Demand Pulse")
st.markdown("**Interactive ops console for surge policy decisions.** "
            "Drag the sliders below to model surge-window shifts and see "
            "live recalculated savings.")

st.divider()

# ============ TOP-LEVEL METRICS ============
col_a, col_b, col_c, col_d = st.columns(4)
total_orders = len(df)
total_surged = df['surge_applied'].sum()
overall_surge_rate = total_surged / total_orders * 100
days = df['timestamp'].dt.date.nunique()

with col_a:
    st.metric("Total orders (90d)", f"{total_orders:,}")
with col_b:
    st.metric("Surged orders", f"{total_surged:,}")
with col_c:
    st.metric("Overall surge rate", f"{overall_surge_rate:.1f}%")
with col_d:
    monthly_surge_spend = (total_surged / 3) * SURGE_COST_PER_ORDER
    st.metric("Current surge spend", f"₹{monthly_surge_spend:,.0f}/mo")

st.divider()

# ============ SECTION 1: THE MISMATCH ============
st.markdown("## The mismatch: when surge is paid vs. when demand peaks")

hourly = df.groupby('hour').agg(
    orders=('order_id', 'count'),
    surge_count=('surge_applied', 'sum')
)
hourly['surge_rate'] = hourly['surge_count'] / hourly['orders'] * 100

# Dual-axis chart
fig, ax1 = plt.subplots(figsize=(12, 4))
ax1.bar(hourly.index, hourly['orders'], color='#4f46e5', alpha=0.7, label='Orders/hour')
ax1.set_xlabel('Hour of Day')
ax1.set_ylabel('Orders/hour', color='#4f46e5')
ax1.tick_params(axis='y', labelcolor='#4f46e5')
ax1.set_xticks(range(24))
ax1.grid(axis='y', alpha=0.2)

ax2 = ax1.twinx()
ax2.plot(hourly.index, hourly['surge_rate'], color='#dc2626',
         marker='o', linewidth=2.5, markersize=6, label='Surge rate %')
ax2.set_ylabel('Surge rate (%)', color='#dc2626')
ax2.tick_params(axis='y', labelcolor='#dc2626')
ax2.set_ylim(0, hourly['surge_rate'].max() * 1.15)

ax1.set_title('Demand (bars) vs. Surge (line)', fontsize=12, weight='semibold')
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

st.caption("Surge is binary (~6% off, ~52% on) but demand is continuous. "
           "Hours 17-18 ramp up demand while surge stays off. Hour 21 keeps "
           "surge on while demand has dropped 32% from peak.")

st.divider()

# ============ SECTION 2: WHAT-IF CALCULATOR ============
st.markdown("## What-if calculator — test surge policy changes live")
st.markdown("Adjust the surge windows below. Savings recalculate instantly.")

calc_col_a, calc_col_b = st.columns(2)

with calc_col_a:
    st.markdown("**Dinner surge START (currently 19h)**")
    new_dinner_start = st.slider(
        "Shift dinner surge earlier to:",
        min_value=16, max_value=19, value=18, step=1,
        help="Earlier start → riders pre-positioned for the ramp at 17-18h",
        label_visibility="collapsed",
    )
    st.caption(f"New dinner surge start: **{new_dinner_start}h** "
               f"(was 19h → shifted {19 - new_dinner_start}h earlier)")

with calc_col_b:
    st.markdown("**Dinner surge END (currently 21h)**")
    new_dinner_end = st.slider(
        "Cut dinner surge tail at:",
        min_value=19, max_value=22, value=20, step=1,
        help="Earlier end → reclaim surge spent on hour 21 cool-down",
        label_visibility="collapsed",
    )
    st.caption(f"New dinner surge end: **{new_dinner_end}h** "
               f"(was 21h → cut {21 - new_dinner_end}h earlier)")

st.markdown(" ")

# Compute the savings live
# Hours currently surged at high rates: 12,13 (lunch ~29%) and 19,20,21 (dinner ~53%)
# After shift: dinner surge hours = [new_dinner_start, ..., new_dinner_end]
current_dinner_hours = [19, 20, 21]
new_dinner_hours = list(range(new_dinner_start, new_dinner_end + 1))

# Reclaimed orders = surge orders at hours dropped from dinner window
dropped_hours = [h for h in current_dinner_hours if h not in new_dinner_hours]
added_hours = [h for h in new_dinner_hours if h not in current_dinner_hours]

# Tail surge reclaimed (hours we're cutting from dinner that were over-surged)
reclaimed_orders = 0
for h in dropped_hours:
    # Estimate: 32% of current surge at that hour is "excess" 
    # (relative to peak hours' demand)
    excess_rate = 0.32 if h == 21 else 0.10
    reclaimed_orders += int(df[df['hour'] == h]['surge_applied'].sum() * excess_rate)

# Net cost of adding new hours (assume we'd surge ~40% of orders there)
new_hour_cost = 0
for h in added_hours:
    if h not in current_dinner_hours:  # New hour added
        hour_orders = df[df['hour'] == h].shape[0]
        # Estimate adding ~30% surge on these hours (less than peak's 52%)
        added_surge_orders = int(hour_orders * 0.30)
        new_hour_cost += added_surge_orders

# Net savings per month
net_reclaimed = reclaimed_orders - new_hour_cost
monthly_savings = (net_reclaimed / 3) * SURGE_COST_PER_ORDER

# Display results
res_col_a, res_col_b, res_col_c = st.columns(3)
with res_col_a:
    st.metric("Reclaimed surge orders",
              f"{reclaimed_orders:,}",
              f"-{reclaimed_orders} surge events")
with res_col_b:
    st.metric("New hours surged",
              f"{new_hour_cost:,}",
              f"+{new_hour_cost} surge events" if new_hour_cost > 0 else "0")
with res_col_c:
    delta_color = "normal" if monthly_savings > 0 else "inverse"
    st.metric("Net monthly impact",
              f"₹{monthly_savings:,.0f}",
              f"₹{monthly_savings * 12:,.0f}/year",
              delta_color=delta_color)

# Interpretation
if monthly_savings > 30000:
    st.success(f"🎯 Strong saving — {((monthly_savings/monthly_surge_spend)*100):.1f}% reduction in monthly surge spend. "
               "Worth piloting in 3 control cities.")
elif monthly_savings > 5000:
    st.info(f"📊 Modest saving of ₹{monthly_savings:,.0f}/month. "
            "Worth piloting if combined with rider supply tightening at new dinner-ramp hours.")
else:
    st.warning("⚠️ Configuration produces minimal savings or net cost. "
               "Try shifting dinner start earlier (16-17h) while keeping end at 20h to maximize the pre-position effect.")

st.caption("Assumption: ₹60 blended cost per surged order. "
           "32% of hour-21 surge is excess relative to demand. "
           "New surge hours assumed at 30% rate. "
           "Adjust assumptions in code (`SURGE_COST_PER_ORDER`) for your internal data.")

st.divider()

# ============ SECTION 3: FORECAST ============
st.markdown("## 7-day forecast — Bangalore (highest volume city)")

if forecast_df is not None:
    # Fetch last 7 days of actuals + forecast
    bng = df[df['city'] == 'Bangalore'].copy()
    bng['datetime_hour'] = bng['timestamp'].dt.floor('H')
    hourly_bng = bng.groupby('datetime_hour').size().reset_index(name='orders')

    # Plot last 7 days history + forecast
    fig, ax = plt.subplots(figsize=(12, 4))
    recent_history = hourly_bng.tail(168)  # last 7 days
    ax.plot(recent_history['datetime_hour'], recent_history['orders'],
            color='#4f46e5', linewidth=1.5, label='Last 7 days (actual)', alpha=0.85)
    ax.plot(forecast_df['datetime_hour'], forecast_df['forecast_orders'],
            color='#dc2626', linewidth=2, linestyle='--', label='Next 7 days (forecast)')
    ax.fill_between(forecast_df['datetime_hour'],
                    forecast_df['forecast_orders_lower'],
                    forecast_df['forecast_orders_upper'],
                    alpha=0.2, color='#dc2626')
    ax.set_xlabel('Date-Hour')
    ax.set_ylabel('Orders/hour')
    ax.legend(loc='upper right')
    ax.grid(alpha=0.3)
    plt.xticks(rotation=30)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # Metrics
    fc_col_a, fc_col_b, fc_col_c = st.columns(3)
    with fc_col_a:
        st.metric("Total forecasted orders (7d)",
                  f"{forecast_df['forecast_orders'].sum():,}")
    with fc_col_b:
        st.metric("Daily MAPE (backtest)", "9.9%")
    with fc_col_c:
        st.metric("Hourly MAE (backtest)", "1.6 orders")
    
    st.caption("MAPE varies by aggregation: 9.9% at daily level, 31.6% at 4-hour shift "
               "blocks (the resolution operations actually uses), 44.7% at hourly. "
               "The hourly number is a small-denominator artifact — see notebook 02 for analysis.")
else:
    st.info("Forecast CSV not found. Run `notebooks/02_forecast.ipynb` to generate it.")

st.divider()

# ============ FOOTER ============
st.markdown(
    "_**Demand Pulse v0.1** · "
    "Built from 90 days of order data across 7 metros (50,000 orders). "
    "Full analysis in `EXEC_SUMMARY.md`. "
    "Notebook source in `notebooks/`._"
)
