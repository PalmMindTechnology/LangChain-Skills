import json
# from typing import Annotated
# from langgraph.prebuilt import InjectedState
from langchain_core.tools import tool

from src.skills.registry import SKILLS
from src.utils.logging import logger


@tool
def load_skill(skill_name: str) -> str:
    """
    Load the full content of a skill into the agent's context.

    Use this when you need detailed information about how to handle a specific
    type of request. This will provide you with comprehensive instructions
    and guidelines for the skill area.
    """
    # Find and return the requested skill
    for skill in SKILLS:
        if skill.name == skill_name:
            tool_names = [t.name for t in skill.tools] if skill.tools else []
            logger.info(
                "Skill loaded | name={} tools=[{}]",
                skill_name,
                ", ".join(tool_names) or "none",
            )
            return json.dumps({
                "loaded_skills": [skill_name],
                "tools": tool_names,
                "content": f"Loaded skill: {skill_name}\n\n{skill.content}",
            })

    # Skill not found
    available = ", ".join(s.name for s in SKILLS)
    logger.warning("Skill not found | requested={} available=[{}]", skill_name, available)
    return json.dumps({
        "error": f"Skill '{skill_name}' not found.",
        "available_skills": available,
    })