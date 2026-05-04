from typing import Any
from pydantic import BaseModel

class SkillRegistry(BaseModel):
    name: str
    description: str
    content: str
    tools: list[Any]