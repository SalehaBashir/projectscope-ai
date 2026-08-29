from app.api import estimate
from app.api import tasks
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import projects
from app.api import analyze
from app.api import questions

app = FastAPI(title="ProjectScope AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router, prefix="/api/v1")
app.include_router(analyze.router, prefix="/api/v1")
app.include_router(questions.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(estimate.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "ProjectScope AI backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}