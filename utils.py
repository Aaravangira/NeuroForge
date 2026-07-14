import json
import uuid
from pathlib import Path
from datetime import datetime

# ==========================================
# GENERATE UNIQUE FILE NAME
# ==========================================

def generate_filename(filename: str) -> str:
    extension = Path(filename).suffix
    unique_name = f"{uuid.uuid4().hex}{extension}"
    return unique_name


# ==========================================
# GET FILE EXTENSION
# ==========================================

def get_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


# ==========================================
# CURRENT DATE TIME
# ==========================================

def current_datetime():
    return datetime.now()


# ==========================================
# SAVE JSON
# ==========================================

def save_json(data, filepath):
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


# ==========================================
# LOAD JSON
# ==========================================

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)