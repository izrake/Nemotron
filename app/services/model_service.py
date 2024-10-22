# File: app/services/model_service.py

from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from typing import Dict
from app.core.config import settings
from huggingface_hub import login
import os
import torch
import logging

logger = logging.getLogger(__name__)

class ModelService:
    def __init__(self):
        self.loaded_models: Dict[str, Dict] = {}
        self.hf_token = os.environ.get("HUGGINGFACE_TOKEN")
        if self.hf_token:
            login(token=self.hf_token)
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

    def load_model(self, model_name: str):
        if model_name not in self.loaded_models:
            try:
                logger.info(f"Loading model: {model_name}")
                tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=self.hf_token)
                model = AutoModelForCausalLM.from_pretrained(model_name, use_auth_token=self.hf_token).to(self.device)
                self.loaded_models[model_name] = {
                    "tokenizer": tokenizer,
                    "model": model
                }
                logger.info(f"Model {model_name} loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load model {model_name}: {str(e)}")
                raise Exception(f"Failed to load model {model_name}: {str(e)}")
        return self.loaded_models[model_name]

    def generate_text(self, model_name: str, prompt: str, max_tokens: int, temperature: float):
        logger.info(f"Generating text for model: {model_name}")
        model_data = self.load_model(model_name)
        model = model_data["model"]
        tokenizer = model_data["tokenizer"]

        try:
            logger.info("Starting text generation")
            input_ids = tokenizer.encode(prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                output = model.generate(
                    input_ids,
                    max_length=max_tokens + input_ids.shape[1],
                    num_return_sequences=1,
                    temperature=temperature,
                )
            
            generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
            logger.info("Text generation completed")
            
            # Remove the prompt from the generated text
            generated_text = generated_text[len(prompt):].strip()
            
            logger.info("Text generation successful")
            return generated_text
        except Exception as e:
            logger.error(f"Error during text generation: {str(e)}", exc_info=True)
            raise

    def get_supported_models(self):
        return settings.SUPPORTED_MODELS

model_service = ModelService()
