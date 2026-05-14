# LiveKit Sales Roleplay Agent

This folder contains the local worker that powers the browser-based sales roleplay experience.

## What is live today

- Browser page: `/roleplay.html`
- Secure session endpoint: `/api/roleplay-token`
- Hosting: Vercel
- Realtime transport: LiveKit Cloud
- Worker runtime: local Python process started with `python agent.py dev`
- Voice stack:
  - STT: `deepgram/nova-3`
  - LLM: `openai/gpt-4.1-mini`
  - TTS: Deepgram Aura voice from persona `voice_id`

## Architecture

1. The browser opens `/roleplay.html`.
2. The page calls `/api/roleplay-token` on Vercel.
3. The API generates a short-lived LiveKit token and optionally creates an agent dispatch.
4. The browser joins the LiveKit room using the token.
5. A local worker started from this folder registers with LiveKit and picks up the dispatch.
6. The persona joins as a remote participant and audio is attached in the browser.

## Prerequisites

- Python virtual environment available at project root: `../.venv`
- LiveKit Cloud project and credentials
- Deepgram API key
- Working internet connection to LiveKit Cloud and Deepgram

## Local install

Run from the repository root:

```bash
source .venv/Scripts/activate
pip install -r livekit-sales-roleplay/requirements.txt
```

## Environment setup

Create `livekit-sales-roleplay/.env`.

Required variables:

- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `DEEPGRAM_API_KEY`
- `ROLEPLAY_PERSONA_ID`

Supported personas:

- `p1_faisal`
- `p2_noura`
- `p3_omar`
- `p4_rajesh`

## Run the worker

Use Git Bash from the repository root:

```bash
cd "/d/01_WORK_PROJECTS/Important Documents -SGC/sgc-overlay-temp/SGC-IT/livekit-sales-roleplay"
source ../.venv/Scripts/activate
python agent.py dev
```

Healthy startup includes a line similar to:

```text
registered worker {"url": "wss://...livekit.cloud"}
```

Keep this terminal open while testing in the browser.

## Quick smoke test

1. Open `/roleplay.html` in production.
2. Click `Start Roleplay`.
3. Allow microphone access.
4. Confirm status progresses through:
   - `Generating secure session...`
   - `Connected to room ...`
   - `Participant joined ...`
   - `Persona audio attached.`

## Failure modes and fixes

### Worker fails with `LIVEKIT_URL` error

Cause: `.env` missing or required env vars not loaded.

Fix:

1. Ensure `livekit-sales-roleplay/.env` exists.
2. Confirm it contains all required keys.
3. Restart `python agent.py dev`.

### Browser says no persona joined yet

Cause: dispatch succeeded but no active worker picked up the job.

Fix:

1. Check the worker terminal is still running.
2. Confirm worker registered successfully.
3. Confirm the worker can reach LiveKit and Deepgram.

### Dispatch succeeds but browser appears to stay on same URL

This is expected. The room opens on the same page and does not redirect.

## Optional dispatch utility

To create an explicit dispatch manually:

```bash
python create_dispatch.py
```

Optional variables:

- `LIVEKIT_ROOM`
- `LIVEKIT_AGENT_NAME`
- `LIVEKIT_DISPATCH_METADATA`
- `LIVEKIT_USER_ID`

## Hardening notes

- Keep secrets only in Vercel env and local `.env`; never commit them.
- Treat the token as temporary session data only.
- If dispatch starts failing after secret updates, re-enter secrets carefully to avoid hidden newline characters.
- Keep `LIVEKIT_ENABLE_DISPATCH=true` in production if you want one-click browser start.
- Keep the local worker terminal isolated from shell history sharing when practical.
