from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, users, transactions, goals, reports, notifications
from app.core.config import settings

app = FastAPI(
    title="Family Finance Manager",
    description="A system to manage family finances, track expenses and set goals",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(transactions.router, prefix="/api", tags=["Transactions"])
app.include_router(goals.router, prefix="/api", tags=["Goals"])
app.include_router(reports.router, prefix="/api", tags=["Reports"])
app.include_router(notifications.router, prefix="/api", tags=["Notifications"])

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root():
    return {"message": "Welcome to Family Finance Manager API"}
