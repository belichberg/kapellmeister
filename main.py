import sentry_sdk
from envyaml import EnvYAML
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse

# from src.database.db import database
from src.database import SessionLocal
from src.routers import manager

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
async def root():
    return PlainTextResponse("Kapellmeister")


# include routes
app.include_router(manager.router, prefix=API_ROUTE_PREFIX)
