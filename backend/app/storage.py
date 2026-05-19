import json
import os
from pathlib import Path
from typing import List
from .models import DecisionRecord

STORAGE_FILE = Path("decisions.json")

def save_decision(record: DecisionRecord):
    records = load_all_decisions()
    records.append(record)
    temp_file = STORAGE_FILE.with_suffix(".json.tmp")
    with open(temp_file, "w") as f:
        json.dump([r.dict() for r in records], f, indent=2, default=str)
    os.replace(temp_file, STORAGE_FILE)

def load_all_decisions() -> List[DecisionRecord]:
    if not STORAGE_FILE.exists():
        return []
    try:
        with open(STORAGE_FILE) as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return []
    return [DecisionRecord(**item) for item in data]

def clear_storage():
    if STORAGE_FILE.exists():
        STORAGE_FILE.unlink()
