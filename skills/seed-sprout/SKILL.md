---
name: Seed: sprout
description: >-
  Use when a Seed topic has enough knowledge to become its own agent, or the user asks
  "make a bot from this", "what would a bot for this look like". Produces a bot blueprint
  plus informed multiple-choice pre-build questions drawn from what Seed learned.
---
# Sprout

1. Call `seed_blueprint` with the topic. It drafts a name, mission, workflow steps from
   the top clusters, safety guardrails, and pre-build questions with options.
2. Improve the draft with your distilled notes: every question should offer 2–4 concrete
   options taken from the sources ("Strategy A from @x vs strategy B from @y"), a
   recommended default, and why.
3. Always include questions for: risk/spend limits, free vs paid tools, paper/dry-run vs
   live, how often to report, and what the bot must never do.
4. Present the questions so the user can answer by tapping options. Do not create the
   bot or connect accounts until the user answers. Time-sensitive topics may skip
   questions only when the user said so.
