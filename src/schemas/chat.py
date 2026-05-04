from uuid import uuid4
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message to the agent")
    thread_id: str = str(uuid4())


class ChatResponse(BaseModel):
    reply: str
    thread_id: str
    loaded_skills: list[str]