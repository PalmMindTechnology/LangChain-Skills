import json

from langchain_core.messages import SystemMessage, trim_messages, BaseMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from langgraph.prebuilt import ToolNode
from typing_extensions import Literal

from src.schemas.agent import AgentState
from src.skills.middleware import SkillMiddleware
from src.skills.registry import SKILL_MAP
from src.tools.loader import LOADED_SKILLS_KEY, load_skill
from src.utils.helper import load_md
from src.core.llm import get_llm
from src.config import settings
from src.utils.logging import logger


MAX_HISTORY_MESSAGES = 10


class _Runtime:
    """Thin wrapper so SkillMiddleware can read/write state via runtime.state."""

    def __init__(self, state: AgentState):
        self.state = state


class Graph:
    def __init__(self):
        self.llm = get_llm()
        self._middleware = SkillMiddleware()

        self.checkpointer = AsyncRedisSaver(
            redis_url=f"redis://{settings.redis_server}:{settings.redis_port}",
            ttl={"default_ttl": 60 * 2},
        )

        self.graph = None

    # --------------
    # Tool helpers
    # --------------
    def _tools_for_state(self, loaded_skills: list[str]):
        """
        Returns load_skill + every tool from currently-loaded skills
        with no duplication.
        """
        seen: set[str] = set()
        tools = [load_skill]
        seen.add(load_skill.name)

        for name in loaded_skills:
            skill = SKILL_MAP.get(name)
            if skill:
                for t in skill.tools:
                    if t.name not in seen:
                        tools.append(t)
                        seen.add(t.name)

        return tools

    # ------------------
    # Message truncation
    # ------------------
    def _truncate_messages(self, messages: list[BaseMessage]) -> list[BaseMessage]:
        """
        Trim the conversation history sent to OpenAI to MAX_HISTORY_MESSAGES.
        """
        trimmed = trim_messages(
            messages,
            strategy="last",
            max_tokens=4000,
            include_system=False,
            token_counter="approximate",
            start_on="human",
        )
        logger.info(
            "Message truncation | before={} after={}",
            len(messages),
            len(trimmed),
        )
        return trimmed

    # -------------------------
    # Agent node
    # -------------------------
    async def agent_node(self, state: AgentState, config: RunnableConfig) -> dict:
        loaded = state.get("loaded_skills", [])
        tools = self._tools_for_state(loaded)

        logger.info(
            "Agent node | loaded_skills={} | active_tools={}",
            loaded,
            [t.name for t in tools],
        )

        bound_model = self.llm.bind_tools(tools)
        runtime = _Runtime(state)
        base_system = load_md("BASE.md")

        # Truncate before sending to OpenAI
        history = self._truncate_messages(state["messages"])

        class _Request:
            def __init__(self):
                # Instance attribute — never a class-level default.
                # This ensures override() mutates only this request object,
                # not every future _Request instantiation.
                self.system_message = SystemMessage(content=base_system)

            def override(self, *, system_message: SystemMessage) -> "_Request":
                """
                Called by SkillMiddleware.wrap_model_call to swap in the
                enriched system prompt (skills menu + active skill instructions).
                Returns self so the result passes straight into _handler.
                """
                self.system_message = system_message
                return self

        class _Response:
            def __init__(self, msg):
                self._msg = msg

        def _handler(r: _Request) -> _Response:
            logger.debug("System prompt being sent to OpenAI:\n{}", r.system_message.content)
            response = bound_model.invoke(
                [r.system_message] + history,
                config=config,
            )
            return _Response(response)

        resp = self._middleware.wrap_model_call(_Request(), _handler, runtime=runtime)
        logger.info(
            "Agent response | tool_calls={}",
            [tc["name"] for tc in (resp._msg.tool_calls or [])],
        )

        return {"messages": [resp._msg]}

    # -------------------------
    # Tool node
    # -------------------------
    async def run_tools(self, state: AgentState, config: RunnableConfig) -> dict:
        """
        Executes tool calls. Extracts loaded_skills written by load_skill
        out of the tool result content, then merges with existing state.
        """
        pending = [tc["name"] for tc in state["messages"][-1].tool_calls or []]
        logger.info("Running tools | calls={}", pending)

        node = ToolNode(self._tools_for_state(state.get("loaded_skills", [])))
        result = node.invoke(state)

        current_loaded: list[str] = list(state.get("loaded_skills", []))

        for msg in result.get("messages", []):
            content = getattr(msg, "content", None)
            logger.info(
                "Tool result raw | tool={} content={}",
                getattr(msg, "name", "?"),
                content,
            )
            if not content:
                continue
            try:
                payload = json.loads(content)
                newly_loaded = payload.get(LOADED_SKILLS_KEY)
                if isinstance(newly_loaded, list):
                    for name in newly_loaded:
                        if name not in current_loaded:
                            current_loaded.append(name)
                            logger.info("Skill loaded | name={}", name)
            except (json.JSONDecodeError, AttributeError):
                pass

        logger.info("Tools done | loaded_skills={}", current_loaded)
        return {
            "messages": result["messages"],
            "loaded_skills": current_loaded,
        }

    # ----------
    # Routing
    # -----------
    def should_continue(self, state: AgentState) -> Literal["tools", "__end__"]:
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"
        return END

    # --------------
    # Build graph
    # --------------
    async def build_graph(self):
        await self.checkpointer.asetup()

        builder = StateGraph(AgentState)

        builder.add_node("agent", self.agent_node)
        builder.add_node("tools", self.run_tools)

        builder.set_entry_point("agent")
        builder.add_conditional_edges(
            "agent",
            self.should_continue,
            {"tools": "tools", END: END},
        )
        builder.add_edge("tools", "agent")

        self.graph = builder.compile(checkpointer=self.checkpointer)
        self.graph.get_graph().print_ascii()

        with open("graph.png", "wb") as f:
            f.write(self.graph.get_graph().draw_mermaid_png())


graph_instance = Graph()