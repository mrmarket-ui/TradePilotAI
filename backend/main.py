from fastapi import FastAPI

from database.database import Base, engine

# Models
from models.user import User
from models.trade import Trade
from models.broker_account import BrokerAccount

# Routes
from routes.v1 import health
from routes.v1 import auth
from routes.v1 import profile
from routes.v1 import brokers
from routes.v1 import trade
from routes.v1 import analytics
from routes.v1 import analytics_charts
from routes.v1 import risk
from routes.v1 import coach
from routes.v1 import recommendations
from routes.v1 import coach_v2


# Trading Routes
from routes.v1.trading import sync
from routes.v1.trading import analytics as trading_analytics
from routes.v1.trading import signals
from routes.v1.trading import memory

app = FastAPI(
    title="TradePilot AI",
    version="1.0.0",
    description="Professional AI-Powered Trading Journal & Analytics Platform"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# ----------------------------------------
# Health
# ----------------------------------------

app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"]
)

# ----------------------------------------
# Authentication
# ----------------------------------------

app.include_router(
    auth.router,
    prefix="/api/v1",
    tags=["Authentication"]
)

# ----------------------------------------
# User Profile
# ----------------------------------------

app.include_router(
    profile.router,
    prefix="/api/v1",
    tags=["Profile"]
)

# ----------------------------------------
# Broker Accounts
# ----------------------------------------

app.include_router(
    brokers.router,
    prefix="/api/v1",
    tags=["Brokers"]
)

# ----------------------------------------
# Trades
# ----------------------------------------

app.include_router(
    trade.router,
    prefix="/api/v1",
    tags=["Trades"]
)

# ----------------------------------------
# Trading Sync
# ----------------------------------------

app.include_router(
    sync.router,
    prefix="/api/v1",
    tags=["Trading"]
)

# ----------------------------------------
# Trading Analytics
# ----------------------------------------

app.include_router(
    trading_analytics.router,
    prefix="/api/v1",
    tags=["Trading Analytics"]
)

# ----------------------------------------
# AI Signals
# ----------------------------------------

app.include_router(
    signals.router,
    prefix="/api/v1",
    tags=["AI Signals"]
)

# ----------------------------------------
# AI Memory
# ----------------------------------------

app.include_router(
    memory.router,
    prefix="/api/v1",
    tags=["AI Memory"]
)

# ----------------------------------------
# Analytics
# ----------------------------------------

app.include_router(
    analytics.router,
    prefix="/api/v1",
    tags=["Analytics"]
)

# ----------------------------------------
# Analytics Charts
# ----------------------------------------

app.include_router(
    analytics_charts.router,
    prefix="/api/v1",
    tags=["Analytics Charts"]
)

# ----------------------------------------
# Risk Analytics
# ----------------------------------------

app.include_router(
    risk.router,
    prefix="/api/v1",
    tags=["Risk Analytics"]
)

# ----------------------------------------
# AI Coach
# ----------------------------------------

app.include_router(
    coach.router,
    prefix="/api/v1",
    tags=["AI Coach"]
)

# ----------------------------------------
# AI Recommendations
# ----------------------------------------

app.include_router(
    recommendations.router,
    prefix="/api/v1",
    tags=["AI Recommendations"]
)
app.include_router(
    coach_v2.router,
    prefix="/api/v1",
)

# ----------------------------------------
# Root Endpoint
# ----------------------------------------

@app.get("/")
def root():
    return {
        "application": "TradePilot AI",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"   
 }