"""
GenAIFinOps REST API
FastAPI application with endpoints for cost optimization.
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from api.models import (
    OracleRequest, OracleResponse,
    ArchitectRequest, ArchitectResponse,
    ScraperStatusResponse, ScraperRunResponse,
    HealthResponse, QueryResponse, QueryResult,
    LoginRequest, TokenResponse, UserResponse
)

from utils.pricing_knowledge_base import PricingKnowledgeBase
from agents.oracle import PricingOracle
from agents.architect import CostArchitect
from agents.scraper import OpenAIPricingScraper
from utils.logger import logger
from utils.auth import (
    verify_password, get_password_hash, create_access_token,
    get_current_user, get_current_user_optional
)
from utils.rate_limit import setup_rate_limiting, rate_limit_decorator, get_rate_limit_config

# Load environment variables
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS", "*").split(",") if os.getenv("ALLOW_ORIGINS") != "*" else ["*"]

app = FastAPI(
    title="GenAIFinOps API",
    description="The 'Kubernetes' of AI Costs - Automated Token Optimization & Multi-Cloud Pricing Intelligence",
    version="0.3.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS if ALLOW_ORIGINS != ["*"] else CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup rate limiting
rate_limiting_enabled = setup_rate_limiting(app)
if rate_limiting_enabled:
    logger.info("Rate limiting enabled", **get_rate_limit_config())
else:
    logger.info("Rate limiting disabled")

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with structured logging."""
    start_time = datetime.utcnow()
    
    # Log request
    logger.info(
        "Request received",
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else None
    )
    
    try:
        response = await call_next(request)
        process_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Log response
        logger.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time=process_time
        )
        
        return response
    except Exception as e:
        process_time = (datetime.utcnow() - start_time).total_seconds()
        logger.error(
            "Request failed",
            method=request.method,
            path=request.url.path,
            error=str(e),
            process_time=process_time
        )
        raise

# Initialize services
kb = PricingKnowledgeBase()
oracle = PricingOracle(kb)
architect = CostArchitect(kb)
executor = ThreadPoolExecutor(max_workers=2)

# In-memory user store (for demo - use database in production)
# In production, use a proper database
DEMO_USERS = {
    "admin": get_password_hash("admin123"),
    "user": get_password_hash("user123"),
}


