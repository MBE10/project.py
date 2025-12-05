from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import auth

app = FastAPI()

# Static files (CSS / Images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------------------
# Helper: Navbar HTML
# ---------------------------
def dashboard_navbar(username: str):
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
          <div style="color:var(--accent-contrast); font-weight:600;">{username}</div>
          <a class="btn-ghost" href="/logout">Logout</a>
        </div>
    </header>
    """

# ---------------------------
# HOME REDIRECT
# ---------------------------
@app.get("/")
async def home(request: Request):
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
    <html>
      <body style="font-family: Arial; background:#f0f2f5; display:flex; justify-content:center; align-items:center; height:100vh;">
        <form method="post" style="background:white; padding:40px; border-radius:15px; width:350px; box-shadow:0 8px 20px rgba(0,0,0,0.1);">
          <h2 style="text-align:center; margin-bottom:20px;">Login</h2>
          <input name="username" placeholder="Username" required style="width:100%; padding:12px; margin-bottom:15px; border-radius:8px; border:1px solid #ccc;">
          <input name="password" type="password" placeholder="Password" required style="width:100%; padding:12px; margin-bottom:20px; border-radius:8px; border:1px solid #ccc;">
          <button type="submit" style="width:100%; padding:12px; border:none; background:#001933; color:white; border-radius:10px; font-weight:600;">Login</button>
          <p style="text-align:center; margin-top:15px;">Don't have an account? <a href="/register">Register</a></p>
        </form>
      </body>
    </html>
    """

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
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
    <html>
      <body style="font-family: Arial; background:#f0f2f5; display:flex; justify-content:center; align-items:center; height:100vh;">
        <form method="post" style="background:white; padding:40px; border-radius:15px; width:350px; box-shadow:0 8px 20px rgba(0,0,0,0.1);">
          <h2 style="text-align:center; margin-bottom:20px;">Register</h2>
          <input name="username" placeholder="Choose username" required style="width:100%; padding:12px; margin-bottom:15px; border-radius:8px; border:1px solid #ccc;">
          <input name="password" type="password" placeholder="Choose password" required style="width:100%; padding:12px; margin-bottom:20px; border-radius:8px; border:1px solid #ccc;">
          <button type="submit" style="width:100%; padding:12px; border:none; background:#001933; color:white; border-radius:10px; font-weight:600;">Register</button>
          <p style="text-align:center; margin-top:15px;">Already have an account? <a href="/login">Login</a></p>
        </form>
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
# DASHBOARD / HOME PAGE
# ---------------------------
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    session_id = request.cookies.get("session_id")
    username = auth.get_user_by_session(session_id)
    if not username:
        return RedirectResponse("/login")

    return f"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width,initial-scale=1" />
      <title>Cineverse — Dashboard</title>
      <style>
        :root {{
          --accent: #001933;
          --accent-contrast: #ffffff;
          --page-bg: #f7f7f9;
          --card-bg: #ffffff;
        }}
        body {{ margin:0; font-family: Arial, Helvetica, sans-serif; background: var(--page-bg); color:#222; }}
        .navbar {{
          display:flex;
          justify-content:space-between;
          align-items:center;
          padding:12px 18px;
          background:var(--accent);
          color:var(--accent-contrast);
          gap:12px;
        }}
        .nav-left {{ display:flex; gap:16px; align-items:center; }}
        .logo {{ font-weight:700; font-size:18px; color:var(--accent-contrast); text-decoration:none; }}
        .nav-links a {{
          color:var(--accent-contrast);
          text-decoration:none;
          margin-left:10px;
          font-weight:500;
        }}
        .nav-links a:hover {{ opacity:0.85; }}
        .nav-right {{ display:flex; gap:12px; align-items:center; }}
        .btn-ghost {{
          background:transparent; border:1px solid rgba(255,255,255,0.18); color:var(--accent-contrast);
          padding:8px 10px; border-radius:8px; text-decoration:none; font-weight:600;
        }}
        .container {{ padding:20px; max-width:1100px; margin:18px auto; }}
        .welcome-card {{
          background: var(--card-bg);
          padding:18px;
          border-radius:12px;
          box-shadow: 0 6px 20px rgba(2,6,23,0.06);
        }}
        @media (max-width:600px) {{
          .nav-links {{ display:none; }}
        }}
      </style>
    </head>
    <body>
      {dashboard_navbar(username)}
      <main class="container">
        <section class="welcome-card">
          <h2>Welcome, {username} 👋</h2>
          <p>Use the navigation above to manage movies — add new ones, scrape details, or search the collection.</p>
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
