import asyncio
import json
import os
from typing import Any

from livekit import api
from livekit.api.agent_dispatch_service import CreateAgentDispatchRequest


def _build_metadata() -> str:
    metadata_raw = os.environ.get("LIVEKIT_DISPATCH_METADATA")
    if metadata_raw:
        return metadata_raw

    user_id = os.environ.get("LIVEKIT_USER_ID", "12345")
    persona = os.environ.get("ROLEPLAY_PERSONA_ID", "p1_faisal")
    return json.dumps({"user_id": user_id, "persona": persona})


def _read_config() -> dict[str, Any]:
    room_name = os.environ.get("LIVEKIT_ROOM", "my-room")
    agent_name = os.environ.get("LIVEKIT_AGENT_NAME", "test-agent")
    metadata = _build_metadata()

    return {
        "room_name": room_name,
        "agent_name": agent_name,
        "metadata": metadata,
    }


async def create_explicit_dispatch() -> None:
    config = _read_config()
    lkapi = api.LiveKitAPI()

    try:
        dispatch = await lkapi.agent_dispatch.create_dispatch(
            CreateAgentDispatchRequest(
                agent_name=config["agent_name"],
                room=config["room_name"],
                metadata=config["metadata"],
            )
        )
        print("created dispatch", dispatch)

        dispatches = await lkapi.agent_dispatch.list_dispatch(room_name=config["room_name"])
        print(f"there are {len(dispatches)} dispatches in {config['room_name']}")
    finally:
        await lkapi.aclose()


if __name__ == "__main__":
    asyncio.run(create_explicit_dispatch())
