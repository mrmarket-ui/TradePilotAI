from fastapi import FastAPI

from database.database import Base, engine
from models.user import User

from routes.v1 import health, auth

app = FastAPI()

Base.metadata.create_all(bind=engine)
from sqlalchemy import inspect

print("Tables:", inspect(engine).get_table_names())

app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])