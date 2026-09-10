import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.endpoints import router as api_router
from src.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):

    os.makedirs("/data", exist_ok=True)

    async with engine.begin() as conn:

        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Smart Content Summarizer AI",
    description="API for scraping and summarizing articles using Gemini 1.5 Flash",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:5000",
        "https://reviewsense-0e26.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Smart Content Summarizer API is running successfully!"
    }
