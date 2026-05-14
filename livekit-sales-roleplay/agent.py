import logging
import os

from dotenv import load_dotenv

from livekit.agents import Agent, AgentServer, AgentSession, JobContext, JobProcess, cli, inference
from livekit.plugins import deepgram, silero

from personas import get_persona

logger = logging.getLogger("sales-roleplay")
logger.setLevel(logging.INFO)

load_dotenv()


PERSONA_ID = os.getenv("ROLEPLAY_PERSONA_ID", "p1_faisal")
ACTIVE_PERSONA = get_persona(PERSONA_ID)


def build_instructions() -> str:
    return ACTIVE_PERSONA["system_prompt"].strip()


class SalesRoleplayAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=build_instructions(),
        )

    async def on_enter(self) -> None:
        self.session.generate_reply(
            instructions=f"Start immediately with this opening line: {ACTIVE_PERSONA['opening_line']}"
        )


server = AgentServer()


def prewarm(proc: JobProcess) -> None:
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    ctx.log_context_fields = {"room": ctx.room.name}

    logger.info(
        "starting roleplay persona=%s name=%s difficulty=%s",
        ACTIVE_PERSONA["id"],
        ACTIVE_PERSONA["name"],
        ACTIVE_PERSONA["difficulty"],
    )

    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        stt=inference.STT("deepgram/nova-3", language="multi"),
        llm=inference.LLM("openai/gpt-4.1-mini"),
        tts=deepgram.TTS(model=ACTIVE_PERSONA["voice_id"]),
    )

    await session.start(
        agent=SalesRoleplayAgent(),
        room=ctx.room,
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(server)
