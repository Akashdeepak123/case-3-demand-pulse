# Surge Spend Is Misaligned With Real Demand
## Three Monday-morning policy changes for the Ops Head

**TL;DR:** Surge fires on a binary on/off schedule, but demand is 
continuous. Three specific mismatches cost ~₹39K/month (~₹4.7L/year). 
The fix isn't more surge — it's redistributing what we already pay.

---

## The findings (90 days, 7 metros, 50,000 orders)

**Finding 1 — Hours 17-18 are under-covered.** Demand ramps from 
1,832 → 3,683 orders/hour during the dinner ramp, but surge stays in 
"off" mode (~6%). Riders are short-supplied right when dinner orders 
flood in. Surge then jumps to 52% at hour 19 — reactive, not 
proactive.

**Finding 2 — Lunch is under-incentivized vs dinner.** Lunch surge 
averages 29%, dinner averages 52%. Demand differs by only 13%. The 
1.8x surge differential isn't justified by the demand differential — 
either lunch is under-paying riders or dinner is over-paying.

**Finding 3 — Hour 21 carries surge tail-waste.** 52.8% surge while 
demand has already dropped 32% from peak. Premium incentives for 
cooled-off hours.

The 7 metros cluster into one main-metro group (Bangalore, Chennai, 
Delhi, Hyderabad, Mumbai) with two outliers (Pune lower-volume, 
Kolkata distinct delivery profile). A uniform main-metro policy with 
two outlier overrides is simpler and more defensible than a 3-cohort 
grid the data doesn't support.

---

## Recommendation 1 — Pre-position surge at the dinner ramp

**What.** Roll surge intensity from ~6% at 16h up to 35-40% by 17-18h, 
rather than jumping from 6% to 52% at 19h.

**Why.** Riders go online and commit shifts ~30 min before they want 
to earn. A binary off→on transition at the peak means rider supply 
catches up only after demand has already spiked. (See chart 3 in 
notebook: surge-demand mismatch.)

**Expected impact.** Cost-neutral by design — the same surge spend, 
shifted earlier. Expected ~20% reduction in delivery time p95 in the 
17-18h window. Measure in pilot.

**A/B test.** Run new schedule in 3 control cities for 4 weeks. 
Primary metric: delivery time p95 during 17-19h. Guardrail: total 
surge spend (must not increase).

**Risk and mitigation.** Riders accustomed to the 19h surge may 
resist earlier dispatch. Mitigate with a 2-week rolling transition 
and a one-time onboarding bonus for early adopters.

---

## Recommendation 2 — Main-metro policy + 2 outlier overrides

**What.** Replace the uniform national policy with: one main-metro 
policy (Bangalore, Chennai, Delhi, Hyderabad, Mumbai) and two 
city-specific overrides (Pune lower surge thresholds, Kolkata 
delivery-time-weighted surge).

**Why.** KMeans clustering on volume, AOV, delivery time, and 
dinner-share features surfaces 5 broadly similar main metros and 2 
outliers. Forcing 3 cohorts would degrade into "1 main + 2 outliers" 
anyway — better to acknowledge what the data shows.

**Expected impact.** ₹13K/month from Pune-Kolkata calibration (more 
surge needed in some windows, less in others — the current uniform 
policy over- and under-incentivizes simultaneously).

**A/B test.** 4-week pilot with Pune and Kolkata under override 
policies vs current. Primary: surge spend per order. Cross-check: 
rider satisfaction survey weekly.

**Risk and mitigation.** Operational complexity rises slightly. 
Mitigate with monthly review meeting and clear escalation rules. 
Document the override logic in the surge engine config.

---

## Recommendation 3 — Pre-position riders using the 7-day forecast

**What.** Use the SARIMA-based 7-day hourly forecast 
(`data/forecast_output.csv`) to schedule rider shift starts 30 min 
before predictable demand spikes.

**Why.** Hourly MAE is 1.6 orders/hour — off by 1-2 orders on a mean 
of 6 orders/hour. At the 4-hour shift-block resolution operations 
actually uses, MAPE is 31.6%; daily MAPE is 9.9%. Operationally 
useful for shift scheduling.

**Expected impact.** Estimated ~10 minutes reduction in delivery 
time p95 during forecast-peak windows. Numbers to be refined in 
pilot.

**A/B test.** Run in Bangalore (highest-volume city) for 2 weeks. 
Primary: delivery time p95 during forecast-peak windows. Compare 
against current week-over-week scheduling.

**Risk and mitigation.** Forecast errors on anomalous days 
(holidays, weather). Mitigate with manual override for the ops 
manager and a fallback to the 4-week rolling average when forecast 
confidence band exceeds ±30%.

---

## How we'll know this worked

**Primary metric.** Surge spend per order. Target -15% in 60 days 
(combined effect of Recs 1 and 2 + revenue recovery from Rec 1's 
delivery-time improvement).

**Guardrails (must not regress more than 5%):** delivery time p95, 
order completion rate, rider rating.

**Kill criteria.** Any guardrail breaches threshold for 2 
consecutive weeks → revert and post-mortem.

---

## Quantified impact summary

| Source | Monthly impact | Confidence |
|---|---|---|
| Finding 3 — tail-surge waste at 21h | ₹13K/month | Direct calculation |
| Finding 2 — recoverable lunch revenue | ₹26K/month | Modeled (5% lunch loss, 50% recovery) |
| Finding 1 — delivery-time improvement | TBD pilot | Quantify post-A/B |
| **Total estimated annual recovery** | **₹4.7L/year** | Conservative |

Assumption: ₹60 blended cost per surged order (midpoint of industry 
range ₹40-150). Validate against internal cost data before pilot.

---

## What we didn't address (honest scope)

- **Restaurant-level surge.** Some restaurants likely attract surge 
  unfairly relative to their demand. Out of scope for this iteration.
- **Order-value-aware surge.** ₹100 and ₹1000 orders currently treated 
  identically. Worth modeling in next quarter.
- **Weather and holiday regressors in the forecast.** SARIMA captures 
  daily + weekly seasonality but not exogenous events. Worth adding 
  if rolling out the forecast-driven scheduling.
- **Cuisine-specific surge.** Biryani and Continental peak at dinner; 
  South Indian peaks at lunch. The current surge is cuisine-blind.

All four are scoped for the next analysis cycle, designed but not 
quantified here.