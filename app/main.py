from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.api.v1.endpoints import redirect
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Metadata
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include Redirect Router (at root)
app.include_router(redirect.router)

@app.get("/", tags=["UI"])
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.on_event("startup")
async def startup_event():
    from app.db.session import engine, Base
    import app.db.models # Ensure models are loaded
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
