# Vercel Roleplay Secret Setup

Set these in Vercel Project Settings -> Environment Variables:

- LIVEKIT_URL
- LIVEKIT_API_KEY
- LIVEKIT_API_SECRET

Optional:
- ROLEPLAY_DEFAULT_PERSONA (defaults to p1_faisal)

## Verify API

After deployment, check:

- /api/roleplay-token?persona=p1_faisal

Expected: JSON with `wsUrl`, `room`, `identity`, `token`, `expiresIn`.

## Why this is safer

- Secrets stay on Vercel server-side.
- Browser gets only short-lived token.
- No user-side API keys needed.
