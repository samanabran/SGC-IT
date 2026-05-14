# Roleplay Live Runbook

This document captures the exact path used to get the roleplay flow from broken state to working live state.

## Final live outcome

- Production site: `https://sgc-it-roleplay.vercel.app`
- Roleplay page: `https://sgc-it-roleplay.vercel.app/roleplay.html`
- Token endpoint: `https://sgc-it-roleplay.vercel.app/api/roleplay-token?persona=p1_faisal`
- Local worker: `python agent.py dev`

## Working architecture

1. Vercel hosts the static site and Node API route.
2. The API route generates a short-lived LiveKit token.
3. The API route attempts agent dispatch when enabled.
4. The browser joins the room with `livekit-client`.
5. The local Python worker registers to LiveKit and picks up the dispatch.
6. The persona joins as a remote participant and returns voice audio.

## Issues that were resolved

### 1. Deployment and hosting stabilization

- Cloudflare was initially used for easier deployment.
- Vercel was then used for more reliable API + secret handling.
- `vercel.json` was configured to treat `api/**/*.js` as Node functions and other files as static.
- `.vercelignore` was used so Python files did not confuse Vercel runtime detection.

### 2. Dispatch authentication failure

- Symptom: `/api/roleplay-token` returned `dispatchError: invalid token`.
- Root cause: malformed Vercel secret formatting for `LIVEKIT_API_SECRET`.
- Fix: remove and re-add the Vercel secret cleanly, then redeploy.

### 3. Browser appeared to do nothing on `Start Roleplay`

- Symptom: same URL remained open and user believed room did not open.
- Root cause: the experience is intentionally in-page with no redirect.
- Fix:
  - added auto-generate session support
  - added clearer connection messages
  - added timeout warning when no persona joins

### 4. Dispatch created but no persona joined

- Symptom: API returned a dispatch object, but `jobs` remained empty.
- Root cause: local LiveKit worker was not running or not configured.
- Fix:
  - install Python dependencies into the project virtual environment
  - create local `livekit-sales-roleplay/.env`
  - start `python agent.py dev`

### 5. Worker startup failure

- Symptom: `ValueError: ws_url is required, or set LIVEKIT_URL environment variable`
- Root cause: no local `.env` and no shell environment variables.
- Fix:
  - create `livekit-sales-roleplay/.env`
  - load `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, `DEEPGRAM_API_KEY`
  - restart worker

## Final setup procedure

### A. Vercel configuration

Set these environment variables in Vercel production:

- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `DEEPGRAM_API_KEY`
- `LIVEKIT_ENABLE_DISPATCH=true`
- `LIVEKIT_AGENT_NAME=test-agent`

Deploy from repository root:

```bash
npx vercel --prod --yes
```

### B. Local worker setup

From repository root:

```bash
source .venv/Scripts/activate
pip install -r livekit-sales-roleplay/requirements.txt
cd livekit-sales-roleplay
python agent.py dev
```

Healthy worker output includes `registered worker`.

### C. Browser test

1. Open the roleplay page.
2. Click `Start Roleplay`.
3. Allow microphone access.
4. Confirm the page reports room connection.
5. Confirm a participant joins.
6. Confirm persona audio is attached.

## Smoke tests used

### Production URL checks

- `/` returned `200`
- `/roleplay.html` returned `200`
- `/api/roleplay-token?persona=p1_faisal` returned `200`
- `dispatchError` became `null`
- token was present

### Worker checks

- dependency install succeeded from `requirements.txt`
- worker reached `registered worker`
- LiveKit URL resolved to `wss://test-7uu4c43i.livekit.cloud`

## Operational guidance

- Keep the local worker terminal open while using browser roleplay.
- Regenerate a session if token lifetime expires.
- If Vercel dispatch breaks unexpectedly, re-check secret formatting first.
- If the browser reports no persona joined, inspect the worker terminal before changing frontend code.

## Hardening applied

- API route now trims env vars before use.
- API route validates `LIVEKIT_URL` format.
- API route sanitizes user-controlled room and identity query parameters.
- API route adds `Cache-Control: no-store` and `Pragma: no-cache`.
- API route now uses UUID-based identity suffixes instead of low-entropy random numbers.
- API route now wraps JWT creation in explicit error handling.
- API route now emits structured logs for token issuance and dispatch failures.
- API response now returns only `dispatchId` and `dispatchCreated` instead of the full dispatch object.
- Browser UI now surfaces worker-offline symptoms instead of failing silently.

## Recommended next operational improvements

1. Run the worker in a managed process instead of a developer terminal.
2. Add authentication and rate limiting to `/api/roleplay-token` before public external launch.
3. Rotate LiveKit and Deepgram secrets after setup is fully handed over.
4. Add a dedicated health endpoint or dashboard for worker registration status.