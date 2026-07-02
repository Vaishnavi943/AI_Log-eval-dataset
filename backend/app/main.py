from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.config import settings
from app.routers import logs, sampling, clustering, labeling, review, export

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Production Log-to-Eval Dataset Builder")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(logs.router)
app.include_router(sampling.router)
app.include_router(clustering.router)
app.include_router(labeling.router)
app.include_router(review.router)
app.include_router(export.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "log-to-eval-dataset-builder"}
