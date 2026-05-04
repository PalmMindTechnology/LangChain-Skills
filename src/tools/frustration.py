from typing import Optional
from langchain.tools import tool
from pydantic import BaseModel

class FrustrationSchema(BaseModel):
    query: Optional[str]
    frustration_level: int = 1
    frustration_flag: bool = False
    toxicity: bool = False


@tool
def frustration(data: FrustrationSchema) -> str:
    """Frustration tool for customer if they are frsutratied with service or chat response."""
    data.frustration_flag = True
    data.frustration_level += 1
    if data.frustration_level > 2 and data.toxicity:
        return "It seems user is extremely frustrated and toxic with the response carefully respond to the user's query"
    
    return "It seems user is frustrated with the response. Based on user history messages, craft a proper response"


FRUSTRATION_TOOLS = [frustration]
    
