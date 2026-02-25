import asyncio
import httpx
import json
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from src.config import settings

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    chat_session_id: str | None = None
    context: list[str] = []


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest) -> EventSourceResponse:
    async def generate() -> Any:
        yield {"event": "start", "data": json.dumps({"status": "generating"})}

        prompt = _build_prompt(request.query, request.context)

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{settings.ollama_host}/api/generate",
                    json={
                        "model": settings.llm_model,
                        "prompt": prompt,
                        "stream": True,
                    },
                ) as resp:
                    async for line in resp.aiter_lines():
                        if not line:
                            continue
                        data = json.loads(line)
                        if token := data.get("response", ""):
                            yield {
                                "event": "token",
                                "data": json.dumps({"content": token}),
                            }
                        if data.get("done", False):
                            break
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)}),
            }

        yield {"event": "done", "data": json.dumps({"status": "complete"})}

    return EventSourceResponse(generate())


def _build_prompt(query: str, context: list[str]) -> str:
    system_prompt = (
        "あなたは生産工場のナレッジベースアシスタントです。\n"
        "提供された情報源のみに基づいて回答してください。\n"
        "情報源にない内容は「該当する情報が見つかりませんでした」と回答してください。\n"
        "日本語で回答してください。\n"
    )

    context_text = "\n\n".join(context) if context else "情報源なし"

    return (
        f"{system_prompt}\n\n"
        f"【提供された情報源】\n{context_text}\n\n"
        f"【ユーザーの質問】\n{query}"
    )
