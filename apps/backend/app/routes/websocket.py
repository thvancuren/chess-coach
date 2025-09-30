"""WebSocket routes for real-time updates."""

import asyncio
import os
from contextlib import suppress

import redis.asyncio as aioredis
from redis.asyncio.client import PubSub
from redis.exceptions import RedisError
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)


async def _relay_pubsub_messages(pubsub: PubSub, websocket: WebSocket) -> None:
    """Forward messages from Redis pub/sub to the WebSocket."""
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message is None:
                await asyncio.sleep(0.1)
                continue
            if message.get("type") != "message":
                continue
            data = message.get("data")
            if data is None:
                continue
            await websocket.send_text(data)
    except asyncio.CancelledError:
        raise
    except (WebSocketDisconnect, RedisError):
        pass


async def _wait_for_disconnect(websocket: WebSocket) -> None:
    """Waits until the client disconnects."""
    with suppress(WebSocketDisconnect):
        await websocket.receive_text()


@router.websocket("/analysis/{username}")
async def websocket_analysis_progress(websocket: WebSocket, username: str):
    """WebSocket endpoint for analysis progress updates."""
    await websocket.accept()

    channel = f"analysis_progress:{username}"
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)

    relay_task = asyncio.create_task(_relay_pubsub_messages(pubsub, websocket))
    disconnect_task = asyncio.create_task(_wait_for_disconnect(websocket))

    done, pending = await asyncio.wait({relay_task, disconnect_task}, return_when=asyncio.FIRST_COMPLETED)

    for task in pending:
        task.cancel()
    with suppress(asyncio.CancelledError):
        await asyncio.gather(*pending, return_exceptions=True)

    await pubsub.unsubscribe(channel)
    await pubsub.close()

    for task in done:
        with suppress(Exception):
            task.result()

