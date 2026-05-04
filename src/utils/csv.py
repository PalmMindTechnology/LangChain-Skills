import csv
import os

from datetime import datetime
from typing import List, Dict


CSV_FILE = "appointments.csv"

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "username", "date_time", "status", "created_at"])


# == CSV Helpers ==
def read_all() -> List[Dict]:
    rows = []
    with open(CSV_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["date_time"] = datetime.fromisoformat(row["date_time"])
            row["created_at"] = datetime.fromisoformat(row["created_at"])
            rows.append(row)
    return rows

def write_all(rows: List[Dict]):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", 
            "username", 
            "date_time", 
            "status", 
            "created_at"]
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "id": row["id"],
                "username": row["username"],
                "date_time": row["date_time"].isoformat(),
                "status": row["status"],
                "created_at": row["created_at"].isoformat(),
            })

def next_id(rows: List[Dict]) -> int:
    if not rows:
        return 1
    return max(int(r["id"]) for r in rows) + 1