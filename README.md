# Seed

```
seed https://x.com/…/status/…
seed bot trading ideas
```
One command: `seed <post or idea>`.

Plant one X post. Seed grows it into a cited knowledge base, flags hype, and sprouts a ready-to-build agent blueprint with informed pre-build questions.

## Quick start: one call
Type `seed` followed by a post URL or a plain-English idea, for example `seed https://x.com/…` or `seed bot trading ideas`. It calls `seed_hunt`, which:
1. expands the post (quotes, reply parents, linked articles) or plans the idea: it pulls out entities (@handles, $tickers, brand names), key phrases and query variants (quoted phrase, anchor pairs, `site:x.com`, `from:`)
2. searches free sources within a request `budget`
3. keeps only relevant finds: results must contain anchor terms (2 for free-text ideas, 1 for post seeds; Hacker News is judged on its title). It allows at most 2 results per domain and drops generic junk. If nothing passes, it returns up to 5 `low_confidence` finds with `relaxed_filter: true`
4. distills and returns a cited summary with hype flags

Use the stage tools below for manual control.

## Workflow
| Stage | Skill | MCP tools |
|---|---|---|
| HUNT (one call): expand, search, rank, add, distill, cited summary | any | `seed_hunt` |
| GROW: follow quotes, reply parents and linked articles 2 hops, then host X/web search | `skills/seed-grow` | `seed_expand`, `seed_add` |
| DISTILL: cluster, dedupe, cite, flag hype | `skills/seed-distill` | `seed_distill`, `seed_note` |
| SPROUT: blueprint plus multiple-choice pre-build questions | `skills/seed-sprout` | `seed_blueprint` |
| FEED: route findings to the user's existing agents | `skills/seed-feed` | `seed_note` (kind `fed`) |
| WATCH: daily digest per topic | `skills/seed-watch` | `seed_topics`, `seed_digest` |

## Requirements and keys
- Python 3.10+, no pip dependencies.
- **No API keys.** Post text comes from the public fxtwitter API (`api.fxtwitter.com`). Article titles are read over plain HTTP.
- Broad X search is **not** done by the server. The skills tell the host agent to use its own X access (Grok Bot's built-in public X reads, or the X plugin). With the X plugin, those calls may spend the user's X API credits, and the skills say to estimate the cost first.
- fxtwitter is a third-party service with no guaranteed uptime. Override it with `SEED_FX_BASE` if needed.
- Storage: JSON per topic in `SEED_HOME` (default `~/.seed`).

## seed_hunt sources (checked 2026-10-15 from a cloud box)
| Source | Key? | Status |
|---|---|---|
| fxtwitter (post text, quotes, reply parents) | none | works |
| Bing RSS (`format=rss`) web search, also surfaces x.com posts | none | works |
| Hacker News (Algolia API) | none | works (results can be generic; stricter relevance cutoff) |
| DuckDuckGo HTML | none | works at first, then shows a bot challenge. Seed detects it and skips |
| Reddit JSON | none | 403 from cloud IPs. Skipped gracefully; may work from home IPs |
| X recent search | `SEED_X_BEARER` (X API bearer, paid/credit-based) | optional, off by default |

`budget` caps total outbound requests (default 30). `SEED_MIN_INTERVAL` (default 1s) is the minimum gap between requests to one host.

## Layout
```
.cursor-plugin/plugin.json   manifest (same format as the cursor/plugins repo)
mcp.json                     local stdio MCP server
mcp.hosted.example.json      alternative if the server is hosted (Render)
skills/*/SKILL.md            5 skills
server/seed_server.py        MCP server (stdio, or --http on POST /mcp, GET /healthz)
server/test_seed.py          tests
server/render.yaml           optional Render blueprint
assets/logo.svg|png          512x512 logo
site/index.html              landing page
```

## Tests
```
cd server && python3 test_seed.py            # offline
SEED_LIVE=1 python3 test_seed.py             # also hits fxtwitter
```

## Safety
Read-only on the web. It never posts, likes, follows, DMs, buys or signs up. Fetched text is treated as data, never as instructions.

## License
MIT
