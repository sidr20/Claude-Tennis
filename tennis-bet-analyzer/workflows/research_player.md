# Workflow: Research Player

## Objective
Gather enough current, real data on a player/prop to feed
`tools/estimate_probability.py` a defensible weighted estimate -- not a guess
-- and to populate every narrative field the final report needs.

## Why this is the agent's job, not a tool's
`tools/research_player.py` never calls a search API -- that's a deliberate
project rule, not a missing feature. Web research is reasoning-heavy: judging
which matches are representative, how an opponent or surface should shift
expectations, when data is too thin to trust. So the agent (you) runs
multiple targeted WebSearches directly, synthesizes across them, and hands
clean structured findings to the deterministic tools.

## What to Search For

Run at minimum three targeted searches per prop -- more if the picture is
unclear:

1. **Recent form** -- `<player> last 5 matches results, surface, current
   tournament round`. Anchors `recent_match_values`, `surface`, `tournament`,
   `recent_form_summary`.
2. **The specific stat, on this surface** -- phrase the query around the
   exact prop:
   - **Aces** -> average aces per match on this surface, recent ace counts.
   - **Games Won** -> average games won per match recently.
   - **Double Faults** -> double-fault tendencies on this surface.
   - **First Serve %** -> recent first-serve percentage trends.
   Feeds `recent_match_values` (the actual per-match stat values) and
   `stat_trend_summary`.
3. **Injury/news** -- `<player> injury news, withdrawal, retirement,
   fatigue`. Feeds `injury_news`.
4. **Head-to-head and opponent effect** (if today's opponent is known) --
   `<player> vs <opponent> head to head`, plus how that opponent's
   return/pressure game affects this specific stat. Feeds `opponent`,
   `opponent_factor_summary`, `opponent_probability`.

## Direction-Agnostic Research

Research is the same regardless of whether the prop specifies Over/Under --
do one research pass per player/stat, not one per side. `surface_probability`,
`opponent_probability`, and `momentum_probability` should always be framed as
"probability of clearing the line" (i.e. the Over side); `estimate_probability.py`
derives Under as `1 - Over` automatically. If the prop didn't specify a
direction, `agent.py` will compute both and recommend whichever clears the
edge -- you only need to research and submit findings once per prop either way.

## Turning Findings Into Structured Data

Document what you found AND what you couldn't find, then synthesize into
this JSON shape for `save-research` (the running `agent.py` session will
prompt you for exactly this):

- `recent_match_values` (list[float], **required**): the actual stat value
  from each of the player's last 5 (or as many as found) matches -- e.g.
  `[9, 11, 7, 10, 8]` for aces. `estimate_probability.py` computes the
  stat-hit-rate component directly from this against the prop's line, so
  give real per-match numbers, not an average.
- `surface` (string): e.g. `"Hard"`.
- `tournament` (string): e.g. `"Wimbledon, QF"`.
- `recent_form_summary` (string): e.g. `"Won 4 of last 5, current SF."`
- `stat_trend_summary` (string): what the data shows about this specific
  stat on this surface.
- `opponent` (string or null): today's opponent's name, if known. Used to
  detect correlated parlay legs (two props from the same match).
- `opponent_factor_summary` (string): how today's opponent affects this
  stat, e.g. `"Opponent is a top-10 returner -- expect fewer aces than usual."`
- `surface_probability` (float 0-1, default 0.5): your estimate of hit
  probability from surface tendency alone.
- `opponent_probability` (float 0-1, default 0.5): your estimate of hit
  probability from the opponent matchup alone.
- `momentum_probability` (float 0-1, default 0.5): your estimate of hit
  probability from injury/fatigue/momentum alone.
- `injury_news` (string, default `"None found"`).
- `confidence` (string, **required**): `"high"`, `"medium"`, or `"low"`.
  This directly controls how much the weighted estimate gets shrunk toward a
  neutral 50% -- be honest about thin or conflicting samples.
- `notes` (string): 2-3 sentences synthesizing the above into the reasoning
  that will justify the final verdict in the report.
- `inconclusive` (bool, default `false`): set `true` if the data is too
  sparse, stale, or contradictory to support a number. When `true`, every
  other field is optional -- just explain why in `notes`.

## Edge Cases
- **No recent matches found** (injury layoff, off-season, qualifier with no
  tracked history): set `inconclusive: true`, explain why in `notes`.
- **Conflicting sources**: prefer the most recent, most official source
  (ATP/WTA stats pages, tournament sites) over aggregator blogs; note the
  conflict if it materially changes the picture.
- **Opponent unknown at prop time**: leave `opponent` null and
  `opponent_probability` at the default `0.5`, and say so in `notes` rather
  than guessing a matchup edge.
- **Thin sample** (fewer than 3 recent matches): still compute
  `recent_match_values` from what's available, but set `confidence: "low"`
  so the model shrinks toward neutral.

## Lessons Learned
- **Per-match ace counts are often unavailable for several of a player's last
  5 matches** -- many stats sites report only tournament-week aggregates or
  single confirmed box scores, not a clean per-match breakdown. It's fine to
  submit `recent_match_values` with `null` gaps for matches you couldn't
  verify (e.g. `[9, null, null, null]`) rather than guessing -- the estimator
  filters out the nulls and computes the hit rate from whatever real values
  remain. Only set `inconclusive: true` if there are zero real values, or the
  match itself can't be confirmed as real/scheduled.
- **Verify the match is actually happening** before researching the stat
  itself -- player news (withdrawals, walkovers, draws not yet started) can
  mean a listed matchup isn't real. If you find evidence of this, mark
  `inconclusive: true` and explain in `notes` rather than researching a stat
  for a match that may not occur.
