from fastapi import FastAPI

from config.settings import APP_NAME, APP_VERSION
from routes import health

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION
)

app.include_router(health.router)