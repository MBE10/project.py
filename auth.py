# auth.py
import hashlib
import uuid
from typing import Optional, Dict
import database

# In-memory session storage: session_id -> username
_sessions: Dict[str, str] = {}

def _hash_password(password: str) -> str:
    # simple sha256 hash (truncate whitespace)
    pw = (password or "").strip()
    h = hashlib.sha256()
    h.update(pw.encode("utf-8"))
    return h.hexdigest()

def register_user(username: str, password: str) -> bool:
    """
    Register user. Returns True if created, False if username exists.
    """
    username = (username or "").strip()
    if not username or not password:
        return False
    pw_hash = _hash_password(password)
    return database.add_user(username, pw_hash)

def login_user(username: str, password: str) -> Optional[Dict]:
    """
    Verify credentials. Returns user dict on success, None on failure.
    """
    username = (username or "").strip()
    user = database.get_user(username)
    if not user:
        return None
    pw_hash = _hash_password(password)
    if pw_hash == user.get("password"):
        return {"username": username}
    return None

def create_session(username: str) -> str:
    """Create session id for username and return it."""
    sid = str(uuid.uuid4())
    _sessions[sid] = username
    return sid

def get_user_by_session(session_id: str) -> Optional[str]:
    return _sessions.get(session_id)

def destroy_session(session_id: str):
    _sessions.pop(session_id, None)
