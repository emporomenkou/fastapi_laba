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

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.mount("/images", StaticFiles(directory="images"), name="images")
