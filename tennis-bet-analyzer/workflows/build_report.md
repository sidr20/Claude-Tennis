# Workflow: Build Report

## Objective
Print the final terminal report in the exact format below. This is handled
by `tools/print_report.py`, called automatically at the end of `python
agent.py`.

## Exact Format

```
TENNIS PROP ANALYSIS — [DATE]

Bankroll: $20

PLAYER NAME — STAT — OVER/UNDER LINE
Surface: [surface]
Tournament: [tournament name + round]
Recent Form: [brief summary — e.g., "Won 4 of last 5, current SF"]
Stat Trend: [what the data shows about this specific stat]
Opponent Factor: [how today's opponent affects this stat]
Injury/News: [any flags or "None found"]
Estimated True Probability: [X%]
PrizePicks Implied Probability: 54%
Edge: [+/- X%]
Verdict: [STRONG ✅ / MODERATE 🟡 / WEAK ⚠️ / FADE ❌]
Reasoning: [2-3 sentence explanation of the verdict]
Other Side: [shown only if the prop had no fixed direction -- the
  probability/edge/rating for the side that wasn't recommended, for
  transparency]
============================================================
[... one block per prop ...]

PARLAY RECOMMENDATIONS
2-PICK PARLAYS (3x payout):
→ [Player A prop] + [Player B prop]
   Combined confidence: [HIGH/MEDIUM]
   Recommended stake: $5
   Potential payout: $15
→ [next best 2-pick combo if available]
   Recommended stake: $4
   Potential payout: $12
3-PICK PARLAYS (5x payout):
→ [Player A] + [Player B] + [Player C]
   Combined confidence: [HIGH/MEDIUM]
   Recommended stake: $3
   Potential payout: $15
============================================================
SUMMARY
Strong plays: [count]
Moderate plays: [count]
Fade/Avoid: [count]
Total recommended spend: $[X] of $20 bankroll
```

## Rules Behind the Format

- **Date**: today's date, top of report.
- **Per-prop block**: every prop is shown, including ones flagged
  insufficient-data or unparseable -- never silently dropped.
  - If insufficient data: show `Estimated True Probability: INSUFFICIENT
    DATA`, `Edge: N/A`, `Verdict: FLAGGED ⚠️`, and explain why in
    `Reasoning`.
- **Verdict bands** (from `tools/evaluate_edge.py`): `STRONG ✅` (edge >10%),
  `MODERATE 🟡` (edge 5-10%), `WEAK ⚠️` (edge 0-5%), `FADE ❌` (true
  probability below 54%).
- **Undirected props** (no Over/Under specified): both sides are evaluated;
  the header, probability, edge, and verdict reflect whichever side won, and
  an `Other Side` line shows the loser's numbers so nothing is hidden.
- **Parlays**: built only from `STRONG`/`MODERATE` legs, correlated legs
  (same player or same match) excluded. At most the top 2 two-pick combos
  and top 1 three-pick combo are shown, each by descending expected value.
  - **Fixed flat stakes**: best 2-pick $5, second 2-pick $4, best 3-pick $3
    -- total session spend never exceeds $12 (60% of the $20 bankroll).
  - If fewer than 2 STRONG/MODERATE props exist, state plainly that no
    parlay is possible and why, instead of printing empty parlay sections.
  - If no combo clears positive expected value, say so explicitly under that
    payout tier rather than forcing a recommendation.
- **Summary counts**: `Strong plays` / `Moderate plays` count STRONG /
  MODERATE verdicts; `Fade/Avoid` lumps together WEAK, FADE, and
  insufficient-data/flagged props -- anything not strong enough to act on.
- **Total recommended spend**: sum of the stakes actually assigned (so it's
  less than $12 whenever fewer than all three parlay slots are filled).

## Formatting Rules
- Plain terminal text, no external formatting libraries -- keep
  `tools/print_report.py` dependency-free.
- Percentages to 1 decimal place for true probability and edge; whole
  percent for the 54% implied baseline; stakes and payouts rounded to whole
  dollars.
- Never state a prop "will" hit -- use "estimated probability" / "edge"
  language throughout.

## Edge Cases
- **Zero qualifying props**: still print every per-prop block (all WEAK,
  FADE, or flagged) and clearly state no parlay is recommended.
- **Mixed batch**: flagged/unparseable props are excluded from parlay
  construction but still shown individually so the user knows why they were
  left out.
