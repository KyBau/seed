---
name: Seed: watch
description: >-
  Use when the user wants Seed to keep following a topic, or asks for a daily or weekly digest of
  what's new. Each run is one seed_hunt per topic plus seed_digest.
---
# Watch

1. Call `seed_topics` to list the seeded topics and their saved queries.
2. For each watched topic, call `seed_hunt` with `seed` set to the topic's original post or idea (or its best saved query) and `topic` set to the slug. Use a small `budget` (10–20). Known URLs are skipped automatically, so only new finds get added.
3. Call `seed_digest` with the topic and the time of the last run (`since`). It returns only new items and new flags.
4. Write a digest of at most 5 bullets: what's new, why it matters, source, and label (CONFIRMED / REPORTED / CLAIM). If nothing changed, say "nothing new".
5. Schedule it with the host's scheduler if available. Default is daily, in the morning in the user's time zone. Never message anyone but the user.
