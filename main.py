# main.py
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import auth
import database

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------- Helpers ----------
def render_navbar(username: str):
    return f"""
    <header class="navbar">
        <div class="nav-left">
            <a class="logo" href="/dashboard">🎬 Cineverse</a>
            <nav class="nav-links">
                <a href="/dashboard">Home</a>
                <a href="/movies">Movies</a>
                <a href="/movies/add">Add Movie</a>
                <a href="/movies/scrape">Scrape</a>
                <a href="/authors">Authors</a>
            </nav>
        </div>
        <div class="nav-right">
            <div style="color:white; font-weight:600;">{username}</div>
            <a class="btn-ghost" href="/logout">Logout</a>
        </div>
    </header>
    """

def render_page(username: str, content: str, title="Cineverse"):
    return f"""
    <html>
    <head>
        <link rel="stylesheet" href="/static/css/style.css">
        <title>{title} - Cineverse</title>
    </head>
    <body>
        {render_navbar(username)}
        <main class="container">{content}</main>
    </body>
    </html>
    """

# ---------- Routes ----------
@app.get("/")
async def home(request: Request):
    session_id = request.cookies.get("session_id")
    username = auth.get_user_by_session(session_id)
    if username:
        return RedirectResponse("/dashboard")
    return RedirectResponse("/login")

# Login
@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return f"""
    <html>
        <head><link rel="stylesheet" href="/static/css/style.css"></head>
        <body>
            <div class="login-container">
                <form method="post" class="login-box">
                    <img src="/static/logo.png" alt="Logo">
                    <h2>Login</h2>
                    <input name="username" placeholder="Username" required>
                    <input name="password" type="password" placeholder="Password" required>
                    <button type="submit">Login</button>
                    <p>Don't have an account? <a href="/register">Register</a></p>
                </form>
            </div>
        </body>
    </html>
    """

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    user = auth.login_user(username, password)
    if not user:
        return HTMLResponse("<h2>Invalid username or password</h2><a href='/login'>Back</a>")
    session_id = auth.create_session(username)
    response = RedirectResponse("/dashboard", status_code=302)
    response.set_cookie("session_id", session_id)
    return response

# Register
@app.get("/register", response_class=HTMLResponse)
async def register_page():
    return f"""
    <html>
        <head><link rel="stylesheet" href="/static/css/style.css"></head>
        <body>
            <div class="login-container">
                <form method="post" class="login-box">
                    <img src="/static/logo.png" alt="Logo">
                    <h2>Register</h2>
                    <input name="username" placeholder="Choose username" required>
                    <input name="password" type="password" placeholder="Choose password" required>
                    <button type="submit">Register</button>
                    <p>Already have an account? <a href="/login">Login</a></p>
                </form>
            </div>
        </body>
    </html>
    """

@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    created = auth.register_user(username, password)
    if not created:
        return HTMLResponse("<h2>Username already exists</h2><a href='/register'>Back</a>")
    return RedirectResponse("/login", status_code=302)

# Dashboard
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    session_id = request.cookies.get("session_id")
    username = auth.get_user_by_session(session_id)
    if not username:
        return RedirectResponse("/login")
    content = f"""
    <section class="welcome-card">
        <h2>Welcome, {username} 👋</h2>
        <p>Manage movies, authors, and more using the navigation above.</p>
    </section>
    <section style="display:flex;gap:14px;flex-wrap:wrap; margin-top:18px;">
        <div class="welcome-card" style="flex:1 1 300px;"><h3>Movies</h3><p>Click <a href='/movies'>Movies</a> to see the list.</p></div>
        <div class="welcome-card" style="flex:1 1 300px;"><h3>Add Movie</h3><p>Go to <a href='/movies/add'>Add Movie</a> to add a movie manually.</p></div>
        <div class="welcome-card" style="flex:1 1 300px;"><h3>Scrape Movies</h3><p>Click <a href='/movies/scrape'>Scrape</a> to fetch movies.</p></div>
        <div class="welcome-card" style="flex:1 1 300px;"><h3>Authors</h3><p>Click <a href='/authors'>Authors</a> to manage authors.</p></div>
    </section>
    """
    return render_page(username, content, title="Dashboard")

# Movies list
@app.get("/movies", response_class=HTMLResponse)
async def movies_page(request: Request):
    session_id = request.cookies.get("session_id")
    username = auth.get_user_by_session(session_id)
    if not username:
        return RedirectResponse("/login")
    movies = database.list_movies()
    movie_cards = "".join(
        f"<div class='welcome-card' style='flex:1 1 300px;'><h3>{m['title']}</h3><p>Author: {m['author']}</p></div>"
        for m in movies
    )
    content = f"<section style='display:flex;gap:14px;flex-wrap:wrap;'>{movie_cards}</section>"
    return render_page(username, content, title="Movies")

# Add movie
@app.get("/movies/add", response_class=HTMLResponse)
async def add_movie_page(request: Request):
    session_id = request.cookies.get("session_id")
    username = auth.get_user_by_session(session_id)
    if not username:
        return RedirectResponse("/login")
    content = """
    <section class="welcome-card">
        <h2>Add a New Movie</h2>
        <form method="post">
            <input name="title" placeholder="Movie Title" required>
            <input name="author" placeholder="Author" required>
            <button type="submit">Add Movie</button>
        </form>
    </section>
    """
    return render_page(username, content, title="Add Movie")

@app.post("/movies/add")
async def add_movie(title: str = Form(...), author: str = Form(...), request: Request = None):
    session_id = request.cookies.get("session_id")
    username = auth.get_user_by_session(session_id)
    if not username:
        return RedirectResponse("/login")
    database.add_movie(title, author)
    database.add_author(author)
    return RedirectResponse("/movies", status_code=302)

# Scrape movies
@app.get("/movies/scrape", response_class=HTMLResponse)
async def scrape_movies(request: Request):
    session_id = request.cookies.get("session_id")
    username = auth.get_user_by_session(session_id)
    if not username:
        return RedirectResponse("/login")
    content = """
    <section class="welcome-card">
        <h2>Scrape Movies</h2>
        <p>Scraper placeholder: This feature will fetch movies automatically.</p>
    </section>
    """
    return render_page(username, content, title="Scrape Movies")

# Authors
@app.get("/authors", response_class=HTMLResponse)
async def authors_page(request: Request):
    session_id = request.cookies.get("session_id")
    username = auth.get_user_by_session(session_id)
    if not username:
        return RedirectResponse("/login")
    authors = database.list_authors()
    author_cards = "".join(f"<div class='welcome-card' style='flex:1 1 300px;'><h3>{a}</h3></div>" for a in authors)
    content = f"<section style='display:flex;gap:14px;flex-wrap:wrap;'>{author_cards}</section>"
    return render_page(username, content, title="Authors")

# Logout
@app.get("/logout")
async def logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id:
        auth.destroy_session(session_id)
    response = RedirectResponse("/login")
    response.delete_cookie("session_id")
    return response
