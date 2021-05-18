from envyaml import EnvYAML
from fastapi import FastAPI
import sentry_sdk
from src.database import db
from fastapi.responses import PlainTextResponse


# read env.yaml config file
env = EnvYAML()

DEBUG: bool = env.get("DEBUG", False)

# Fast api start
app = FastAPI(
    title="Kapellmeister Manager",
    debug=DEBUG,
    version=env["version"],
    redoc_url=None,
    docs_url="/docs" if DEBUG else None,
)

# Sentry integration
if not env.get("DEBUG"):
    sentry_sdk.init(env.get("SENTRY_DSN"), traces_sample_rate=1.0)


@app.get("/")
async def root():
    dbms = db.MyDatabase(db.SQLITE, dbname='mydb.sqlite')
    # Create Tables
    dbms.create_db_tables()
    # dbms.insert_single_data()
    dbms.print_all_data(db.PROJECTS)
    dbms.print_all_data(db.CHANNELS)
    dbms.print_all_data(db.CONTAINERS)
    # dbms.sample_query()  # simple query
    # dbms.sample_delete()  # delete data
    # dbms.sample_insert()  # insert data
    # dbms.sample_update()  # update data
    return PlainTextResponse("⇚ B.M.R.F © 2021 ⇛")