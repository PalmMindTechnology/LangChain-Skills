from langchain.tools import tool
from src.tools.knowledge_base import RETENTION_DB


@tool
def retention_faq_info(query: str) -> str:
    """Retention tool for customer if they want to leave our service."""
    q = query.lower()
    for k, v in RETENTION_DB.items():
        if k in q:
            return v

    return "Let me know if you'd like a better plan recommendation."

RETENTION_TOOLS = [retention_faq_info]