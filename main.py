from contextlib import asynccontextmanager
from typing import AsyncIterator
from uuid import uuid4
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessageChunk

from src.schemas.chat import ChatRequest, ChatResponse
from src.core.graph import graph_instance
from src.utils.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting up == building LangGraph...")
    await graph_instance.build_graph()
    logger.info("Graph ready.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="Skills Agent API",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3000"],  # Add your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------
# Helper 
# ------
async def _invoke_graph(message: str, thread_id: str) -> tuple[str, list[str]]:
    if graph_instance.graph is None:
        raise RuntimeError("Graph has not been initialised yet.")

    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 30}
    inputs = {"messages": [HumanMessage(content=message)]}

    logger.info("Invoking graph | thread_id={} | message={}", thread_id, message)

    # ── DEBUG: stream every node so we can see the loop ──────────────────────
    messages_out = []
    loaded_skills: list[str] = []
    step = 0

    async for chunk in graph_instance.graph.astream(inputs, config=config, stream_mode="updates"):
        for node_name, node_update in chunk.items():
            step += 1
            msgs = (node_update or {}).get("messages", [])
            summary = []
            for m in msgs if isinstance(msgs, list) else []:
                role = type(m).__name__
                tool = getattr(m, "name", None)
                calls = [c["name"] for c in getattr(m, "tool_calls", []) or []]
                content_preview = str(getattr(m, "content", ""))[:80]
                summary.append(f"{role}(tool={tool}, calls={calls}, content={content_preview!r})")

            logger.info(
                "STEP {:02d} | node={} | messages=[{}]",
                step, node_name, " | ".join(summary) or "none"
            )

            # collect tool results for loaded_skills extraction
            for m in msgs if isinstance(msgs, list) else []:
                if m.__class__.__name__ == "ToolMessage" and getattr(m, "name", None) == "load_skill":
                    try:
                        data = json.loads(m.content)
                        loaded_skills.extend(data.get("loaded_skills", []))
                    except (json.JSONDecodeError, TypeError):
                        pass
                messages_out.append(m)
    # ─────────────────────────────────────────────────────────────────────────

    loaded_skills = list(dict.fromkeys(loaded_skills))
    reply = getattr(messages_out[-1], "content", "") if messages_out else ""

    logger.info("Graph done | thread_id={} | loaded_skills={}", thread_id, loaded_skills)
    return reply, loaded_skills

# ------------
# Endpoints
# ------------
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """
    Send a message to the skills agent and receive its reply.
    Pass the same `thread_id` on subsequent requests to continue
    the conversation (state is persisted in Redis via the checkpointer).
    """
    try:
        reply, loaded_skills = await _invoke_graph(req.message, req.thread_id)
    except Exception as exc:
        logger.exception("Graph invocation failed: {}", exc)
        raise HTTPException(status_code=500, detail=str(exc))

    return ChatResponse(
        reply=reply,
        thread_id=req.thread_id,
        loaded_skills=loaded_skills,
    )


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest) -> StreamingResponse:
    if graph_instance.graph is None:
        raise HTTPException(status_code=503, detail="Graph not initialised.")

    config = {"configurable": {"thread_id": req.thread_id}}
    inputs = {"messages": [HumanMessage(content=req.message)]}

    async def _event_generator():
        try:
            async for chunk in graph_instance.graph.astream(
                inputs,
                config=config,
                stream_mode="messages",
                version="v2",
            ):
                if chunk["type"] != "messages":
                    continue

                message_chunk, metadata = chunk["data"]

                # Skip anything not produced by an AI node
                # (filters out HumanMessage, tool messages, etc.)
                if not isinstance(message_chunk, AIMessageChunk):
                    continue

                # Skip tool-call tokens (content is empty, chunk has tool_call_chunks)
                token = getattr(message_chunk, "content", "")
                if not token:
                    continue

                # No trailing space — SSE spec: "data: " + payload + "\n\n"
                yield f"data: {token}\n\n"

        except Exception as exc:
            logger.exception("Streaming error: {}", exc)
            yield f"event: error\ndata: {exc}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        _event_generator(),
        media_type="text/event-stream",
        headers={"X-Thread-Id": req.thread_id},
    )


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "graph_ready": graph_instance.graph is not None,
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8089, log_level="info", reload=True)