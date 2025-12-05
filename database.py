# database.py
import os
import json
from typing import Optional, Dict

USERS_FILE = "users.json"

def _ensure_file():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": []}, f, indent=2)

_ensure_file()

def _read() -> Dict:
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _write(data: Dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def add_user(username: str, password_hash: str) -> bool:
    """
    Add user with hashed password.
    Returns True if created, False if username exists.
    """
    data = _read()
    for u in data.get("users", []):
        if u.get("username") == username:
            return False
    data["users"].append({"username": username, "password": password_hash})
    _write(data)
    return True

def get_user(username: str) -> Optional[Dict]:
    data = _read()
    for u in data.get("users", []):
        if u.get("username") == username:
            return u
    return None

def list_users():
    data = _read()
    return [u.get("username") for u in data.get("users", [])]
