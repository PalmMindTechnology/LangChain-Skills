from src.schemas.skill import SkillRegistry
from src.utils.helper import load_md
from src.utils.logging import logger

from src.tools.booking import BOOKING_TOOLS
from src.tools.rag import RAG_TOOLS
from src.tools.retention import RETENTION_TOOLS
from src.tools.frustration import FRUSTRATION_TOOLS



SKILLS: list[SkillRegistry] = [
    SkillRegistry(
        name="appointment_booking",
        description="Use when the user wants to book, schedule, reschedule, cancel, or check availability for an appointment. Also trigger when the user is trying to confirm timing, slots, or manage existing bookings.",
        content=load_md("BOOKING.md"),
        tools=BOOKING_TOOLS,
    ),

    SkillRegistry(
        name="rag_support",
        description="Use when the user asks factual questions that require retrieving information from internal knowledge sources, documents, FAQs, or structured content. Ideal for product/service explanations, policies, procedures, or any 'what is / how does / explain' type queries grounded in stored knowledge.",
        content=load_md("RAG.md"),
        tools=RAG_TOOLS,
    ),

    SkillRegistry(
        name="retention",
        description="Use when the user shows signs of churn risk, wants to leave, cancels, expresses intent to stop using the service, or is inactive/low engagement. Also trigger for win-back conversations, discounts, incentives, or re-engagement flows.",
        content=load_md("RETENTION.md"),
        tools=RETENTION_TOOLS,
    ),

    SkillRegistry(
        name="frustration",
        description="Use when the user expresses anger, dissatisfaction, confusion, complaints, or emotional distress related to the service. Trigger when tone indicates frustration, escalation risk, or support dissatisfaction, requiring empathetic handling and de-escalation.",
        content=load_md("FRUSTRATION.md"),
        tools=FRUSTRATION_TOOLS,
    ),
]

# Skill dict map instance
SKILL_MAP: dict[str, SkillRegistry] = {s.name: s for s in SKILLS}
logger.info("Skill map loaded | count={}", len(SKILL_MAP))