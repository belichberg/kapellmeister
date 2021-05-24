from envyaml import EnvYAML
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse

# from src.database.db import database
from src.database import SessionLocal
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


# # Sentry integration
# if not env.get("DEBUG"):
#     sentry_sdk.init(env.get("SENTRY_DSN"), traces_sample_rate=1.0)


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
def home(request: Request):
    """Create home page"""
    #
    # for route in request.app.routes:
    #     print(route)
    # return RedirectResponse(url="/login/")
    return templates.TemplateResponse("login.html", {"request": request})


# include routes
app.include_router(manager.router, prefix=API_ROUTE_PREFIX)
app.include_router(auth.router, prefix=API_ROUTE_PREFIX)


# @app.post("/login/")
# async def login(request: Request, form: OAuth2PasswordRequestForm = Depends()):
#     """Create login page"""
#     username: str = form.username
#     password: str = form.password
#     #  get user from fake_db
#     check_user = load_user(username)
#
#     # validate user
#     if not check_user or password != check_user['password']:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, detail="Invalid user or password"
#         )
#     access_token = login_manager.create_access_token(data={"sub": username})
#     login_manager.set_cookie(RedirectResponse(url="/private"), access_token)
#     login_manager.cookie_name: str = username

# # build data
# data: TokenData = TokenData(
#     sub=username
# )

# return RedirectResponse(url="/private")

# @app.post("/private/")
# async def getPrivateendpoint(request: Request, db: Session = Depends(get_db)):
#     # print(db.query(Container).first().__dict__)
#     # print(db.query(Container).all())
#     # RedirectResponse(url="/")
#     return templates.TemplateResponse("index.html", {"request": request, "username": login_manager.cookie_name})

# @app.get("/logout/")
# async def logout():
#     resp = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
#     login_manager.set_cookie(resp, "")
#     return resp
