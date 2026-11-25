from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import db
from .routes import router


@asynccontextmanager
async def lifespan(application: FastAPI):
    # Create tables and seed sample data before serving requests.
    db.initialize()
    yield


app = FastAPI(title="Side Streets", lifespan=lifespan)

# Make the router's endpoints available through this application.
app.include_router(router)
