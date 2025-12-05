# database.py
import os
import json
from typing import Optional, Dict, List

USERS_FILE = "users.json"
MOVIES_FILE = "movies.json"
AUTHORS_FILE = "authors.json"

def _ensure_file(filename, default_data):
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=2)

_ensure_file(USERS_FILE, {"users": []})
_ensure_file(MOVIES_FILE, {"movies": []})
_ensure_file(AUTHORS_FILE, {"authors": []})

def _read(filename) -> Dict:
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def _write(filename, data: Dict):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# Users
def add_user(username: str, password_hash: str) -> bool:
    data = _read(USERS_FILE)
    for u in data.get("users", []):
        if u.get("username") == username:
            return False
    data["users"].append({"username": username, "password": password_hash})
    _write(USERS_FILE, data)
    return True

def get_user(username: str) -> Optional[Dict]:
    data = _read(USERS_FILE)
    for u in data.get("users", []):
        if u.get("username") == username:
            return u
    return None

def list_users() -> List[str]:
    data = _read(USERS_FILE)
    return [u.get("username") for u in data.get("users", [])]

# Movies
def add_movie(title: str, author: str):
    data = _read(MOVIES_FILE)
    data["movies"].append({"title": title, "author": author})
    _write(MOVIES_FILE, data)

def list_movies() -> List[Dict]:
    data = _read(MOVIES_FILE)
    return data.get("movies", [])

# Authors
def add_author(name: str):
    data = _read(AUTHORS_FILE)
    if name not in data["authors"]:
        data["authors"].append(name)
    _write(AUTHORS_FILE, data)

def list_authors() -> List[str]:
    data = _read(AUTHORS_FILE)
    return data.get("authors", [])
