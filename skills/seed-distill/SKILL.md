---
name: Seed: distill
description: >-
  Use after Seed has grown a topic, or when the user asks to summarize, merge, dedupe or
  fact-check what Seed found. Clusters ideas, merges duplicates with citations, and flags
  unverified, promotional or internally contradictory claims (e.g. "88 wins out of 97
  trades with 37 losses").
---
# Distill

1. Call `seed_distill` with the topic. It returns clusters of similar items, shared
   keywords, and automatic `flags`: big-return claims, win/loss math that doesn't add up,
   paid-product mentions, and "results not typical" fine print.
2. For each cluster write one idea: a plain-language name, how it works in 1–3 lines,
   sources (URLs), and a confidence label:
   - CONFIRMED: primary source or reproducible data
   - REPORTED: credible secondhand source
   - CLAIM: self-reported screenshot or marketing
3. Keep the flags. Never "fix" a contradictory number; quote it and say why it doesn't add up.
4. Save the merged write-up with `seed_note` (kind `distilled`) so the knowledge base
   compounds across runs.
