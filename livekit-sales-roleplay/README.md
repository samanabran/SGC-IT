# LiveKit Sales Roleplay Agent

This folder contains a ready LiveKit voice agent for sales roleplay training.

## What it does

- Acts as a buyer persona for sales call practice
- Supports objection handling practice (budget, timing, authority, risk)
- Difficulty levels: `easy`, `medium`, `hard`
- Gives a short performance debrief at the end
- Uses Deepgram Aura TTS for more human-like voice
- Persona-by-file setup under `personas/`

## 1) Install

```bash
cd livekit-sales-roleplay
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

## 2) Configure environment

Copy and edit:

```bash
cp .env.example .env
```

Required LiveKit values:
- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`

Required voice value:
- `DEEPGRAM_API_KEY`

Roleplay selection:
- `ROLEPLAY_PERSONA_ID` (`p1_faisal`, `p2_noura`, `p3_omar`, `p4_rajesh`)

Persona files:
- `personas/p1_faisal.py`
- `personas/p2_noura.py`
- `personas/p3_omar.py`
- `personas/p4_rajesh.py`

## 3) Run in terminal (quick test)

```bash
python agent.py console --text
```

## 4) Run for LiveKit clients

```bash
python agent.py dev
```

Then connect from LiveKit Agents Playground or any LiveKit client using the same `LIVEKIT_` env values.

## 5) Create explicit agent dispatch (optional)

Use this to proactively dispatch an agent into a room:

```bash
python create_dispatch.py
```

Optional env vars for dispatch script:
- `LIVEKIT_ROOM` (default: `my-room`)
- `LIVEKIT_AGENT_NAME` (default: `test-agent`)
- `LIVEKIT_DISPATCH_METADATA` (default built from `LIVEKIT_USER_ID`)
- `LIVEKIT_USER_ID` (default: `12345`)

## Notes

- Current model stack:
  - STT: `deepgram/nova-3`
  - LLM: `openai/gpt-4.1-mini`
  - TTS: Deepgram Aura voice from persona `voice_id`
- You can add more personas in `personas/` and register them in `personas/__init__.py`.
