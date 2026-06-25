# Workflow: Analyze Props (Master SOP)

## Objective
Take raw PrizePicks tennis props typed into chat by the user, research each
one, estimate true probability, compare against PrizePicks' implied
probability, and recommend flat-stake 2-pick and 3-pick parlays -- printed to
the terminal.

## Trigger
The user wants to analyze one or more tennis props. The single entry point
is:
```
python agent.py
```
Run this via the terminal whenever the user provides props -- it drives the
rest of the session interactively.

## Required Inputs
- Raw prop text (player, stat type, line, and optionally over/under) -- one
  prop per line, typed when `agent.py` prompts for it. Direction is
  optional: PrizePicks doesn't fix a side, so a line like
  "Carlos Alcaraz Aces 8.5" (no Over/Under) tells the pipeline to evaluate
  both sides and recommend whichever clears the edge.
- Implied probability baseline: 0.54 (PrizePicks standard), fixed unless the
  user says otherwise.
- Bankroll: $20 flat. 2-pick parlays pay 3x, 3-pick parlays pay 5x.

## Procedure

1. **Run `python agent.py`.** It prints a welcome banner and prompts for
   props. Type or paste props, one per line, then press Enter on a blank
   line to submit.

2. **Parsing happens automatically.** Each line becomes a structured prop
   (`player_name`, `stat_type`, `direction`, `line_value`). If a line can't
   be parsed, `agent.py` shows it back and asks for that one prop to be
   re-entered (or skipped) -- never guesses what was meant.

3. **For each prop, `agent.py` pauses and prints the WebSearch queries
   needed** (recent form, the specific stat on this surface, head-to-head,
   injury/news -- per [research_player.md](research_player.md)). At this
   point:
   - Run those WebSearches using your own WebSearch tool.
   - Synthesize the findings into the JSON shape described in
     research_player.md.
   - Paste that JSON back in when `agent.py` prompts for it (or type
     `INCONCLUSIVE` if the research genuinely didn't turn up usable data).

   Repeat for every prop before the script moves on.

4. **Estimation runs automatically** once all props are researched
   (`tools/estimate_probability.py`): a weighted score of stat-hit-rate
   (40%), surface tendency (25%), opponent factor (20%), and
   injury/fatigue/momentum (15%), shrunk toward neutral when confidence is
   medium/low. Inconclusive research is never turned into a guessed number.

5. **Edge evaluation runs automatically** (`tools/evaluate_edge.py`):
   `edge = true_probability - 0.54`, rated `STRONG` (edge >10%), `MODERATE`
   (5-10%), `WEAK` (0-5%), or `FADE` (true probability below 54%). If the
   prop didn't specify a direction, `agent.py` evaluates both Over and
   Under and keeps whichever side has the better rating -- the other side's
   number is still shown in the report for transparency.

6. **Parlay construction runs automatically** (`tools/build_parlays.py`):
   only `STRONG`/`MODERATE` props are eligible, correlated legs (same player
   or same match) are excluded, and only the top 2 two-pick combos and top 1
   three-pick combo (by expected value) are kept, staked at a fixed $5 / $4
   / $3 -- capped at $12 total per session.

7. **The final report prints automatically**
   (`tools/print_report.py`), per [build_report.md](build_report.md).

8. **Before any of this**, `agent.py` checks for past props awaiting a real
   outcome and prompts to resolve them, then logs this session's new
   predictions for future calibration, and prints a calibration check if
   there's resolved history -- see [track_results.md](track_results.md).

## Edge Cases

- **Parse failure**: `agent.py` asks the user to re-enter that specific
  prop -- never guesses player/stat/line.
- **Inconclusive research**: typing `INCONCLUSIVE` at the findings prompt
  flags the prop clearly in the report and excludes it from parlay
  construction -- never fabricate a probability to fill the gap.
- **Large batches**: no hard cap on prop count -- process all of them, just
  expect more research pauses for larger batches (8+ props).
- **Fewer than 2 STRONG/MODERATE props**: the report states plainly that no
  parlay is possible and why.
- **No combo clears positive expected value**: say so explicitly under that
  payout tier rather than forcing a recommendation.

## Ground Rules (carried over from CLAUDE.md / project setup)
- Always use live WebSearch for research -- never rely on memorized stats,
  and never call an external search API.
- 0.54 is the fixed implied-probability baseline unless the user overrides
  it.
- Flag low-confidence / inconclusive props explicitly rather than guessing.
- This is informational/analytical only -- never present output as
  guaranteed outcomes or financial advice.
