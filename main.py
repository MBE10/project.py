from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import auth
import database

app = FastAPI()

# Serve static files (CSS, JS, Images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------------------
# HOME REDIRECT
# ---------------------------
@app.get("/")
async def home_redirect(request: Request):
    session_id = request.cookies.get("session_id")
    username = auth.get_user_by_session(session_id)
    if username:
        return RedirectResponse("/dashboard")
    return RedirectResponse("/login")

# ---------------------------
# LOGIN PAGE
# ---------------------------
@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - Cineverse</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <div class="login-container">
            <form action="/login" method="post" class="login-form">
                <h1>Cineverse</h1>
                <h3>Welcome Back!</h3>
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
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

# ---------------------------
# REGISTER PAGE
# ---------------------------
@app.get("/register", response_class=HTMLResponse)
async def register_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register - Cineverse</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <div class="login-container">
            <form action="/register" method="post" class="login-form">
                <h1>Cineverse</h1>
                <h3>Create Account</h3>
                <input type="text" name="username" placeholder="Choose username" required>
                <input type="password" name="password" placeholder="Choose password" required>
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

# ---------------------------
# DASHBOARD
# ---------------------------
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    session_id = request.cookies.get("session_id")
    username = auth.get_user_by_session(session_id)
    if not username:
        return RedirectResponse("/login")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cineverse - Dashboard</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <header class="navbar">
            <div class="nav-left"><a class="logo" href="/dashboard">Cineverse</a></div>
            <div class="nav-center">
                <a href="/dashboard">Home</a>
                <a href="/movies">Movies</a>
                <a href="/movies/add">Add Movie</a>
                <a href="/movies/scrape">Scrape</a>
                <a href="/authors">Authors</a>
            </div>
            <div class="nav-right">
                <div class="username">{username}</div>
                <a href="/logout" class="logout-btn">Logout</a>
            </div>
        </header>

        <main class="container">
            <section class="welcome-card">
                <h2>Welcome, {username} </h2>
                <p>Use the navigation above to manage movies — add, scrape, or search.</p>
            </section>
        </main>
    </body>
    </html>
    """

# ---------------------------
# LOGOUT
# ---------------------------
@app.get("/logout")
async def logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id:
        auth.destroy_session(session_id)
    response = RedirectResponse("/login")
    response.delete_cookie("session_id")
    return response

