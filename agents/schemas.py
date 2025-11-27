from typing import List
from pydantic import BaseModel, Field

# 1. Transcription Agent
class TranscriptionOutput(BaseModel):
    transcript: str = Field(..., description="Full transcript text")
    word_count: int = Field(..., description="Number of words")

# 2. Research Agent
class Citation(BaseModel):
    title: str
    url: str
    snippet: str

class ResearchOutput(BaseModel):
    summary: str
    bullets: List[str]
    citations: List[Citation]

# 3. Outline Agent
class OutlineSegment(BaseModel):
    title: str
    summary: str

class OutlineOutput(BaseModel):
    hook: str
    segments: List[OutlineSegment]
    closing: str

# 4. Show Notes Agent
class ShowNotesOutput(BaseModel):
    summary: str
    bullets: List[str]

# 5. Timestamp Agent
class Chapter(BaseModel):
    start: str
    title: str

class TimestampOutput(BaseModel):
    chapters: List[Chapter]

# 6. Quote Agent
class QuotesOutput(BaseModel):
    quotes: List[str]

# 7. Social Agent
class SocialOutput(BaseModel):
    twitter_thread: List[str]
    linkedin_posts: List[str]
    instagram_captions: List[str]

# 8. SEO Agent
class SEOOutput(BaseModel):
    title: str
    meta_description: str
    keywords: List[str]
