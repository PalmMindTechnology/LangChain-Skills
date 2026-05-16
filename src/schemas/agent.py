from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


def _merge_unique_skills(existing: list[str], new: list[str]) -> list[str]:
    """
    Reducer for loaded_skills.
    Merges incoming skill names into the existing list, preserving order
    and deduplicating — so LangGraph never overwrites the list when two
    nodes write state in the same step.
    """
    seen = set(existing)
    return existing + [s for s in new if s not in seen]


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    # FIX: reducer ensures updates merge instead of last-write-wins overwrite.
    # Without this, any node that returns state without loaded_skills resets it to [].
    loaded_skills: Annotated[list[str], _merge_unique_skills]  # Tools are extended per turn according to skill access

    llm_calls: int