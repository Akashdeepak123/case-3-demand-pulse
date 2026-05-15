import pandas as pd
import numpy as np

df = pd.read_csv("data/case3_food_delivery_orders.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['hour'] = df['timestamp'].dt.hour
df['day_of_week'] = df['timestamp'].dt.day_name()
df['date'] = df['timestamp'].dt.date

hourly_demand = df.groupby('hour').size()
top_3_hours = hourly_demand.sort_values(ascending=False).head(3)
peak_hour = top_3_hours.index[0]
peak_orders = top_3_hours.iloc[0]
trough_hour = hourly_demand.idxmin()
trough_orders = hourly_demand.min()
hour_18_orders = hourly_demand[18]
hour_18_rank = (hourly_demand.sort_values(ascending=False).index == 18).argmax() + 1

print(f"Peak hour: {peak_hour}:00 ({peak_orders:,} orders/day on average)")
print(f"Top 3 hours by demand: {list(top_3_hours.index)}")
print(f"Hour 18 — the dinner ramp: {hour_18_orders:,} orders (rank #{hour_18_rank} of 24)")
print(f"Trough: {trough_hour}:00 ({trough_orders:,} orders)")
print(f"Peak-to-trough ratio: {peak_orders/trough_orders:.1f}x")
