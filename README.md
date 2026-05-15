---
title: Demand Pulse
emoji: ⚡
colorFrom: indigo
colorTo: red
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# Demand Pulse — Food Delivery Surge Analysis

> One-line: Three Monday-morning policy changes for the Ops Head, 
> backed by 90 days of order data, cohort analysis, and a 7-day 
> demand forecast.

## Run locally

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

## Deliverables

- [EXEC_SUMMARY.md](./EXEC_SUMMARY.md) — 1-page brief for the Ops Head
- [notebooks/](./notebooks/) — analysis, narrated top-to-bottom
- [data/forecast_output.csv](./data/forecast_output.csv) — 7-day hourly forecast
- [docs/](./docs/) — chart exports

## Status

Work in progress.
