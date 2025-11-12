"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import alerts, events, incidents, integrations
from config.settings import settings

try:
    from api.routes import ml

    ML_ROUTES_AVAILABLE = True
except ImportError:
    ML_ROUTES_AVAILABLE = False

app = FastAPI(
    title=settings.APP_NAME,
    description="CSIRT Platform - Security Incident Response Team",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(events.router, prefix="/api/v1/events", tags=["Events"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["Incidents"])
app.include_router(
    integrations.router, prefix="/api/v1/integrations", tags=["Integrations"]
)
if ML_ROUTES_AVAILABLE:
    app.include_router(ml.router, prefix="/api/v1", tags=["ML"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "CSIRT Platform API", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
