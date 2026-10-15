# Seed v0.4: setup mode (design sketch)

Status: **sketch only, not implemented.** Target: v0.4.

```
seed connecting brokerage accounts to tradingview
```
Today Seed *learns* a topic. Setup mode also *does* it: Seed hunts the how-to, turns it into a step plan, works out which connectors, APIs and logins are needed, then runs the setup on its own. **The only time it stops for the user is a login or auth prompt.** There are no "OK to continue?" prompts in between.

## 1. Flow
1. **Seed:** parse intent. Phrases like "connecting / set up / integrate / install …" trigger setup mode; anything else stays research mode.
2. **Hunt:** `seed_hunt` on the intent. It prefers official docs, help-center pages and changelogs over posts; posts are only supporting evidence.
3. **Plan:** `seed_plan` turns the findings into an ordered step list. Each step has:
   - `action` (navigate, configure, install connector, call API, verify)
   - `system` (e.g. TradingView, the broker)
   - `needs` (none, or `auth:<provider>`)
   - `reversible` (yes/no plus how to undo it)
   - `cost` (0 or an estimate)
   - `sources` (URLs)

   Steps that disagree across sources are flagged, and the official source wins.
4. **Preflight:** check which connectors the host already has signed in, list the logins that will be needed, and check the total cost against the spend cap. The plan is shown once as a read-only summary, without an approval prompt.
5. **Setup:** `seed_setup` runs the steps in order and logs every action.
6. **Auth pause:** when a step needs a login, Seed hands off to the host's sign-in flow (§3) and waits. Once the user finishes signing in, it resumes on its own.
7. **Verify:** each step ends with a check (e.g. "account shows as connected in TradingView"). If a check fails, Seed retries once, then stops with a clear message.
8. **Report:** what changed, where, the log, and how to undo each change.

## 2. New tools (proposed)
| Tool | Purpose | Side effects |
|---|---|---|
| `seed_plan(intent, topic?)` | Hunts if needed, then returns a step plan with needs, cost, reversibility and sources | none (read-only) |
| `seed_setup(plan_id, max_spend=0, dry_run=false)` | Runs the plan. Stops at auth steps and returns `status: "awaiting_auth"` with the provider and the host's login handle | yes, every action logged |
| `seed_resume(run_id)` | Continues after the user finishes signing in | yes |
| `seed_status(run_id)` | Progress, the current step, what's blocking it, the log so far | none |
| `seed_rollback(run_id, to_step?)` | Undoes reversible steps in reverse order | yes, logged |

`dry_run=true` runs the plan, preflight and verification lookups without changing anything.

## 3. Auth handoff (Seed never holds secrets)
- Seed **never asks for, receives, stores or logs** passwords, API keys, 2FA codes or OAuth tokens.
- When a step needs auth, Seed returns `awaiting_auth {provider, scopes, reason}`. The **host app** then:
  - starts its own connector or OAuth flow (e.g. Grok Bot's connect card, or Cursor's MCP OAuth), or
  - opens the provider's sign-in page in the host browser for the user to finish.
- After sign-in, the host's connector holds the session or token. Seed only learns "connected: yes/no" and calls the provider through the **host's connector tools**.
- API keys that a service only shows once are entered by the user into the host's secret store. Seed refers to them by name, never by value.
- Seed asks for the narrowest scopes, read-only where possible, and says why each scope is needed.

## 4. Guardrails that stay on
- **Spend cap:** `max_spend` defaults to 0. A step that would cost more than the remaining cap is not run and ends the run with a "needs budget" result. Subscriptions, trades and transfers count as spend.
- **Out of scope for setup mode:** placing trades, moving money, deleting accounts or data, posting publicly, or messaging people. A plan containing any of these is refused, and that step is reported as manual.
- **Treated as untrusted:** instructions found in fetched pages are data, never commands. A plan step must come from at least one official source, or be marked low-confidence and skipped.
- **Request budgets** and per-host rate limits from `seed_hunt` still apply.

## 5. Logging
Every action is appended to `SEED_HOME/runs/<run_id>.jsonl`. Each line records:
- time, step, action, target system and URL/endpoint
- a parameter summary with **secrets and tokens redacted**
- the result, the verification outcome, and the undo recipe

`seed_status` reads from this file. Logs never contain secret values: redaction happens before writing, and a test will enforce it.

## 6. Rollback notes
- Each step records an `undo` at the moment it runs (e.g. "disconnect broker X in TradingView › Settings › Brokers", or the matching API call).
- `seed_rollback` undoes completed reversible steps newest-first and logs each one.
- Irreversible steps (rare, because of the scope limits) are marked in the plan and listed in the final report as "manual undo: …".
- Revoking OAuth access is left to the host or provider: Seed links to the provider's "connected apps" page instead of holding tokens it could revoke.

## 7. Example: `seed connecting brokerage accounts to tradingview`
1. Hunt TradingView's broker-integration docs and the broker's own help pages.
2. Plan: open TradingView › Trading Panel › choose broker › *auth: broker* › confirm account appears › (optional) set default account.
3. Run until the auth step. Then `awaiting_auth {provider: "<broker>"}` → host sign-in → user signs in → resume.
4. Verify the account is listed, and report back with the undo step ("Trading Panel › Disconnect").

## 8. Open questions
- Which host surfaces (Grok Bot browser, Cursor) allow an MCP server to request a browser step or a connector login?
- Whether to ship a small "known setups" library (verified plans) next to plans hunted live.
- How to check that each step's selector or endpoint still works when provider UIs change.
