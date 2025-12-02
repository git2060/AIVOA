from typing import List, Literal, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field
from uuid import UUID

class BaseSchema(BaseModel):
    model_config = {"arbitrary_types_allowed": True}


# ------------------ CORE INTERACTION LOGGING ------------------

class LogInteractionSchema(BaseSchema):
    hcp_name: str
    interaction_type: Literal["Meeting", "Call", "Email"]
    interaction_date: date

    attendees: List[str] = Field(default_factory=list)
    topics_discussed: List[str] = Field(default_factory=list)
    materials_shared: List[str] = Field(default_factory=list)
    samples_distributed: List[str] = Field(default_factory=list)

    sentiment: Literal["Positive", "Neutral", "Negative"]
    outcomes: str


class HCPInteractionCreate(LogInteractionSchema):
    pass


class HCPInteractionRead(LogInteractionSchema):
    interaction_id: UUID
    raw_transcript: Optional[str] = None
    created_at: datetime


# ------------------ TOOL SCHEMAS ------------------

class InteractionUpdateSchema(BaseSchema):
    interaction_id: UUID
    field_to_update: Literal["hcp_name", "sentiment", "outcomes"]
    new_value: str


class ScheduleTaskSchema(BaseSchema):
    task_description: str
    due_date: date
    priority: Literal["High", "Medium", "Low"] = "Medium"
    assigned_user_id: str


class ComplianceCheckSchema(BaseSchema):
    raw_text_segment: str
    material_references: List[str] = Field(default_factory=list)
    hcp_consent_verified: bool = False


class SearchQuerySchema(BaseSchema):
    query: str


# ------------------ TOOL OUTPUT SCHEMAS ------------------

class ComplianceReport(BaseSchema):
    status: Literal["Pass", "Warning", "Fail"]
    details: str
    risk_score: int = 0


class SearchResult(BaseSchema):
    summary: str
    source_documents: List[str]
