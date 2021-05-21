import sentry_sdk
from envyaml import EnvYAML
from fastapi import FastAPI, Request, Response, Depends, Form, status
import sentry_sdk
from fastapi.responses import PlainTextResponse, RedirectResponse, HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager #Loginmanager Class
from fastapi_login.exceptions import InvalidCredentialsException #Exception class


from src.database.models import Container
from src.helpers import get_db
from src.routers import manager
# from src.database.db import database
from src.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


# read env.yaml config file
env = EnvYAML()

DEBUG: bool = env.get("DEBUG", False)
API_ROUTE_PREFIX: str = "/api/v1"

# Fast api start
app = FastAPI(
    title="Kapellmeister Manager",
    debug=DEBUG,
    version=env["version"],
    # default_response_class=ORJSONResponse,
    redoc_url=None,
    docs_url="/docs" if DEBUG else None,
)

# add static files to project
# app.mount("/static", StaticFiles(directory="static"), name="static")

# add templates to project
templates = Jinja2Templates(directory="templates")

# # Sentry integration
# if not env.get("DEBUG"):
#     sentry_sdk.init(env.get("SENTRY_DSN"), traces_sample_rate=1.0)

SECRET = "secret-key"
# To obtain a suitable secret key you can run | import os; print(os.urandom(24).hex())

login_manager = LoginManager(SECRET, token_url="/login", use_cookie=True)
# login_manager.cookie_name = "user"

DB = {"user": {"password": "1111"}}


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response: Response = Response("Internal server error", status_code=500)

    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()

    return response

# @app.on_event("startup")
# async def startup():
#     await database.connect()
#
#
# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()


# @app.get("/")
# async def root(db: Session = Depends(get_db)):
#     # print(db.query(Container).first().__dict__)
#     return PlainTextResponse("Kapellmeister")

# @app.get("/")
# async def home(request: Request):
#     """Create main page"""
#     user: str = ""
#     if user:
#         return templates.TemplateResponse("index.html", {"request": request, "username": request.session.get("user")})
#     else:
#         return RedirectResponse(url='/login')

# @app.get("/login")
# async def login(request: Request):
#     """Create login page"""
#     return templates.TemplateResponse("login.html", {"request": request})

# @app.post("/login_user")
# async def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
#     """Get username, password from login form"""
#     print(username, password)
#     return templates.TemplateResponse("index.html", {"request": request, "username": username})

@login_manager.user_loader
def load_user(username: str):
    user = DB.get(username)
    return user

@app.get("/")
def home(request: Request):
    """Create home page"""

    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(data: OAuth2PasswordRequestForm = Depends()):
    """Create login page"""
    username: str = data.username
    password: str = data.password
    # print(username, password)
    user = load_user(username)
    if not user:
        raise InvalidCredentialsException
    elif password != user['password']:
        raise InvalidCredentialsException
    access_token = login_manager.create_access_token(data={"sub": username})
    login_manager.set_cookie(RedirectResponse(url="/private"), access_token)
    login_manager.cookie_name = username
    # print(f"login_manager.cookie_name = {login_manager.cookie_name}")
    # print(login_manager.get_current_user(access_token))
    return RedirectResponse(url="/private")

@app.post("/private")
# def getPrivateendpoint(user=Depends(login_manager)):
async def getPrivateendpoint(request: Request, db: Session = Depends(get_db)):
    # print(db.query(Container).first().__dict__)
    # RedirectResponse(url="/")
    return templates.TemplateResponse("index.html", {"request": request, "username": login_manager.cookie_name})

@app.get("/logout")
async def logout(request: Request, user=Depends(login_manager)):
    resp = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    login_manager.set_cookie(resp, "")
    return resp

# include routes
# app.include_router(manager.router, prefix=API_ROUTE_PREFIX)
