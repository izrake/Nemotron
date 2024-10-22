# File: app/api/routes.py

from fastapi import APIRouter, HTTPException, Query
from app.models.request_models import CompletionRequest
from app.models.response_models import CompletionResponse, CompletionChoice, ModelList, Model
from app.services.model_service import model_service
from typing import List, Optional
import time
import uuid
import traceback
import logging

router = APIRouter()

def validate_model(model: str):
    if model not in model_service.get_supported_models():
        raise HTTPException(status_code=400, detail=f"Unsupported model: {model}")

logger = logging.getLogger(__name__)

@router.post("/completions", response_model=CompletionResponse)
async def create_completion(request: CompletionRequest):
    logger.info(f"Received completion request for model: {request.model}")
    validate_model(request.model)
    
    try:
        logger.debug("Attempting to generate text...")
        generated_text = model_service.generate_text(
            request.model,
            request.prompt,
            request.max_tokens,
            request.temperature
        )
        logger.info("Text generation successful")

        return CompletionResponse(
            id=f"cmpl-{uuid.uuid4()}",
            object="text_completion",
            created=int(time.time()),
            model=request.model,
            choices=[
                CompletionChoice(
                    text=generated_text,
                    index=0,
                    logprobs=None,
                    finish_reason="length",
                )
            ],
            usage={
                "prompt_tokens": len(request.prompt.split()),
                "completion_tokens": len(generated_text.split()),
                "total_tokens": len(request.prompt.split()) + len(generated_text.split())
            }
        )
    except Exception as e:
        logger.error(f"Error during text generation: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models", response_model=ModelList)
async def list_models():
    models = model_service.get_supported_models()
    return ModelList(
        data=[Model(id=model, object="model", created=int(time.time())) for model in models],
        object="list"
    )

@router.get("/models/{model}", response_model=Model)
async def retrieve_model(model: str):
    validate_model(model)
    return Model(id=model, object="model", created=int(time.time()))
