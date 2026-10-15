---
name: Seed: feed
description: >-
  Use when Seed finds ideas relevant to an agent or project the user already has (for
  example a trading bot, job-search bot or store tool). Routes the best new findings to
  the owner instead of starting something duplicate.
---
# Feed

1. List the user's existing agents/projects if the host can. Match each distilled idea
   to at most one owner by topic.
2. For each match, send a short handoff: the idea, why it fits, sources, confidence
   label, and the flags. Ask the owner to test it safely (paper/dry-run) first.
3. Seed never acts on an idea itself: no trades, purchases, sign-ups, posts or messages
   to people outside the user's own agents without explicit user approval.
4. Record what was routed with `seed_note` (kind `fed`, include the owner name) so the
   same idea isn't sent twice.
