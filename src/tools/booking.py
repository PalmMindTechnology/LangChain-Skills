from datetime import datetime, timedelta
from pydantic import BaseModel, field_validator

from langchain.tools import tool
from src.utils.logging import logger
from src.utils.csv import read_all, next_id, write_all


# == Schema ==
class AppointmentSchema(BaseModel):
    username: str
    date_time: datetime

    @field_validator("date_time", mode="before")
    @classmethod
    def validate_datetime(cls, v):
        if isinstance(v, str):
            logger.debug(f"Parsing datetime input: {v}")
            return datetime.fromisoformat(v)
        return v


# == Tools ==
@tool
def book_appointment(data: AppointmentSchema) -> str:
    """Book a new appointment."""
    logger.info(f"Booking request received | user={data.username} | date_time={data.date_time}")

    rows = read_all()

    for row in rows:
        if row["status"] == "active" and row["date_time"] == data.date_time:
            logger.warning(f"Booking conflict | user={data.username} | slot={data.date_time}")
            return f"Slot conflict: {data.date_time.isoformat()} is already booked."

    new_id = next_id(rows)
    now = datetime.now()

    rows.append({
        "id": str(new_id),
        "username": data.username,
        "date_time": data.date_time,
        "status": "active",
        "created_at": now,
    })

    write_all(rows)

    logger.success(f"Appointment booked | id={new_id} | user={data.username} | slot={data.date_time}")

    return (
        f"Booked appointment #{new_id} "
        f"for {data.username} on {data.date_time.strftime('%Y-%m-%d %H:%M')}"
    )


@tool
def cancel_appointment(data: AppointmentSchema) -> str:
    """Cancel an existing appointment by username and datetime."""
    logger.info(
        f"Cancel request | user={data.username} | date_time={data.date_time}"
    )

    rows = read_all()
    found = False

    for row in rows:
        if (
            row["username"] == data.username
            and row["date_time"] == data.date_time
            and row["status"] == "active"
        ):
            row["status"] = "cancelled"
            found = True
            break

    if not found:
        logger.warning(
            f"Cancellation failed | no appointment found | user={data.username}"
        )
        return (
            f"No active appointment found for "
            f"{data.username} at {data.date_time.isoformat()}"
        )

    write_all(rows)

    logger.success(
        f"Appointment cancelled | user={data.username} | slot={data.date_time}"
    )

    return (
        f"Cancelled appointment for {data.username} "
        f"on {data.date_time.strftime('%Y-%m-%d %H:%M')}"
    )


@tool
def reschedule_appointment(data: AppointmentSchema) -> str:
    """Reschedule an appointment by moving it 2 days later."""
    logger.info(f"Reschedule request | user={data.username} | current={data.date_time}")

    rows = read_all()
    target = None

    for row in rows:
        if (
            row["username"] == data.username
            and row["date_time"] == data.date_time
            and row["status"] == "active"
        ):
            target = row
            break

    if not target:
        logger.warning(f"Reschedule failed | appointment not found | user={data.username}")
        return (
            f"No active appointment found for "
            f"{data.username} at {data.date_time.isoformat()}"
        )

    new_time = data.date_time + timedelta(days=2)

    for row in rows:
        if (
            row["status"] == "active"
            and row["date_time"] == new_time
            and row["id"] != target["id"]
        ):
            logger.warning(f"Reschedule conflict | user={data.username} | new_slot={new_time}")
            return f"Cannot reschedule: {new_time.isoformat()} is already booked."

    target["date_time"] = new_time
    write_all(rows)

    logger.success(
        f"Appointment rescheduled | id={target['id']} | "
        f"old={data.date_time} | new={new_time}"
    )

    return (
        f"Rescheduled appointment #{target['id']} "
        f"for {data.username} to {new_time.strftime('%Y-%m-%d %H:%M')} "
        f"(was {data.date_time.strftime('%Y-%m-%d %H:%M')})"
    )


@tool
def check_available_slots() -> str:
    """Check available slots for today."""
    logger.info("Checking available slots")

    now = datetime.now()

    if now.minute >= 30:
        start = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    else:
        start = now.replace(minute=30, second=0, microsecond=0)

    slots = [start + timedelta(minutes=30 * i) for i in range(10)]

    rows = read_all()

    booked = {
        r["date_time"]
        for r in rows
        if r["status"] == "active"
    }

    available = [s for s in slots if s not in booked]

    logger.info(f"Slots checked | total={len(slots)} | available={len(available)}")

    if not available:
        return "No slots available."

    return "Available slots: " + ", ".join(
        s.strftime("%-I:%M %p") for s in available
    )


BOOKING_TOOLS = [
    book_appointment,
    cancel_appointment,
    reschedule_appointment,
    check_available_slots,
]