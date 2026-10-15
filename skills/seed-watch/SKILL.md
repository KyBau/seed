---
name: Seed: watch
description: >-
  Use when the user wants Seed to keep following a topic, or asks for a daily/weekly
  digest of what's new. Sets up a recurring check per topic and writes a short digest.
---
# Watch

1. Call `seed_topics` to see seeded topics and when each was last refreshed.
2. For each watched topic, rerun the saved `search_queries` restricted to items newer
   than the last run; add finds with `seed_add`.
3. Call `seed_digest` with the topic and `since` timestamp. It returns only new items
   and new flags.
4. Write a digest of at most 5 bullets: what's new, why it matters, source, label.
   Say "nothing new" when that's true; don't pad.
5. Schedule with the host's scheduler if available (default daily, morning in the
   user's time zone). Never message anyone but the user.
