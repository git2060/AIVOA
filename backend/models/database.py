from sqlmodel import SQLModel, Field, Column, JSON
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID, uuid4

class HCPInteraction(SQLModel, table=True):
    interaction_id: UUID = Field(default_factory=uuid4, primary_key=True)
    hcp_name: str
    interaction_type: str
    interaction_date: date

    attendees: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    topics_discussed: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    materials_shared: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    samples_distributed: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    sentiment: str
    outcomes: str

    follow_up_actions: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    raw_transcript: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
