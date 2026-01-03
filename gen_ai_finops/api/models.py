"""
Pydantic Models for API Request/Response
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class OracleRequest(BaseModel):
    """Request model for Oracle queries."""
    question: str = Field(..., description="Pricing question to ask", min_length=1)
    n_results: Optional[int] = Field(5, description="Number of context results to retrieve", ge=1, le=20)


class OracleResponse(BaseModel):
    """Response model for Oracle queries."""
    status: str
    question: str
    answer: str
    context_used: Optional[int] = None


class ArchitectRequest(BaseModel):
    """Request model for cost optimization analysis."""
    use_case_description: str = Field(..., description="Description of the use case", min_length=1)
    monthly_input_tokens: int = Field(..., description="Estimated monthly input tokens", gt=0)
    monthly_output_tokens: Optional[int] = Field(None, description="Estimated monthly output tokens")
    current_model: Optional[str] = Field(None, description="Current model name (optional)")


class ModelRecommendation(BaseModel):
    """Model recommendation details."""
    model: str
    monthly_cost: str
    monthly_cost_raw: float
    reasoning: str
    action: Optional[str] = None


class AlternativeModel(BaseModel):
    """Alternative model option."""
    provider: str
    model_name: str
    monthly_cost: str
    monthly_cost_raw: float
    input_cost_per_1m: str
    output_cost_per_1m: str
    match_score: int
    reasons: List[str]
    context_window: Optional[int] = None
    supports_function_calling: Optional[bool] = None
    supports_vision: Optional[bool] = None


class SavingsDetails(BaseModel):
    """Cost savings details."""
    monthly: str
    monthly_raw: float
    annual: str
    annual_raw: float
    percentage: str


class ArchitectResponse(BaseModel):
    """Response model for cost optimization analysis."""
    status: str
    use_case: str
    requirements: Dict[str, Any]
    recommendation: ModelRecommendation
    alternatives: List[AlternativeModel]
    volume: Dict[str, int]
    current_model: Optional[Dict[str, Any]] = None
    savings: Optional[SavingsDetails] = None
    message: Optional[str] = None


class ScraperStatusResponse(BaseModel):
    """Scraper status response."""
    status: str
    total_models: int
    providers: List[str]
    last_updated: Optional[str] = None


class ScraperRunResponse(BaseModel):
    """Scraper run response."""
    status: str
    message: str
    entries_added: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    knowledge_base_status: str
    llm_available: bool


class QueryResult(BaseModel):
    """Semantic search result."""
    provider: str
    model_name: str
    input_cost: float
    output_cost: float
    context_window: Optional[int] = None
    supports_function_calling: Optional[bool] = None


class QueryResponse(BaseModel):
    """Response for semantic search."""
    status: str
    query: str
    results: List[QueryResult]
    total_results: int


class LoginRequest(BaseModel):
    """Login request model."""
    username: str = Field(..., description="Username", min_length=1)
    password: str = Field(..., description="Password", min_length=1)


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response model."""
    username: str
    authenticated: bool
