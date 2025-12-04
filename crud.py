from typing import Optional, List
import database
import scraper
import auth
from models import UserCreate, UserLogin, MovieCreate, MovieUpdate, MovieSearch


def register_user_crud(user: UserCreate) -> Optional[dict]:
    return auth.register_user(user.username, user.password)


def login_user_crud(user: UserLogin) -> Optional[dict]:
    return auth.login_user(user.username, user.password)



def create_movie_crud(movie: MovieCreate) -> dict:
    movie_data = {
        "title": movie.title,
        "year": movie.year,
        "director": movie.director,
        "description": movie.description,
        "added_by": movie.added_by
    }
    return database.create_movie(movie_data)


def update_movie_crud(movie_id: int, updates: MovieUpdate) -> Optional[dict]:
    update_dict = updates.dict(exclude_unset=True)
    return database.update_movie(movie_id, update_dict)


def delete_movie_crud(movie_id: int) -> bool:
    return database.delete_movie(movie_id)


def get_all_movies_crud() -> List[dict]:
    movies_df = database.get_all_movies()
    return [row.dropna().to_dict() for _, row in movies_df.iterrows()]


def find_movie_by_id_crud(movie_id: int) -> Optional[dict]:
    return database.find_movie_by_id(movie_id)


def search_movies_crud(search: MovieSearch) -> List[dict]:
    return database.search_movies(search.query)



def scrape_movie_crud(title: str, added_by: str = "scraper") -> Optional[dict]:
    return scraper.scrape_movie(title, added_by)


def scrape_many_movies_crud(titles: list, added_by: str = "scraper") -> list:
    return scraper.scrape_many(titles, added_by)
