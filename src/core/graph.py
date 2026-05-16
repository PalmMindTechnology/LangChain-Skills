from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.redis.aio import AsyncRedisSaver

from src.skills.middleware import SkillMiddleware
from src.tools.skill_loader import load_skill
from src.utils.helper import load_md
from src.core.llm import get_llm
from src.config import settings
from src.utils.logging import logger
from src.schemas.agent import AgentState

LOADED_SKILLS_KEY = "loaded_skills"


class Graph:
    def __init__(self):
        self.checkpointer = AsyncRedisSaver(
            redis_url=f"redis://{settings.redis_server}:{settings.redis_port}",
            ttl={"default_ttl": 60 * 2},
        )
        self.graph = None

    def _tools_for_agent(self) -> list:
        """
        Base tools for the agent. load_skill is always present.
        Skill-specific tools are added dynamically as skills are loaded.
        """
        seen: set[str] = set()
        tools = [load_skill]
        seen.add(load_skill.name)
        return tools

    async def build_graph(self):
        await self.checkpointer.asetup()

        model = get_llm()
        base_system = load_md("BASE.md")

        self.graph = create_agent(
            model,
            system_prompt=base_system,
            tools=self._tools_for_agent(),
            middleware=[SkillMiddleware()],
            checkpointer=self.checkpointer,
            # FIX: pass custom state schema so loaded_skills has its reducer.
            # Without this, create_agent uses its default MessagesState which
            # has no loaded_skills field at all — reads return [] every turn.
            state_schema=AgentState,
        )
        self.graph.get_graph().print_ascii()

        with open("graph.png", "wb") as f:
            f.write(self.graph.get_graph().draw_mermaid_png())

        logger.info("Graph built with SkillMiddleware")


graph_instance = Graph()