# Surge Spend Is Misaligned with Real Demand
## Three Monday-morning policy changes for the Ops Head

**The finding** *(quantified below)*

Surge tracks demand well overall (correlation 0.81), but the policy 
has three specific flaws:

1. **Reactive timing** — Hour 18 has the third-highest demand of the 
   day (3,683 orders) but only 5.7% surge. Surge spikes to 52% only 
   AFTER dinner has started at 19h. Riders are short-supplied right 
   when dinner orders flood in.

2. **Lunch-dinner imbalance** — Lunch surge averages ~29%, dinner 
   surge averages ~53%. But lunch demand is only ~16% below dinner. 
   The 2x surge differential isn't justified by a 16% demand 
   differential.

3. **Tail surge waste** — Hour 21 still carries 52.8% surge while 
   demand has already dropped 32% from the dinner peak. We're paying 
   premium incentives for cooled-off hours.

Each finding maps to one recommendation below. Estimated combined 
impact: ₹[X]/month with no demand-coverage loss.

---

## Recommendation 1 — Shift surge windows to real peak hours

**What.** Move primary surge from [CURRENT_HOURS] to [REAL_PEAK_HOURS].

**Why.** [Reference notebook chart 3]

**Expected impact.** ₹[X]/month saved with no service degradation 
(rider availability maintained because total surged hours stay 
constant; only the timing shifts).

**A/B test design.** Run the new schedule in 3 control cities for 
4 weeks. Primary metric: surge spend per order. Guardrail: delivery 
time p95.

**Risk and mitigation.** Riders accustomed to old surge hours may 
not be available at new peaks. Mitigate with a 2-week rolling 
transition rather than a hard cut, and a one-time onboarding bonus.

---

## Recommendation 2 — Per-cohort incentive grid

**What.** Replace the single national surge policy with 
[N]-cohort-specific policies for [COHORT_NAMES].

**Why.** [Reference notebook chart 5 — cohort analysis]

**Expected impact.** ₹[X]/month from cohort-aware pricing 
(estimated as a fraction of the savings already counted in Rec 1, 
to avoid double-counting).

**A/B test design.** 4-week pilot with one city per cohort. 
Primary: surge spend per order. Cross-check: rider satisfaction 
survey weekly.

**Risk and mitigation.** Operational complexity goes up. Mitigate 
with a monthly review meeting and clear escalation rules.

---

## Recommendation 3 — Pre-position riders using 7-day forecast

**What.** Use a Prophet-based hourly demand forecast to schedule 
rider shift starts 30 min before predictable spikes.

**Why.** [Reference notebook 02_forecast — backtest MAPE]

**Expected impact.** ~[X] minutes reduction in delivery time p95 
during peak hours.

**A/B test design.** Run in the highest-volume city for 2 weeks. 
Primary: delivery time p95 during forecasted-peak windows.

**Risk and mitigation.** Forecast errors on anomalous days 
(holidays, weather). Mitigate with a manual override capability 
for the ops manager and a fallback to the 4-week rolling average 
when forecast confidence is low.

---

## How we'll know this worked

**Primary metric:** surge spend per order — target -15% in 60 days.

**Guardrails (must not regress more than 5%):** delivery time p95, 
order completion rate, rider rating.

**Kill criteria:** any guardrail breaches threshold for 2 
consecutive weeks → revert and post-mortem.

---

## What we didn't address (honest scope)

- Restaurant-level surge (some restaurants attract surge unfairly).
- Order-value-aware surge (₹100 vs ₹1000 orders treated the same).
- Weather and holiday calendars as forecast regressors.

All three are next-quarter work, designed but not analyzed here.
