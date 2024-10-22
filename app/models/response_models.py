# File: app/models/response_models.py

from pydantic import BaseModel
from typing import List, Optional, Dict

class CompletionChoice(BaseModel):
    text: str
    index: int
    logprobs: Optional[Dict[str, List[float]]] = None
    finish_reason: str

class CompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[CompletionChoice]
    usage: Dict[str, int]

class Model(BaseModel):
    id: str
    object: str
    created: int

class ModelList(BaseModel):
    object: str
    data: List[Model]
