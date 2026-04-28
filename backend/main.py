"""
RealSTEM FastAPI Application Entry Point

Main application initialization, middleware setup, route registration,
and lifecycle management for the RealSTEM backend service.
"""
import logging
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Store for active WebSocket connections
class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept and store a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"✨ Client connected. Active connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a disconnected WebSocket connection"""
        self.active_connections.remove(websocket)
        logger.info(f"👋 Client disconnected. Active connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all active connections"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to client: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


manager = ConnectionManager()


# Lifecycle events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Async context manager for application startup and shutdown events
    """
    # Startup event
    logger.info("=" * 60)
    logger.info("🚀 RealSTEM Backend starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info(f"API Version: {settings.VERSION}")
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'N/A'}")
    logger.info("=" * 60)
    yield
    # Shutdown event
    logger.info("=" * 60)
    logger.info("🛑 RealSTEM Backend shutting down...")
    logger.info(f"Shutdown time: {datetime.utcnow().isoformat()}")
    logger.info("=" * 60)


# Initialize FastAPI app
app = FastAPI(
    title="RealSTEM API",
    description="AI-powered STEM education platform with adaptive lessons and real-time collaboration",
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)


# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring service status
    
    Returns:
        JSON with status, version, service name, and timestamp
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "service": "RealSTEM Backend",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information
    
    Returns:
        JSON with API metadata and documentation links
    """
    return {
        "message": "Welcome to RealSTEM API",
        "service": "AI-Powered STEM Education Platform",
        "version": settings.VERSION,
        "docs": "/docs" if settings.DEBUG else "Not available",
        "redoc": "/redoc" if settings.DEBUG else "Not available",
    }


# ============================================================================
# WebSocket Endpoint for Real-time Updates
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates and notifications
    
    Handles WebSocket connections for:
    - Real-time collaboration updates
    - Live lesson notifications
    - Progress tracking
    - Chat messages
    
    Args:
        websocket: WebSocket connection object
    """
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            logger.debug(f"📨 WebSocket message received: {data}")
            
            # Echo message back with metadata
            response = {
                "type": data.get("type", "message"),
                "data": data.get("data"),
                "timestamp": datetime.utcnow().isoformat(),
                "echo": True,
            }
            
            # Send back to client
            await websocket.send_json(response)
            
            # Optional: Broadcast to other clients for shared updates
            if data.get("broadcast"):
                response["echo"] = False
                await manager.broadcast(response)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        manager.disconnect(websocket)


# ============================================================================
# API Route Registration
# ============================================================================

# Import routers
try:
    from api.news import router as news_router
    from api.lessons import router as lessons_router
    from api.users import router as users_router
    from api.collaboration import router as collaboration_router
    from api.analytics import router as analytics_router
    
    # Include routers with prefixes
    app.include_router(
        news_router,
        prefix="/api/news",
        tags=["News"],
    )
    
    app.include_router(
        lessons_router,
        prefix="/api/lessons",
        tags=["Lessons"],
    )
    
    app.include_router(
        users_router,
        prefix="/api/users",
        tags=["Users"],
    )
    
    app.include_router(
        collaboration_router,
        prefix="/api/collaboration",
        tags=["Collaboration"],
    )
    
    app.include_router(
        analytics_router,
        prefix="/api/analytics",
        tags=["Analytics"],
    )
    
    logger.info("✅ All API routers successfully registered")

except ImportError as e:
    logger.warning(f"⚠️ Some routers could not be imported: {e}")
    logger.info("Continue with available routers...")


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors
    
    Args:
        request: Request object
        exc: Exception object
        
    Returns:
        JSON error response
    """
    logger.error(f"❌ Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred",
        },
    )


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    """
    Run the FastAPI application with Uvicorn
    """
    logger.info(f"Starting RealSTEM Backend on {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level="info" if settings.DEBUG else "warning",
        access_log=settings.DEBUG,
    )
