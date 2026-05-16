from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from langchain.messages import (
    AIMessage,
    HumanMessage, 
    ToolMessage
)
from src.utils.logging import logger



def load_md(file):
    try:
        skill_path = f"src/skills/prompts/{file}"
        content = Path(skill_path).read_text()
        if file.lower().startswith(("base", "booking")):
            now = datetime.now(ZoneInfo("Asia/Kathmandu"))
            content = (
            content.replace("{{current_date}}", now.strftime("%Y-%m-%d"))
                   .replace("{{current_time}}", now.strftime("%H:%M:%S"))
                   .replace("{{timezone}}", str(now.tzinfo))
        )
        logger.info(f"Loaded skill file: {file}")
        return content

    except FileNotFoundError:
        raise FileNotFoundError(f"Skill file not found: {file}")
    except Exception as e:
        raise Exception(f"Error loading skill file: {file}") from e
    


# ===========================
# Middleware Helpers
# ===========================

def build_skills_prompt(skills: list) -> str:
    """
    Return a markdown formatted of available skills if available else return empty string.
    """
    if not skills:
        logger.warning("No skills found")
        return ""
    
    lines: list[str] = []
    for skill in skills:
        try:
            lines.append(f"- **{skill.name}**: {skill.description}")
        except AttributeError:
            logger.warning("Skipping malformed skill entry: {}", skill)

    return "\n".join(lines)


def truncate_messages(
    messages: list,
    convo_turns: int = 5,
) -> list:
    """
    Return the last *max_turns* conversation turns in chronological order.
    This included HumanMessage, AIMessage and tools calls
    """
    turns: list[list] = []
    current_turn: list = []
 
    for msg in reversed(messages):
        current_turn.append(msg)
        if isinstance(msg, HumanMessage):
            turns.append(current_turn)
            current_turn = []
            if len(turns) >= convo_turns:
                break
 
    # Restore chronological order: 
    # Reverse the turns list and each turn's messages.
    result: list = []
    for turn in reversed(turns):
        result.extend(reversed(turn))
 
    return result


def build_tool_call_index(messages: list) -> dict[str, str]:
    """
    Return a dict of tool_call_id -> tool_name for all tool calls in AIMessages.
    """
    index: dict[str, str] = {}
    for msg in messages:
        if isinstance(msg, AIMessage):
            for tc in msg.tool_calls or []:
                tc_id = tc.get("id")
                tc_name = tc.get("name")
                if tc_id and tc_name:
                    index[tc_id] = tc_name
    return index


def extract_msg_since_last_ai_response(messages: list) -> list:
    """
    Return meesages from the most recent non-tool-call AIMessage onward
    """
    tail: list = []
    for msg in reversed(messages):
        tail.append
        if isinstance(msg, AIMessage) and not getattr(msg, "tool_calls", None):
            break
    tail.reverse()
    return tail

                

    

