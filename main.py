import sentry_sdk
from envyaml import EnvYAML
from fastapi import FastAPI, Request, Response, Depends, File, UploadFile, Form
import sentry_sdk
from fastapi.responses import PlainTextResponse

from src.database.models import Container
from src.helpers import get_db
from src.routers import manager
# from src.database.db import database
from src.database.db import SessionLocal
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


# @app.get("/")
# async def root(db: Session = Depends(get_db)):
#     # print(db.query(Container).first().__dict__)
#     return PlainTextResponse("Kapellmeister")

# @app.get("/login")
# async def login(request: Request):
#     """Create user login page"""
#     return templates.TemplateResponse(
#             "login.html",
#             {
#                 "request": request
#             }
#     )

@app.get("/")
async def home(request: Request):
    """Create user login page"""

    user: str = ""
    if user:
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    print(username, password)
    return PlainTextResponse("You Logined!")
    # return templates.TemplateResponse("index.html", {"request": request})



# include routes
app.include_router(manager.router, prefix=API_ROUTE_PREFIX)
