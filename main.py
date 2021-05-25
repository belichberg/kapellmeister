import json
from datetime import datetime

import sentry_sdk
from envyaml import EnvYAML
from fastapi import FastAPI, Request, Response, status, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse, PlainTextResponse

# from src.database.db import database
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
import itsdangerous

from src.database import SessionLocal
from src.dependencies import get_user, token_validate
from src.helpers import get_db, time_utc_now
from src.models.user import UserAPI, Token
from src.routers import manager, auth

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
app.mount("/static", StaticFiles(directory="static"), name="static")

# add templates to project
templates = Jinja2Templates(directory="templates")

# Sentry integration
if not env.get("DEBUG"):
    sentry_sdk.init(env.get("SENTRY_DSN"), traces_sample_rate=1.0)


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


@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    """Create home page"""

    # check if token exists
    if request.session.get('token'):
        token: Token = Token.parse_obj(json.loads(request.session.get('token')))

        # when access token time is run out redirect to login page
        if token_validate(token.access_token) is None:
            return RedirectResponse(url='/login')

        # if all is ok return home page
        else:
            # token: Token = Token.parse_obj(json.loads(request.session.get('token')))
            user: UserAPI = get_user(token, db)
            return templates.TemplateResponse("index.html", {"request": request, "username": user.username})

    return RedirectResponse(url='/login')
    # return PlainTextResponse("⇚ B.M.R.F © 2021 ⇛")


@app.get("/login")
async def login(request: Request):
    """Create login page"""

    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/logout/")
async def logout(request: Request):
    """Clear session and logout user"""

    request.session.clear()
    return RedirectResponse(url='/')


# include routes
app.include_router(manager.router, prefix=API_ROUTE_PREFIX)
app.include_router(auth.router, prefix=API_ROUTE_PREFIX)

# we need this to save temporary code & state in session
app.add_middleware(SessionMiddleware, secret_key=env["security.key"])