@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "GenAIFinOps API",
        "version": "0.3.0",
        "description": "The 'Kubernetes' of AI Costs",
        "docs": "/docs",
        "endpoints": {
            "oracle": "/api/oracle/ask",
            "architect": "/api/architect/optimize",
            "scraper": "/api/scraper/status",
            "query": "/api/query",
            "auth": "/api/auth/login"
        },
        "rate_limiting": get_rate_limit_config()
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint."""
    stats = kb.get_stats()

    return HealthResponse(
        status="healthy",
        version="0.3.0",
        knowledge_base_status="operational" if stats["total_models"] > 0 else "empty",
        llm_available=oracle.llm_available
    )


# Authentication endpoints
@app.post("/api/auth/login", response_model=TokenResponse, tags=["Authentication"])
@rate_limit_decorator(calls=5, period="minute")
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT token.
    
    Demo credentials:
    - username: admin, password: admin123
    - username: user, password: user123
    """
    try:
        # Check if user exists
        if request.username not in DEMO_USERS:
            logger.warning("Login attempt failed", username=request.username, reason="user_not_found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Verify password
        hashed_password = DEMO_USERS[request.username]
        if not verify_password(request.password, hashed_password):
            logger.warning("Login attempt failed", username=request.username, reason="invalid_password")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")))
        access_token = create_access_token(
            data={"sub": request.username},
            expires_delta=access_token_expires
        )
        
        logger.info("User logged in successfully", username=request.username)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(access_token_expires.total_seconds())
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login error", error=str(e))
        raise HTTPException(status_code=500, detail="Authentication failed")


@app.get("/api/auth/me", response_model=UserResponse, tags=["Authentication"])
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """Get current authenticated user information."""
    return UserResponse(
        username=user["username"],
        authenticated=True
    )


@app.post("/api/oracle/ask", response_model=OracleResponse, tags=["Oracle"])
@rate_limit_decorator(calls=30, period="minute")
async def ask_oracle(request: OracleRequest, user: Optional[dict] = Depends(get_current_user_optional)):
    """
    Ask the Oracle a pricing question using RAG + LLM.

    This endpoint uses semantic search to find relevant pricing data,
    then uses an LLM to generate a natural language response.
    """
    try:
        if not request.question or request.question.strip() == "":
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        logger.info("Oracle query", question=request.question[:100], user=user["username"] if user else "anonymous")

        loop = asyncio.get_event_loop()
        answer = await loop.run_in_executor(
            executor,
            oracle.ask,
            request.question,
            request.n_results
        )

        logger.info("Oracle query completed", question=request.question[:100])

        return OracleResponse(
            status="success",
            question=request.question,
            answer=answer,
            context_used=request.n_results
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Oracle error", error=str(e), question=request.question[:100])
        raise HTTPException(status_code=500, detail=f"Oracle error: {str(e)}")


@app.post("/api/architect/optimize", response_model=ArchitectResponse, tags=["Architect"])
@rate_limit_decorator(calls=20, period="minute")
async def optimize_costs(request: ArchitectRequest, user: Optional[dict] = Depends(get_current_user_optional)):
    """
    Analyze a use case and recommend optimal model choices.

    This endpoint analyzes your use case, calculates costs for different models,
    and recommends the most cost-effective option.
    """
    try:
        logger.info(
            "Architect optimization request",
            use_case=request.use_case_description[:100],
            tokens=request.monthly_input_tokens,
            user=user["username"] if user else "anonymous"
        )

        loop = asyncio.get_event_loop()
        analysis = await loop.run_in_executor(
            executor,
            architect.analyze_and_optimize,
            request.use_case_description,
            request.monthly_input_tokens,
            request.monthly_output_tokens,
            request.current_model
        )

        if analysis.get("status") == "error":
            raise HTTPException(status_code=400, detail=analysis.get("message", "Analysis failed"))

        logger.info("Architect optimization completed", use_case=request.use_case_description[:100])

        return ArchitectResponse(**analysis)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Architect error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Architect error: {str(e)}")


@app.get("/api/scraper/status", response_model=ScraperStatusResponse, tags=["Scraper"])
async def get_scraper_status():
    """
    Get the current status of the pricing knowledge base.

    Returns information about the number of models, providers,
    and when the data was last updated.
    """
    try:
        stats = kb.get_stats()

        return ScraperStatusResponse(
            status="operational",
            total_models=stats["total_models"],
            providers=stats["providers"],
            last_updated=datetime.utcnow().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check error: {str(e)}")


def run_scraper_background():
    """Background task to run the scraper."""
    try:
        scraper = OpenAIPricingScraper(kb)
        count = scraper.run()
        return count
    except Exception as e:
        print(f"Background scraper error: {str(e)}")
        return 0


@app.post("/api/scraper/run", response_model=ScraperRunResponse, tags=["Scraper"])
@rate_limit_decorator(calls=5, period="hour")
async def run_scraper(background_tasks: BackgroundTasks, user: dict = Depends(get_current_user)):
    """
    Manually trigger the scraper to update pricing data.

    This runs the scraper in the background and returns immediately.
    Requires authentication.
    """
    try:
        logger.info("Scraper triggered", user=user["username"])
        
        loop = asyncio.get_event_loop()
        count = await loop.run_in_executor(executor, run_scraper_background)

        logger.info("Scraper completed", entries_added=count, user=user["username"])

        return ScraperRunResponse(
            status="success",
            message=f"Scraper completed successfully",
            entries_added=count
        )

    except Exception as e:
        logger.error("Scraper error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Scraper error: {str(e)}")


@app.post("/api/query", response_model=QueryResponse, tags=["Search"])
@rate_limit_decorator(calls=60, period="minute")
async def semantic_search(query: str, n_results: Optional[int] = 5, user: Optional[dict] = Depends(get_current_user_optional)):
    """
    Perform semantic search on pricing data.

    This endpoint performs vector similarity search without LLM processing.
    Use this for raw data retrieval.
    """
    try:
        if not query or query.strip() == "":
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        results = kb.query_prices(query, n_results=n_results)

        if not results:
            return QueryResponse(
                status="success",
                query=query,
                results=[],
                total_results=0
            )

        formatted_results = []
        for result in results:
            meta = result['metadata']
            formatted_results.append(QueryResult(
                provider=meta['provider'],
                model_name=meta['model_name'],
                input_cost=meta['input_cost'],
                output_cost=meta['output_cost'],
                context_window=meta.get('context_window'),
                supports_function_calling=meta.get('supports_function_calling')
            ))

        return QueryResponse(
            status="success",
            query=query,
            results=formatted_results,
            total_results=len(formatted_results)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")


@app.get("/api/providers", tags=["Data"])
async def list_providers():
    """List all available providers in the knowledge base."""
    try:
        providers = kb.get_all_providers()
        return {
            "status": "success",
            "providers": providers,
            "total": len(providers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/models", tags=["Data"])
async def list_models():
    """List all models in the knowledge base."""
    try:
        models = kb.get_all_models()
        return {
            "status": "success",
            "models": models,
            "total": len(models)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/stats", tags=["Data"])
async def get_stats():
    """Get knowledge base statistics."""
    try:
        stats = kb.get_stats()
        return {
            "status": "success",
            **stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler."""
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "message": "Endpoint not found",
            "docs": "/docs"
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler."""
    logger.error("Internal server error", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc) if os.getenv("API_ENV") == "development" else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
