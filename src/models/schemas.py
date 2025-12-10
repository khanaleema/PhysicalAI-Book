from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

# From data-model.md
class UserQuery(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str = Field(min_length=1, max_length=500)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None
    selected_text: Optional[str] = None  # For answering questions based on selected text

class SourceDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str # e.g., "TEXTBOOK", "CONSTITUTION"
    content_raw: str
    last_indexed_at: Optional[datetime] = None

class TextChunk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    text: str
    embedding: Optional[List[float]] = None # Will be populated
    source_metadata: str # e.g., page, chapter, section
    order_in_document: int

class ChatbotResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query_id: str
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    constitutional_compliance_status: str # e.g., "COMPLIANT", "FLAGGED", "NON_COMPLIANT"
    cited_sources: List[dict] # e.g., [{"document_id": "...", "source_metadata": "..."}]

class ConversationSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    start_timestamp: datetime = Field(default_factory=datetime.utcnow)
    last_activity_timestamp: datetime = Field(default_factory=datetime.utcnow)
    context: dict = {}
