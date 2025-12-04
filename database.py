
from __future__ import annotations
import os
import threading
from typing import Dict, Any, Optional, List
import pandas as pd

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.csv")
MOVIES_FILE = os.path.join(DATA_DIR, "movies.csv")

_lock = threading.Lock()

_USERS_COLUMNS = ["id", "username", "password_hash"]
_MOVIES_COLUMNS = ["id", "title", "year", "director", "description", "added_by"]

def _ensure_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(columns=_USERS_COLUMNS).to_csv(USERS_FILE, index=False)
    if not os.path.exists(MOVIES_FILE):
        pd.DataFrame(columns=_MOVIES_COLUMNS).to_csv(MOVIES_FILE, index=False)

_ensure_files()

def _read_csv(path: str, cols: List[str]) -> pd.DataFrame:
    if not os.path.exists(path):
        return pd.DataFrame(columns=cols)
    df = pd.read_csv(path)
    for c in cols:
        if c not in df.columns:
            df[c] = pd.NA
    return df[cols]

def _write_csv(df: pd.DataFrame, path: str):
    with _lock:
        tmp = path + ".tmp"
        df.to_csv(tmp, index=False)
        os.replace(tmp, path)

def _next_id(df: pd.DataFrame) -> int:
    if df.empty:
        return 1
    try:
        mx = int(pd.to_numeric(df["id"], errors="coerce").max(skipna=True))
    except Exception:
        mx = 0
    return (mx or 0) + 1

def get_all_users() -> pd.DataFrame:
    return _read_csv(USERS_FILE, _USERS_COLUMNS)

def save_users(df: pd.DataFrame):
    df = df.copy()
    for c in _USERS_COLUMNS:
        if c not in df.columns:
            df[c] = pd.NA
    df = df[_USERS_COLUMNS]
    _write_csv(df, USERS_FILE)

def create_user(username: str, password_hash: str) -> Dict[str, Any]:
    df = get_all_users()
    new_id = _next_id(df)
    new = {"id": new_id, "username": username, "password_hash": password_hash}
    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
    save_users(df)
    return new

def find_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    df = get_all_users()
    row = df[df["username"] == username]
    if row.empty:
        return None
    r = row.iloc[0].to_dict()
    try:
        r["id"] = int(r["id"])
    except Exception:
        pass
    return r

def find_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    df = get_all_users()
    row = df[df["id"] == user_id]
    if row.empty:
        return None
    r = row.iloc[0].to_dict()
    try:
        r["id"] = int(r["id"])
    except Exception:
        pass
    return r

def update_user(user_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    df = get_all_users()
    idx = df[df["id"] == user_id].index
    if len(idx) == 0:
        return None
    i = idx[0]
    for k in ("username", "password_hash"):
        if k in updates:
            df.at[i, k] = updates[k]
    save_users(df)
    return find_user_by_id(user_id)

def delete_user(user_id: int) -> bool:
    df = get_all_users()
    if user_id not in df["id"].values:
        return False
    df = df[df["id"] != user_id].copy()
    save_users(df)
    return True

def get_all_movies() -> pd.DataFrame:
    return _read_csv(MOVIES_FILE, _MOVIES_COLUMNS)

def save_movies(df: pd.DataFrame):
    df = df.copy()
    for c in _MOVIES_COLUMNS:
        if c not in df.columns:
            df[c] = pd.NA
    df = df[_MOVIES_COLUMNS]
    _write_csv(df, MOVIES_FILE)

def create_movie(movie: Dict[str, Any]) -> Dict[str, Any]:
    df = get_all_movies()
    new_id = _next_id(df)
    new = {
        "id": new_id,
        "title": movie.get("title", ""),
        "year": movie.get("year") if movie.get("year") not in (None, "") else pd.NA,
        "director": movie.get("director", ""),
        "description": movie.get("description", ""),
        "added_by": movie.get("added_by", "")
    }
    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
    save_movies(df)
    new["id"] = int(new["id"])
    return new

def find_movie_by_id(movie_id: int) -> Optional[Dict[str, Any]]:
    df = get_all_movies()
    row = df[df["id"] == movie_id]
    if row.empty:
        return None
    r = row.iloc[0].to_dict()
    if pd.notna(r.get("year")):
        try:
            r["year"] = int(r["year"])
        except Exception:
            pass
    try:
        r["id"] = int(r["id"])
    except Exception:
        pass
    return r

def update_movie(movie_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    df = get_all_movies()
    idx = df[df["id"] == movie_id].index
    if len(idx) == 0:
        return None
    i = idx[0]
    for k in ("title", "year", "director", "description", "added_by"):
        if k in updates:
            df.at[i, k] = updates[k]
    save_movies(df)
    return find_movie_by_id(movie_id)

def delete_movie(movie_id: int) -> bool:
    df = get_all_movies()
    if movie_id not in df["id"].values:
        return False
    df = df[df["id"] != movie_id].copy()
    save_movies(df)
    return True

def search_movies(q: str) -> List[Dict[str, Any]]:
    df = get_all_movies()
    if df.empty:
        return []
    q_low = q.lower()
    mask = (
        df["title"].astype(str).str.lower().str.contains(q_low, na=False) |
        df["director"].astype(str).str.lower().str.contains(q_low, na=False) |
        df["description"].astype(str).str.lower().str.contains(q_low, na=False)
    )
    rows = df[mask]
    return [row.dropna().to_dict() for _, row in rows.iterrows()]

def reset_data(remove_files: bool = False):
    if remove_files:
        for f in (USERS_FILE, MOVIES_FILE):
            try:
                os.remove(f)
            except FileNotFoundError:
                pass
    _ensure_files()

if __name__ == "__main__":
    users = get_all_users()
    movies = get_all_movies()
    print("Users:", len(users), "Movies:", len(movies))
