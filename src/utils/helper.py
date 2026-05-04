from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from src.utils.logging import logger

def load_md(file):
    try:
        skill_path = f"src/skills/prompts/{file}"
        content = Path(skill_path).read_text()
        if file.lower().startswith("base"):
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
    
