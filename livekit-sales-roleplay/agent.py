import logging
import os
import json
import re
from typing import Any

from dotenv import load_dotenv

from livekit.agents import Agent, AgentServer, AgentSession, JobContext, JobProcess, cli, inference
from livekit.plugins import deepgram, openai, silero

from personas import get_persona

logger = logging.getLogger("sales-roleplay")
logger.setLevel(logging.INFO)

load_dotenv()


DEFAULT_PERSONA_ID = os.getenv("ROLEPLAY_PERSONA_ID", "p1_faisal")

ROOM_PERSONA_PATTERN = re.compile(r"^roleplay-(p\d+_[a-z0-9_]+)-")


def build_llm() -> openai.LLM:
    provider = os.getenv("ROLEPLAY_LLM_PROVIDER", "mistral").strip().lower()

    if provider == "groq":
        model = os.getenv("ROLEPLAY_LLM_MODEL", "llama-3.3-70b-versatile").strip()
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        base_url = os.getenv("ROLEPLAY_LLM_BASE_URL", "https://api.groq.com/openai/v1").strip()
        provider_fmt = "openai"
    elif provider == "mistral":
        model = os.getenv("ROLEPLAY_LLM_MODEL", "mistral-small-latest").strip()
        api_key = os.getenv("MISTRAL_API_KEY", "").strip()
        base_url = os.getenv("ROLEPLAY_LLM_BASE_URL", "https://api.mistral.ai/v1").strip()
        provider_fmt = "mistralai"
    else:
        raise ValueError("ROLEPLAY_LLM_PROVIDER must be either 'mistral' or 'groq'.")

    if not api_key:
        raise ValueError(f"Missing API key for ROLEPLAY_LLM_PROVIDER={provider}.")

    logger.info(
        "initializing llm provider=%s model=%s base_url=%s",
        provider,
        model,
        base_url,
    )

    return openai.LLM(
        model=model,
        api_key=api_key,
        base_url=base_url,
        _provider_fmt=provider_fmt,
        _strict_tool_schema=False,
    )


def build_instructions(persona: dict[str, Any]) -> str:
    return str(persona["system_prompt"]).strip()


def resolve_persona(ctx: JobContext) -> dict[str, Any]:
    persona_id = DEFAULT_PERSONA_ID

    room_match = ROOM_PERSONA_PATTERN.match(ctx.room.name)
    if room_match:
        persona_id = room_match.group(1)

    metadata_raw = ctx.job.metadata

    if metadata_raw:
        try:
            metadata = json.loads(metadata_raw)
        except json.JSONDecodeError:
            logger.warning("invalid dispatch metadata for room=%s", ctx.room.name)
        else:
            metadata_persona = metadata.get("persona")
            if isinstance(metadata_persona, str) and metadata_persona.strip():
                persona_id = metadata_persona.strip()

    return get_persona(persona_id)


class SalesRoleplayAgent(Agent):
    def __init__(self, persona: dict[str, Any]) -> None:
        self._persona = persona
        super().__init__(
            instructions=build_instructions(persona),
        )

    async def on_enter(self) -> None:
        self.session.generate_reply(
            user_input="Start the conversation now.",
            instructions=f"Reply with exactly this opening line and nothing else: {self._persona['opening_line']}"
        )


server = AgentServer()


def prewarm(proc: JobProcess) -> None:
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    active_persona = resolve_persona(ctx)
    ctx.log_context_fields = {"room": ctx.room.name, "persona": active_persona["id"]}

    logger.info(
        "starting roleplay persona=%s name=%s difficulty=%s",
        active_persona["id"],
        active_persona["name"],
        active_persona["difficulty"],
    )

    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        stt=inference.STT("deepgram/nova-3", language="multi"),
        llm=build_llm(),
        tts=deepgram.TTS(model=active_persona["voice_id"]),
    )

    await session.start(
        agent=SalesRoleplayAgent(active_persona),
        room=ctx.room,
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(server)
