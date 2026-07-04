from routes.v1.trading import memory
from fastapi import FastAPI

from database.database import Base, engine
from models.user import User
from models.trade import Trade
from routes.v1.trading import signals

from routes.v1 import health, auth, profile

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"]
)

app.include_router(
    auth.router,
    prefix="/api/v1",
    tags=["Auth"]
)

app.include_router(
    profile.router,
    prefix="/api/v1",
    tags=["Profile"]
)
app.include_router(
    signals.router,
    prefix="/api/v1",
    tags=["AI Signals"]
)
app.include_router(
    memory.router,
    prefix="/api/v1",
    tags=["AI Memory"]
)