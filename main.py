# & "C:\Program Files\Git\usr\bin\openssl.exe" req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
# ВЕРХНЮЮ СТРОЧКУ В БАШ
# uvicorn main:app --reload --ssl-keyfile=key.pem --ssl-certfile=cert.pem

# python -m venv fastapi_venv
# fastapi_venv\Scripts\activate.ps1

from datetime import datetime

from fastapi import FastAPI, Form, Request, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.routing import Match
import pandas as pd
import hashlib
import shutil
import uuid
import os

SESSION_LIFETIME = 300
white_urls = ["/", "/login", "/logout", "/register"]
AVATAR_DIR = "images"
os.makedirs(AVATAR_DIR, exist_ok=True)
ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

app = FastAPI()

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path

    if path.startswith("/static") or path.startswith("/images") or path.startswith("/avatars"):
        return await call_next(request)

    username = request.session.get("username")
    starttime_str = request.session.get("session_starttime")
    request.state.user = None

    if username and starttime_str:
        starttime = datetime.fromisoformat(starttime_str)
        if (datetime.now() - starttime).total_seconds() > SESSION_LIFETIME:
            request.session.clear() 
        else:
            request.state.user = username
            request.session["session_starttime"] = str(datetime.now())

    # 3. Если страница закрытая (не в white_urls) и юзер не залогинен — кидаем на /login
    # if path not in white_urls and not request.state.user:
    #     return RedirectResponse(url="/login", status_code=303)

    return await call_next(request)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
app.mount("/images", StaticFiles(directory="images"), name="images")
app.mount("/avatars", StaticFiles(directory="avatars"), name="avatars")

@app.get("/", response_class=HTMLResponse)
async def first_page(request: Request):
    if request.state.user:
        return RedirectResponse(url="/home", status_code=303)
    
    return templates.TemplateResponse(request=request, name="first.html")

@app.get('/login', response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/login")
def login(request: Request,
          password: str = Form(...), 
          username: str = Form(...) 
          ):
    df = pd.read_csv('users.csv')
    users_new = df.to_dict(orient="records")
    print(users_new)
    res = 'neverno'
    for i in users_new:
        if username == i['username'] and hash_password(password + username) == i['password'] :
            res = 'успешно'
            id = i['user_unique_id']
            break

    if res == 'успешно':
        request.session["username"] = username
        request.session['session_starttime'] = str(datetime.now())
        request.session['user_unique_id'] = id
        response = RedirectResponse(url=f"/home", status_code=303)
        return response
    else:
        return templates.TemplateResponse(request=request,
                                          name="login.html",
                                          context={"error": "Неверный пароль или логин"},
                                        )

@app.get('/register', response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name='register.html')

@app.post('/register')
def register(request: Request,
             age: float = Form(...),
             password: str = Form(...), 
             username: str = Form(...),
             avatar: UploadFile  = File(None)):
    res = ''
    df = pd.read_csv('users.csv')
    users_new = df.to_dict(orient="records")
    print(users_new)
    for i in users_new:
        if username == i['username']:
            res = 'ужес exist'
            break
    if res:
        return templates.TemplateResponse(name="register.html",
                                        request=request, 
                                        context={"error": res})
    if avatar.filename:
        if avatar.content_type not in ALLOWED_TYPES:
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "error": "Неверный формат картинки. Разрешены JPG, PNG и WEBP."}
            )
        else:
            ext = os.path.splitext(avatar.filename)[1]
            new_filename = f'{uuid.uuid4()}{ext}'
            file_path = os.path.join(AVATAR_DIR, new_filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(avatar.file, buffer)
            avatar_url = f"/images/{new_filename}"
    else:
        avatar_url = f"/images/default.png"

    new_user = pd.DataFrame([{'username' : username, 'password' : hash_password(password + username), 'avatar' : avatar_url, 'unique_id' : len(users_new)}])
    new_user.to_csv('users.csv', mode="a", index=False, header=False, encoding="utf-8")
    request.session['username'] = username
    request.session['password_hash'] = hash_password(password + username)
    request.session['session_starttime'] = str(datetime.now())
    request.session['user_unique_id'] = len(users_new)
    response = RedirectResponse(url=f"/home", status_code=302)
    return response