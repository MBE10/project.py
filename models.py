from pydantic import BaseModel
from typing import Optional



class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str



class MovieBase(BaseModel):
    title: str
    year: Optional[int] = None
    director: Optional[str] = ""
    description: Optional[str] = ""


class MovieCreate(MovieBase):
    added_by: str


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    year: Optional[int] = None
    director: Optional[str] = None
    description: Optional[str] = None


class MovieOut(MovieBase):
    id: int
    added_by: str



class MovieSearch(BaseModel):
    query: str
