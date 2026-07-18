from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import Base, engine

# Import models so SQLAlchemy registers their tables
from models.user import User
from models.trade import Trade
from models.broker_account import BrokerAccount
from models.strategy_profile import StrategyProfile

# Core routes
from routes.v1 import health
from routes.v1 import auth
from routes.v1 import profile
from routes.v1 import brokers
from routes.v1 import trade
from routes.v1 import analytics
from routes.v1 import analytics_charts
from routes.v1 import risk
from routes.v1 import coach
from routes.v1 import coach_v2
from routes.v1 import recommendations
from routes.v1 import ai_chat

# Trading routes
from routes.v1.trading import sync
from routes.v1.trading import analytics as trading_analytics
from routes.v1.trading import signals
from routes.v1.trading import memory
from routes.v1 import trade_review
from routes.v1 import weekly_review
from routes.v1 import monthly_review
from routes.v1 import strategy_profiles

app = FastAPI(
    title="TradePilot AI",
    version="1.0.0",
    description=(
        "Professional AI-powered trading journal, "
        "analytics and coaching platform."
    ),
)
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


# Health
app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"],
)

# Authentication
app.include_router(
    auth.router,
    prefix="/api/v1",
    tags=["Authentication"],
)

# Profile
app.include_router(
    profile.router,
    prefix="/api/v1",
    tags=["Profile"],
)

# Brokers
app.include_router(
    brokers.router,
    prefix="/api/v1",
    tags=["Brokers"],
)

# Trades
app.include_router(
    trade.router,
    prefix="/api/v1",
    tags=["Trades"],
)

# Trading sync
app.include_router(
    sync.router,
    prefix="/api/v1",
    tags=["Trading"],
)

# Trading analytics
app.include_router(
    trading_analytics.router,
    prefix="/api/v1",
    tags=["Trading Analytics"],
)

# AI signals
app.include_router(
    signals.router,
    prefix="/api/v1",
    tags=["AI Signals"],
)

# AI memory
app.include_router(
    memory.router,
    prefix="/api/v1",
    tags=["AI Memory"],
)

# Analytics
app.include_router(
    analytics.router,
    prefix="/api/v1",
    tags=["Analytics"],
)

# Analytics charts
app.include_router(
    analytics_charts.router,
    prefix="/api/v1",
    tags=["Analytics Charts"],
)

# Risk analytics
app.include_router(
    risk.router,
    prefix="/api/v1",
    tags=["Risk Analytics"],
)

# Original AI Coach
app.include_router(
    coach.router,
    prefix="/api/v1",
    tags=["AI Coach"],
)

# AI Coach V2
app.include_router(
    coach_v2.router,
    prefix="/api/v1",
)

# AI recommendations
app.include_router(
    recommendations.router,
    prefix="/api/v1",
    tags=["AI Recommendations"],
)

# AI Chat Coach
app.include_router(
    ai_chat.router,
    prefix="/api/v1",
)
app.include_router(
    trade_review.router,
    prefix="/api/v1",
)


# Strategy Brain
app.include_router(
    strategy_profiles.router,
    prefix="/api/v1",
)
@app.get("/", tags=["System"])
def root():
    return {
        "application": "TradePilot AI",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }

# Weekly AI Review
app.include_router(
    weekly_review.router,
    prefix="/api/v1",
)

# Monthly AI Review
app.include_router(
    monthly_review.router,
    prefix="/api/v1",
)




