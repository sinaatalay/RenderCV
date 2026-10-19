# Session Handoff — RenderCV Web Editor

Last updated: 2026-10-19, after checking the Render dashboard. Read this
together with [cv-editor-web-app.md](cv-editor-web-app.md), whose Progress
section carries the per-phase verification evidence.

## Status on 2026-10-19: the deployment is down

`main` is at PR #54 (`9e420e1`, last code change 2026-09-10), and `develop`
carries nothing beyond it. Every one of the 28 deploys of `rendercv-web`
built and went live, through PR #54. Nothing has been merged since.

**The service is now failing at startup, and it is not the code.** On the
Render dashboard:

| Resource | Status | Cause |
| --- | --- | --- |
| `rendercv-web-db` (Postgres, free) | Suspended by Render | *Free database expired.* Render deletes it and its data **within a day** unless it is upgraded to a paid plan |
| `rendercv-web` (Docker, free) | Failed service | The startup migration cannot reach the database: `psycopg.OperationalError: failed to resolve host 'dpg-daen9if40ujc73fumqn0-a'`, then `Application startup failed. Exiting.` |
| `p041-backend` | Failed deploy | Built from a different repository (`P041-Version-3.0`), one Blueprint deploy a month ago. Not this project |

Render's free Postgres has a fixed lifetime from creation; the database was
created about a month before this check. Redeploying the web service changes
nothing while the database is gone. The way back is one of:

1. **Upgrade `rendercv-web-db` to a paid instance** before deletion. Keeps
   every user's CVs and needs no change here.
2. **Let it go and recreate it.** Create a new free database (from the
   Blueprint, or by hand) and point `RENDERCV_WEB_DATABASE_URL` at it; the
   migrations run on startup. Every existing account and CV is lost, and the
   new database expires the same way.
3. **Move to a provider without an expiry** (Neon, Supabase), setting
   `RENDERCV_WEB_DATABASE_URL` by hand and dropping `fromDatabase` from
   `render.yaml`. Same data loss as option 2 unless the data is copied first,
   which needs the database to be reachable -- that is, option 1 first.

The choice is about money and users' data, so it is the owner's.

## Work merged after the plan closed (PR #20 – #54)

All of it on `main` and deployed:

- Deployment proved on Render: Postgres confirmed by restart, a smoke test
  from outside, schema.json and the core's Typst baked into the image, the
  image slimmed by 712 MB.
- Google sign-in published to external users; Search Console verification;
  privacy policy; account deletion.
- Editor: a new CV opens on the filled-in example; YAML download and
  import; download as images (every page); form editors fixed; theme
  switcher no longer shows a stale document.
- Operations: database password rotation runbook, a script reporting who
  uses the deployment, deploy checks recorded in
  [the runbook](../../runbooks/enable-google-sign-in-and-postgres.md).

## Where things stand

**The plan is complete.** Everything is merged to `develop`:

- PR #1 (`dd8250e`'s parent, `f831a58`) — phases 0-5, the build roadmap.
- PR #2 (`dd8250e`) — phase 6: landing-first routing, Google sign-in, and
  the fixes that made deployment actually possible.

`main` is untouched and still guarded by the PreToolUse hook. Branches
`quan` and `quan-phase6` are merged but not deleted.

Gates on `develop`: core 1540 passed (2 Windows skips), backend 104/104,
svelte-check 0 errors (366 files), Vitest 295/295, Playwright 35/35,
`just check` clean.

## What is left, and it is not code

Both need credentials this repository does not have:

1. **Google OAuth.** Create a client in Google Cloud Console and set
   `GOOGLE_OAUTH_CLIENT_ID` / `_SECRET` / `_REDIRECT_URI`. The exact
   redirect URI is in `web/README.md`. Until then the app runs anonymously
   and the sign-in UI stays hidden, which is a supported state, not a
   broken one. The backend tests patch one seam because the real flow ends
   at Google's consent screen, so **the first real sign-in still needs a
   human**.
2. **Postgres.** Pick a provider, then run the migration against it before
   anything else: only driver and dialect resolution were exercised here
   (the Docker daemon was unavailable), plus the full migration round trip
   on SQLite. `uv sync --extra postgres` is required; a pasted
   `postgres://` or `postgresql://` URL is normalized in code.

`RENDERCV_WEB_SECRET` and `RENDERCV_WEB_HTTPS` must both be set before any
deployment. `web/README.md` is the operator's document; this file is not.

## How this project was run

1. Per phase: present a change list → user approves → implement → run every
   gate → report → commit only after the user has seen the result.
2. Push over HTTPS; SSH is broken on this machine:
   `git push https://github.com/NguyenMinhQuan-2A202601478/rendercv_P-041.git <branch>`
3. `/code-review` after each PR, before merging. It earned its place: it
   found 10 real defects in PR #1 and 5 in PR #2, including one that
   destroyed a user's account when a second person signed in on the same
   browser. Both times the fixes came with regression tests that were
   verified to fail without them.

## Gates

- Repo: `just check`, `just test` (expect 2 Windows skips).
- Backend: `cd web/backend && uv run pytest -q`.
- Frontend: `npm run check && npm run test && npm run build`, then
  `npx playwright test` — the e2e suite needs a backend on port 8000 with a
  **throwaway** database, never `web/backend/data/rendercv_web.db`. See
  `web/README.md` for the exact commands.

## Known debt

None of it blocking, all of it recorded in the plan's Result section:

- Signing out is account-wide, not per-device: one account has one
  `session_token`, and per-device sessions need a `sessions` table. The
  safe direction of the two was chosen deliberately.
- The favicon is still the SvelteKit default.
- The photo field accepts a URL but not an upload; local paths 422 by
  design, with a clear message.
- Placeholder documents are defined twice — `web/backend/defaults.py` and
  the frontend's `createDefaultDocuments()` — with no shared source.
- The versions/history panel has no e2e coverage.
- Harness payload files (`.agents/`, `.harness-core/`,
  `docs/assets/rendercv_skill.zip`) and `graphify-out/` sit modified by
  hooks and uncommitted; commit as a chore or discard, the user's call.
- `full_repository/` and `image/` are the user's untracked scratch
  directories at the repository root — leave them alone.
