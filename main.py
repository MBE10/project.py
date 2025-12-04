from fastapi import FastAPI, Request, Form, Depends, Response
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from crud import (
    register_user_crud, login_user_crud, create_movie_crud,
    update_movie_crud, delete_movie_crud, get_all_movies_crud,
    find_movie_by_id_crud, search_movies_crud, scrape_movie_crud
)
from models import UserCreate, UserLogin, MovieCreate, MovieUpdate, MovieSearch
import auth

app = FastAPI()


templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")



def get_current_user(request: Request):
    cookie = request.cookies.get("cineverse_session")
    user_id = auth.verify_session(cookie)
    if user_id:
        return user_id
    return None



@app.get("/")
def home(request: Request):
    user_id = get_current_user(request)
    movies = get_all_movies_crud()
    return templates.TemplateResponse("index.html", {"request": request, "user_id": user_id, "movies": movies})



@app.get("/register")
def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register_post(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...)
):
    user = register_user_crud(UserCreate(username=username, password=password))
    if not user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username exists!"})
    session = auth.create_session(user["id"])
    resp = RedirectResponse("/", status_code=302)
    resp.set_cookie("cineverse_session", session)
    return resp



@app.get("/login")
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login_post(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...)
):
    user = login_user_crud(UserLogin(username=username, password=password))
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid login!"})
    session = auth.create_session(user["id"])
    resp = RedirectResponse("/", status_code=302)
    resp.set_cookie("cineverse_session", session)
    return resp



@app.get("/logout")
def logout(request: Request):
    resp = RedirectResponse("/", status_code=302)
    resp.delete_cookie("cineverse_session")
    return resp



@app.get("/movies/add")
def add_movie_get(request: Request):
    return templates.TemplateResponse("add_movie.html", {"request": request})


@app.post("/movies/add")
def add_movie_post(
    request: Request,
    title: str = Form(...),
    year: int = Form(None),
    director: str = Form(""),
    description: str = Form(""),
    added_by: str = Form("manual")
):
    movie = create_movie_crud(MovieCreate(title=title, year=year, director=director, description=description, added_by=added_by))
    return RedirectResponse("/", status_code=302)



@app.get("/movies/update/{movie_id}")
def update_movie_get(request: Request, movie_id: int):
    movie = find_movie_by_id_crud(movie_id)
    return templates.TemplateResponse("update_movie.html", {"request": request, "movie": movie})


@app.post("/movies/update/{movie_id}")
def update_movie_post(
    request: Request,
    movie_id: int,
    title: str = Form(None),
    year: int = Form(None),
    director: str = Form(None),
    description: str = Form(None)
):
    update_movie_crud(movie_id, MovieUpdate(title=title, year=year, director=director, description=description))
    return RedirectResponse("/", status_code=302)



@app.get("/movies/delete/{movie_id}")
def delete_movie_route(movie_id: int):
    delete_movie_crud(movie_id)
    return RedirectResponse("/", status_code=302)



@app.post("/movies/search")
def search_movies_route(request: Request, query: str = Form(...)):
    results = search_movies_crud(MovieSearch(query=query))
    return templates.TemplateResponse("search_results.html", {"request": request, "movies": results})



@app.get("/movies/scrape")
def scrape_get(request: Request):
    return templates.TemplateResponse("scrape_movie.html", {"request": request})


@app.post("/movies/scrape")
def scrape_post(request: Request, title: str = Form(...)):
    movie = scrape_movie_crud(title)
    return RedirectResponse("/", status_code=302)
