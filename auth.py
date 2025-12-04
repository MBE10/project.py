import hashlib
import hmac
import os
from typing import Optional
import database 


SECRET_KEY = os.environ.get("CINEVERSE_SECRET", "supersecretkey")



def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash



def register_user(username: str, password: str) -> Optional[dict]:
    if database.find_user_by_username(username):
        return None  # user exists
    hashed = hash_password(password)
    return database.create_user(username, hashed)


def login_user(username: str, password: str) -> Optional[dict]:
    user = database.find_user_by_username(username)
    if not user:
        return None
    if verify_password(password, user["password_hash"]):
        return user
    return None



def create_session(user_id: int) -> str:
    msg = str(user_id).encode()
    signature = hmac.new(SECRET_KEY.encode(), msg, hashlib.sha256).hexdigest()
    return f"{user_id}|{signature}"


def verify_session(cookie: str) -> Optional[int]:
    if not cookie:
        return None
    parts = cookie.split("|")
    if len(parts) != 2:
        return None
    user_id_str, signature = parts
    expected = hmac.new(SECRET_KEY.encode(), user_id_str.encode(), hashlib.sha256).hexdigest()
    if hmac.compare_digest(signature, expected):
        try:
            return int(user_id_str)
        except:
            return None
    return None
