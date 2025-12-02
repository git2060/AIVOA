import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api import interactions, agent
from config import settings
from database.setup import create_db_and_tables

# 1. Lifespan Context Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup: Creating database tables...")
    await create_db_and_tables()
    print("Database ready. Starting application...")
    yield
    print("Application shutdown complete.")

# 2. FastAPI Initialization
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan 
)

# 3. CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Include API Routers
app.include_router(interactions.router, prefix=settings.API_V1_STR + "/interactions", tags=["Interactions"])
app.include_router(agent.router, prefix=settings.API_V1_STR + "/agent", tags=["Agent"])

# 5. Root Endpoint (Sanity check)
@app.get("/")
def read_root():
    return {"message": "AI-First HCP CRM API is running."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)