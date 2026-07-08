from fastapi import FastAPI

from database.database import Base, engine

# Import models so SQLAlchemy creates the tables
from models.user import User
from models.trade import Trade
from models.broker_account import BrokerAccount

# API routes
from routes.v1 import health
from routes.v1 import auth
from routes.v1 import profile
from routes.v1 import brokers
from routes.v1 import trade
from routes.v1.trading import sync
from routes.v1.trading import analytics
from routes.v1.trading import signals
from routes.v1.trading import memory
from routes.v1 import analytics
from routes.v1 import analytics_charts
from routes.v1 import risk
from routes.v1 import coach
app = FastAPI(
    title="TradePilot AI",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

# Health
app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"]
)

# Authentication
app.include_router(
    auth.router,
    prefix="/api/v1",
    tags=["Authentication"]
)

# User Profile
app.include_router(
    profile.router,
    prefix="/api/v1",
    tags=["Profile"]
)

# Broker Connection
app.include_router(
    brokers.router,
    prefix="/api/v1",
    tags=["Brokers"]
)

# Trade Sync
app.include_router(
    sync.router,
    prefix="/api/v1",
    tags=["Trading"]
)

# AI Signals
app.include_router(
    signals.router,
    prefix="/api/v1",
    tags=["AI Signals"]
)

# AI Memory
app.include_router(
    memory.router,
    prefix="/api/v1",
    tags=["AI Memory"]
)
app.include_router(
    trade.router,
    prefix="/api/v1",
    tags=["Trades"]
)
# Analytics
app.include_router(
    analytics.router,
    prefix="/api/v1",
    tags=["Analytics"]
)
app.include_router(
    analytics_charts.router,
    prefix="/api/v1"
)
app.include_router(
    risk.router,
    prefix="/api/v1"
)
app.include_router(
    coach.router,
    prefix="/api/v1"
)