from langchain.agents.middleware import ModelRequest, ModelResponse, AgentMiddleware
from langchain_core.messages import SystemMessage
from typing import Callable

from src.skills.registry import SKILLS, SKILL_MAP


_SKILLS_MARKER = "<!-- skills-injected -->"
_LOADED_MARKER = "<!-- loaded-skills -->"


class SkillMiddleware(AgentMiddleware):
    """
    Injects the skills menu into the system prompt (once, no duplication).
    Also appends inline instructions for every skill loaded in the current
    runtime state.
    """

    def __init__(self):
        self.skills_prompt = "\n".join(
            f"- {s.name}: {s.description}" for s in SKILLS
        )

    def wrap_model_call(
    self,
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
    *,
    runtime=None,
) -> ModelResponse:

        original: str = request.system_message.content

        loaded: list[str] = (
            runtime.state.get("loaded_skills", []) if runtime else []
        )

        # Skills menu (inject once, guard with marker)
        if _SKILLS_MARKER not in original:
            skills_addendum = (
                "\n\n## Available Skills\n"
                f"{self.skills_prompt}\n"
                "Call `load_skill` with a skill name before using its specialized tools.\n"
                "Use tools only when necessary. Do not repeat tool calls.\n"
                + (f"Already loaded skills (do NOT call load_skill for these again): {', '.join(loaded)}\n" if loaded else "")
                + f"{_SKILLS_MARKER}"
            )
        else:
            # Update the already-loaded notice even on subsequent turns
            if _SKILLS_MARKER in original:
                before_marker = original[: original.index(_SKILLS_MARKER)]
                # Strip old "Already loaded" line if present
                lines = [l for l in before_marker.split("\n") if "Already loaded skills" not in l]
                original = "\n".join(lines)

            skills_addendum = (
                (f"\nAlready loaded skills (do NOT call load_skill for these again): {', '.join(loaded)}\n" if loaded else "")
                + f"{_SKILLS_MARKER}"
            )

        # Active skill instructions
        if _LOADED_MARKER in original:
            original = original[: original.index(_LOADED_MARKER)]

        loaded_instructions = ""
        if loaded:
            loaded_instructions = f"\n\n{_LOADED_MARKER}"
            for name in loaded:
                skill = SKILL_MAP.get(name)
                if skill:
                    loaded_instructions += (
                        f"\n\n### Active Skill: {skill.name}\n{skill.content}"
                    )

        new_content = original + skills_addendum + loaded_instructions
        return handler(request.override(system_message=SystemMessage(content=new_content)))