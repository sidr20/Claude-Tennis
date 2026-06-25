# Workflow: Track Results

## Objective
Find out whether `estimate_probability.py`'s model is actually calibrated --
i.e. do `STRONG`-rated props really hit around 70%+ of the time, or is the
model overconfident -- by checking real outcomes against predictions over
many props, instead of reacting to any single slate (two misses on ~70%
picks is unremarkable; the same two misses across fifty picks is a real
signal).

## How It Fits Into `agent.py`

This runs automatically as part of `python agent.py` -- there's no separate
command:

1. **At startup**, before asking for new props, `agent.py` checks
   `results_log.json` for `pending` entries (props from a past session whose
   real-world outcome isn't logged yet). For each one, it shows the prop and
   what was predicted, and asks for the actual stat value.
   - Type a number (e.g. `7` aces) to resolve it -- the script computes
     hit/miss against the line and direction automatically.
   - Type `SKIP` if the match hasn't finished yet -- it stays pending.
   - Type `VOID` if the match never happened (retirement, walkover,
     postponement) -- it's excluded from calibration entirely rather than
     counted as a loss.
2. **After a new slate is analyzed**, every prop that got a real probability
   (not flagged/unparseable) is appended to `results_log.json` as a new
   `pending` entry, tagged with today's date, the prediction, and the rating.
3. **At the end of every run**, if there's any resolved history at all, a
   `CALIBRATION CHECK` block prints: per rating tier (`STRONG`/`MODERATE`/
   `WEAK`/`FADE`), how many have resolved, the actual hit rate, and the
   average predicted probability for that tier, plus an overall hit rate.

## Why `results_log.json` Lives Outside `.tmp/`
Per CLAUDE.md, `.tmp/` is disposable and gets regenerated. This log is the
opposite -- it's the one piece of local state in this project meant to
persist and accumulate across sessions, because the entire point is to
compare predictions against outcomes over a real sample size. Don't delete
it as part of routine cleanup.

## Edge Cases
- **Match not finished when you next run the script**: type `SKIP` -- it
  stays pending indefinitely until resolved.
- **Match didn't happen** (retirement before the relevant stat was
  meaningful, walkover, postponed): type `VOID` rather than guessing a
  number or leaving it pending forever.
- **Not enough resolved history yet**: `print_calibration_check()` simply
  doesn't print anything until at least one prop has been resolved -- no
  need to force a summary on tiny samples.
- **Same prop logged twice in one day** (e.g. re-running analysis on the
  same slate): `log_new_evaluations` dedupes by `log_id`
  (`date-player-stat-line`), so it won't double-log.

## Reading the Numbers
A well-calibrated `STRONG` tier (edge >10%, i.e. true probability >64%)
should land somewhere north of 64% actual hit rate over enough props -- if
it's tracking noticeably lower than the average predicted probability for
that tier over a real sample (call it 20+ resolved props per tier before
drawing conclusions), that's the signal to revisit the weights in
`estimate_probability.py`, not any single slate's results.
