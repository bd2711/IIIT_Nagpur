from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3
    threshold: float = 1.5

class SourceSnippet(BaseModel):
    doc_name: str
    content: str
    chunk_index: int
    score: float

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceSnippet]
    refused: bool = False

class UploadResponse(BaseModel):
    message: str
    files: List[str]
    total_chunks: int
