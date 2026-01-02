"""Pydantic schemas for data validation."""

from typing import List, Optional
from pydantic import BaseModel, HttpUrl


class TopicSource(BaseModel):
    """Source URL for a topic."""
    url: HttpUrl
    title: Optional[str] = None
    snippet: Optional[str] = None


class Topic(BaseModel):
    """Topic selected for article generation."""
    titolo: str
    angolo: str  # Editorial angle
    fonti: List[str]  # Source URLs
    keywords: List[str]


class TopicsResponse(BaseModel):
    """Response containing selected topics."""
    topics: List[Topic]


class Article(BaseModel):
    """Generated article."""
    title: str
    content: str  # HTML/Markdown content
    topic: Topic
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    word_count: int
    sources: List[TopicSource]


class GoogleDocInfo(BaseModel):
    """Information about created Google Doc."""
    doc_id: str
    doc_url: str
    title: str


class WorkflowResult(BaseModel):
    """Result of workflow execution."""
    articles: List[Article]
    docs: List[GoogleDocInfo]
    sources_monitored: int
    execution_timestamp: str
    success: bool
    error_message: Optional[str] = None

