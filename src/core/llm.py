from __future__ import annotations

from functools import lru_cache
from langchain_openai import ChatOpenAI

from src.config import settings
from src.utils.logging import logger

def _build_llm(model_name: str) -> ChatOpenAI:
    """Internal factory for creating ChatOpenAI instance"""

    try:
        return ChatOpenAI(
            model=model_name,
            api_key=settings.openai_api_key,
            # top_p=0.4,
            # temperature=0.2,
            # max_completion_tokens=4096,  
            request_timeout=30, 
            max_retries=2
        )

    except Exception as e:
        logger.exception("Unexpected error during model initialization")
        raise f"Failed to initialize model: {str(e)}"


@lru_cache(maxsize=1)
def get_llm(model_name: str = "gpt-5.4-mini") -> ChatOpenAI:
    return _build_llm(model_name=model_name)