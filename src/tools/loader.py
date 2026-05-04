import json
from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from src.skills.registry import SKILL_MAP

LOADED_SKILLS_KEY = "__loaded_skills__"


@tool
def load_skill(
    skill_name: str,
    state: Annotated[dict, InjectedState],
) -> str:
    """
    Loads a skill by name, making its tools available for this and future
    turns. Already-loaded skills are not re-loaded.
    """
    skill = SKILL_MAP.get(skill_name)
    if not skill:
        available = ", ".join(SKILL_MAP.keys())
        return f"Skill '{skill_name}' not found. Available skills: {available}"

    current_loaded: list[str] = list(state.get("loaded_skills", []))

    if skill_name in current_loaded:
        return f"Skill '{skill_name}' is already loaded."

    updated = current_loaded + [skill_name]

    return json.dumps({
        LOADED_SKILLS_KEY: updated,
        "message": (
            f"Loaded skill: {skill.name}\n\n"
            f"Instructions:\n{skill.content}"
        ),
    })