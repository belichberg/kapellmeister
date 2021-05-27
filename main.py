from typing import Optional

from envyaml import EnvYAML
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from src.database.models import User, UserRole
from src.dependencies import get_user, pwd_hash
from src.models.user import UserAPI
from src.routers import manager, auth

# read env.yaml config file
env = EnvYAML()

DEBUG: bool = env.get("DEBUG", False)
API_ROUTE_PREFIX: str = "/api/v1"

# # Sentry integration
# if not env.get("DEBUG"):
#     sentry_sdk.init(env.get("SENTRY_DSN"), traces_sample_rate=1.0)

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


@app.on_event("startup")
async def startup():
    User.get_or_create(dict(username=env["default_user.username"], password=pwd_hash(env["default_user.password"]), role=UserRole.super), id=1)


@app.get("/")
def home(request: Request, user: Optional[UserAPI] = Depends(get_user)):
    """Create home page"""

    # print(f"token = {request.session.get('token')}")
    # print(f"request.session = {request.session}")

    if user:
        # user: UserAPI = get_user(token, db)

        return templates.TemplateResponse("index.html", {"request": request, "username": user.username})
    return RedirectResponse(url="/login")


@app.get("/login")
async def login(request: Request):
    """Create login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/logout/")
async def logout(request: Request):
    """Clear session and logout user"""
    # response.delete_cookie("session")
    request.session.clear()
    return {"status": "ok"}
    # return RedirectResponse(url="/")


# add static files to project
app.mount("/static", StaticFiles(directory="static"), name="static")

# include routes
app.include_router(manager.router, prefix=API_ROUTE_PREFIX)
app.include_router(auth.router, prefix=API_ROUTE_PREFIX)

# we need this to save temporary code & state in session
app.add_middleware(SessionMiddleware, secret_key=env["security.key"])
