from contextlib import asynccontextmanager
from typing import AsyncIterator
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

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
    """
    Invoke the compiled graph for a single user turn.
    Returns (reply_text, loaded_skills).
    """
    if graph_instance.graph is None:
        raise RuntimeError("Graph has not been initialised yet.")

    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 10}
    inputs = {"messages": [HumanMessage(content=message)]}

    logger.info("Invoking graph | thread_id={} | message={}", thread_id, message)

    result = await graph_instance.graph.ainvoke(inputs, config=config)

    messages = result.get("messages", [])
    loaded_skills: list[str] = result.get("loaded_skills", [])

    # Last message in state is the agent's final reply
    last = messages[-1] if messages else None
    reply = getattr(last, "content", "") if last else ""

    logger.info(
        "Graph done | thread_id={} | loaded_skills={} | reply_preview={}",
        thread_id,
        loaded_skills,
        reply[:120],
    )

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


# @app.post("/chat/stream")
# async def chat_stream(req: ChatRequest) -> StreamingResponse:
#     """
#     Streaming variant yields agent tokens as Server-Sent Events.
#     """
#     if graph_instance.graph is None:
#         raise HTTPException(status_code=503, detail="Graph not initialised.")

#     config = {"configurable": {"thread_id": req.thread_id}}
#     inputs = {"messages": [HumanMessage(content=req.message)]}

#     async def _event_generator():
#         try:
#             async for chunk in graph_instance.graph.astream(
#                 inputs, config=config, stream_mode="values"
#             ):
#                 messages = chunk.get("messages", [])
#                 if not messages:
#                     continue

#                 last = messages[-1]
                
#                 # Skip user messages
#                 if isinstance(last, HumanMessage):
#                     continue

#                 token = getattr(last, "content", "")
#                 if token:
#                     yield f"data: {token}\n\n"

#         except Exception as exc:
#             logger.exception("Streaming error: {}", exc)
#             yield f"event: error\ndata: {exc}\n\n"

#         yield "data: [DONE]\n\n"

#     return StreamingResponse(
#         _event_generator(),
#         media_type="text/event-stream",
#         headers={"X-Thread-Id": req.thread_id},
#     )


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "graph_ready": graph_instance.graph is not None,
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8089, log_level="info")