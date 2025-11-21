from pydantic import BaseModel
from typing import List, Optional

# --- CHAT ---

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None


class Source(BaseModel):
    file_name: str
    citation: str


class ChatResponse(BaseModel):
    response: str
    thread_id: str
    sources: List[Source] = []


# --- DOCUMENTOS ---

class UploadResponse(BaseModel):
    filename: str
    file_id: str
    status: str