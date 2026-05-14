# Vercel Roleplay Secret Setup

Set these in Vercel Project Settings -> Environment Variables.

## Required

- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`

## Required for end-to-end voice roleplay

- `DEEPGRAM_API_KEY`

## Recommended

- `LIVEKIT_ENABLE_DISPATCH=true`
- `LIVEKIT_AGENT_NAME=test-agent`
- `LIVEKIT_TOKEN_TTL=15m`

## Security next step

- The current flow is optimized for frictionless demos and internal use.
- If this endpoint will remain publicly reachable, add authentication and rate limiting before broad external rollout.

## Notes

- Enter values carefully. A hidden newline in `LIVEKIT_API_SECRET` previously caused dispatch to fail with `invalid token`.
- The browser page never receives server secrets. It only receives a short-lived access token.
- The browser experience depends on both Vercel env vars and a running local worker.

## Verify API

After deployment, check:

- `/api/roleplay-token?persona=p1_faisal`

Expected response:

- `wsUrl`
- `room`
- `identity`
- `token`
- `expiresIn`
- `dispatch`
- `dispatchError`

Healthy response:

- `token` is present
- `dispatchError` is `null`

## Verify production pages

- `/`
- `/roleplay.html`

## Why this is safer

- Secrets stay on the Vercel server side.
- The API returns only a short-lived room token.
- Rotation can be done centrally in Vercel without browser changes.
