"""
Pydantic Models für API Request/Response
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ============================================================================
# Authentication Models
# ============================================================================

class UserLogin(BaseModel):
    """Login Request"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT Token Response"""
    access_token: str
    token_type: str = 'bearer'
    user_id: str
    school_id: str
    role: str


class UserCreate(BaseModel):
    """User Registration"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str
    last_name: str
    school_id: str


class User(BaseModel):
    """User Response"""
    user_id: str
    school_id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime


# ============================================================================
# Funding Models
# ============================================================================

class FundingOpportunity(BaseModel):
    """Fördermittel-Ausschreibung"""
    funding_id: str
    title: str
    source_url: str
    deadline: Optional[datetime]
    provider: Optional[str]
    region: Optional[str]
    funding_area: Optional[str]
    min_funding_amount: Optional[float]
    max_funding_amount: Optional[float]
    tags: Optional[List[str]]
    scraped_at: datetime
    cleaned_text: Optional[str] = None


class FundingDetail(FundingOpportunity):
    """Detaillierte Förderausschreibung (inkl. Text)"""
    cleaned_text: str  # Override to make it required
    metadata: Optional[dict]

    # Structured fields from scraper
    eligibility: Optional[List[str]] = []
    target_groups: Optional[List[str]] = []
    evaluation_criteria: Optional[List[str]] = []
    requirements: Optional[List[str]] = []
    eligible_costs: Optional[List[str]] = []
    application_process: Optional[str] = None
    contact_person: Optional[str] = None
    decision_timeline: Optional[str] = None
    funding_period: Optional[str] = None
    application_url: Optional[str] = None
    extraction_quality_score: Optional[float] = None


class FundingFilter(BaseModel):
    """Filter für Fördermittel-Suche"""
    region: Optional[str] = None
    funding_area: Optional[str] = None
    provider: Optional[str] = None
    deadline_from: Optional[datetime] = None
    deadline_to: Optional[datetime] = None
    search_query: Optional[str] = None
    limit: int = Field(50, ge=1, le=200)
    offset: int = Field(0, ge=0)


# ============================================================================
# Application Models
# ============================================================================

class ApplicationCreate(BaseModel):
    """Antrag erstellen"""
    funding_id: str
    title: str
    projektbeschreibung: str


class ApplicationUpdate(BaseModel):
    """Antrag aktualisieren"""
    title: Optional[str] = None
    projektbeschreibung: Optional[str] = None
    status: Optional[str] = None
    budget_total: Optional[float] = None
    notes: Optional[str] = None


class Application(BaseModel):
    """Antrag Response"""
    application_id: str
    school_id: str
    user_id: str
    funding_id: Optional[str]
    title: str
    status: str
    projektbeschreibung: Optional[str]
    budget_total: Optional[float]
    submission_date: Optional[datetime]
    decision_status: Optional[str]
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Draft Generation Models
# ============================================================================

class DraftGenerateRequest(BaseModel):
    """Request für KI-Antragsentwurf"""
    application_id: str
    funding_id: str
    user_query: str = Field(
        ...,
        description='Projektidee der Schule',
        min_length=5,
        max_length=5000
    )


class DraftGenerateResponse(BaseModel):
    """Response mit generiertem Entwurf"""
    draft_id: str
    application_id: str
    generated_content: str
    model_used: str
    created_at: datetime


class DraftFeedback(BaseModel):
    """User-Feedback zu generiertem Entwurf"""
    draft_id: str
    feedback: str = Field(..., pattern='^(helpful|not_helpful)$')


# ============================================================================
# School Models
# ============================================================================

class School(BaseModel):
    """Schul-Stammdaten"""
    school_id: str
    school_name: str
    school_number: Optional[str]
    address: Optional[dict]
    schultyp: Optional[str]
    schuelerzahl: Optional[int]
    traeger: Optional[str]
    contact_email: Optional[str]


# ============================================================================
# Generic Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Fehler-Response"""
    error: str
    detail: Optional[str]
    timestamp: datetime = Field(default_factory=datetime.now)


class SuccessResponse(BaseModel):
    """Success-Response"""
    message: str
    data: Optional[dict] = None
