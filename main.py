from typing import Optional

import sentry_sdk
from envyaml import EnvYAML
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from src.database.models import User, UserRole
from src.dependencies import get_user, pwd_hash
from src.models.user import UserAPI
from src.routers import manager, auth, token


# read env.yaml config file
env = EnvYAML()

DEBUG: bool = env.get("DEBUG", False)
API_ROUTE_PREFIX: str = "/api/v1"

# Sentry integration
if not env.get("DEBUG"):
    sentry_sdk.init(env.get("SENTRY_DSN"), traces_sample_rate=1.0)

# Fast api start
app = FastAPI(
    title="Kapellmeister Manager",
    debug=DEBUG,
    version=env["version"],
    # default_response_class=ORJSONResponse,
    redoc_url=None,
    docs_url="/docs" if DEBUG else None,
)


# add templates to project
templates = Jinja2Templates(directory="templates")


# @app.on_event("startup")
# async def startup():
#     User.get_or_create(
#         dict(
#             username=env["default_user.username"], password=pwd_hash(env["default_user.password"]), role=UserRole.super
#         ),
#         id=1,
#     )


@app.get("/")
def home(request: Request, user: Optional[UserAPI] = Depends(get_user)):
    """Create home page"""
    if user:
        return templates.TemplateResponse("index.html", {"request": request, "username": user.username})
    return RedirectResponse(url="/login")


@app.get("/login")
async def login(request: Request):
    """Create login page"""
    error_message: str = ""
    if request.session.get("fail_login_message"):
        error_message = request.session.get("fail_login_message")
        request.session["fail_login_message"] = ""
    return templates.TemplateResponse("login.html", {"request": request, "error_message": error_message})


@app.get("/logout/")
async def logout(request: Request):
    """Clear session and logout user"""
    request.session.clear()
    return RedirectResponse(url="/")


@app.get("/tokens")
async def tokens(request: Request):
    """Create tokens page"""
    return templates.TemplateResponse("tokens.html", {"request": request})


@app.get("/users")
async def users(request: Request):
    """Create users page"""
    return templates.TemplateResponse("users.html", {"request": request})


# add static files to project
app.mount("/static", StaticFiles(directory="static"), name="static")

# include routes
app.include_router(manager.router, prefix=API_ROUTE_PREFIX)
app.include_router(auth.router, prefix=API_ROUTE_PREFIX)
app.include_router(token.router, prefix=API_ROUTE_PREFIX)

# we need this to save temporary code & state in session
app.add_middleware(SessionMiddleware, secret_key=env["security.key"])
