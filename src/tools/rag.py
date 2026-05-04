from langchain.tools import tool
from src.utils.logging import logger
from src.tools.knowledge_base import KNOWLEDGE_DB

@tool
def general_info(category: str) -> str:
    """Basic FAQ lookup"""
    logger.info(f"general_info called | query_category={category}")

    normalized_query = category.lower()

    for k, v in KNOWLEDGE_DB.items():
        if k in normalized_query:
            logger.success(f"FAQ match found | category={k}")
            return v

    logger.warning(f"No FAQ match found | query_category={category}")
    return "No info found"


@tool
def escalate_support_team(query: str) -> str:
    """Escalates support team for a given non-answerable by rag general_info tool."""
    logger.info(f"Support escalation triggered | query={query}")

    result = f"Your {query} escalated to support team"
    logger.success(f"Escalation completed | query={query}")
    return result


RAG_TOOLS = [
    general_info,
    escalate_support_team,
]