# File: app/models/request_models.py

from pydantic import BaseModel
from typing import Optional

class CompletionRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: int = 16
    temperature: float = 1.0

