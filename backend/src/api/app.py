"""Main FastAPI application for GramSaarthi AI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.enterprise_routes import router as enterprise_router
from src.api.voice_routes import router as voice_router
from src.api.market_routes import router as market_router
from src.api.scheme_routes import router as scheme_router
from src.api.financial_routes import router as financial_router
from src.api.operations_routes import router as operations_router


# Create FastAPI application
app = FastAPI(
    title="GramSaarthi AI API",
    description="Voice-first rural growth orchestration platform API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://localhost:5173",  # Vite development server
        "http://localhost:8000",  # Local API testing
        "*",  # Allow all origins for hackathon demo
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers
)

# Include routers
app.include_router(enterprise_router)
app.include_router(voice_router)
app.include_router(market_router)
app.include_router(scheme_router)
app.include_router(financial_router)
app.include_router(operations_router)


@app.get("/", tags=["health"])
async def root():
    """Root endpoint."""
    return {
        "service": "GramSaarthi AI API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns the health status of the API service.
    """
    return {
        "status": "healthy",
        "service": "GramSaarthi AI API",
    }


@app.get("/api/v1/health", tags=["health"])
async def api_health_check():
    """
    API health check endpoint.
    
    Returns the health status of the API service with version info.
    """
    return {
        "status": "healthy",
        "service": "GramSaarthi AI API",
        "version": "1.0.0",
        "api_version": "v1",
    }


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "NOT_FOUND",
            "message": "The requested resource was not found",
            "path": str(request.url),
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An internal server error occurred",
        },
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
