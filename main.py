from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import connect_db, close_db
from app.routes import user_routes, admin_routes, agent_routes, product_routes, order_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
    yield
    # Shutdown
    await close_db()

app = FastAPI(
    title="VegGo API",
    description="Complete Vegetable Delivery Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routes
app.include_router(user_routes.router, prefix="/api/user", tags=["Users"])
app.include_router(admin_routes.router, prefix="/api/admin", tags=["Admin"])
app.include_router(agent_routes.router, prefix="/api/agent", tags=["Agents"])
app.include_router(product_routes.router, prefix="/api", tags=["Products"])
app.include_router(order_routes.router, prefix="/api", tags=["Orders"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to VegGo API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
