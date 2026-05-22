"""FitAgent - Main application entry point."""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fitagent.config import settings
from fitagent.api.routes import router
from fitagent.api.auth import auth_router

app = FastAPI(
    title="FitAgent",
    description="Multi-Agent Fitness Coaching Platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api", tags=["coaching"])
app.include_router(auth_router, tags=["authentication"])


@app.get("/")
async def root():
    """Root endpoint with application info."""
    return {
        "name": "FitAgent",
        "version": "0.1.0",
        "description": "Multi-Agent Fitness Coaching Platform",
        "agents": [
            {
                "name": "Running Coach (Coach Marcus)",
                "expertise": "All running distances, 25+ years experience",
                "endpoint": "/api/chat with agent_type='running'",
            },
            {
                "name": "Triathlon Coach (Coach Elena)",
                "expertise": "Sprint to Ironman, 25+ years experience",
                "endpoint": "/api/chat with agent_type='triathlon'",
            },
            {
                "name": "Hyrox Coach (Coach Viktor)",
                "expertise": "Hyrox race preparation, 25+ years experience",
                "endpoint": "/api/chat with agent_type='hyrox'",
            },
            {
                "name": "Strength Coach (Coach Dmitri)",
                "expertise": "Strength for endurance athletes, 25+ years experience",
                "endpoint": "/api/chat with agent_type='strength'",
            },
            {
                "name": "Nutritionist (Dr. Sofia)",
                "expertise": "Sports nutrition, 30+ years experience",
                "endpoint": "/api/chat with agent_type='nutrition'",
            },
        ],
        "integrations": ["Strava", "TrainingPeaks", "Garmin Connect"],
        "docs": "/docs",
    }


def main():
    """Run the application."""
    uvicorn.run(
        "fitagent.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True,
    )


if __name__ == "__main__":
    main()
