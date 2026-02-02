#Gemini AI service module for generating therapeutic responses
import logging
import time
from typing import List, Optional
from dataclasses import dataclass

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from flask import current_app

from app.models.room import Room
from app.services.prompt_templates import (
    THERAPIST_SYSTEM_PROMPT,
    WELCOME_MESSAGE,
    get_crisis_response

)
from app.utils.conversation_formatter import (
    format_conversation_history,
    merge_consecutive_user_messages,
    estimate_token_count
)
Logger = logging.getLogger(__name__)

@dataclass
class GeminiResponse:
    #Struct of Gemini repsonse
    content : str 
    success : bool
    error_message : Optional[str] = None
    error_type : Optional[str] = None
    token_count : Optional[int] = None

class GeminiService:
    """Service to interact with Gemini AI for therapeutic responses."""

    _instance = None
    _model = None
    _last_call_time = 0

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GeminiService, cls).__new__(cls)
        return cls._instance
    
    def initialize_gemini_client(self, api_key: Optional[str] = None) -> bool:
        """Initialize the Gemini AI client with API key and model."""
        try:
            key = api_key or  current_app.config['GEMINI_API_KEY']
            if not key: 
                Logger.error("Gemini API key is not configured.")
                return False
            genai.configure(api_key= key)

            self._model = genai.GenerativeModel(
                model_name = current_app.config.get('GEMINI_MODEL', 'gemini-1.5-flash'),
                system_instruction = THERAPIST_SYSTEM_PROMPT,
                generation_config = {
                    "max_output_tokens": current_app.config.get('GEMINI_MAX_TOKENS', 1024),
                 "temperature": current_app.config.get('GEMINI_TEMPERATURE', 0.7),
                }
            
            )
            Logger.info("Gemini AI client initialized successfully.")
            return True
        except Exception as e:
            Logger.error(f"Failed to initialize Gemini AI client: {e}")
            return False 
    
    def _enforce_rate_limit(self):
        """Enforce  the rate limit between api calls."""
        rate_limit_delay = current_app.config.get('GEMINI_RATE_LIMIT_DELAY', 1.0)
        elapsed = time.time() - self._last_call_time
        if  elapsed < rate_limit_delay:
            time.sleep(rate_limit_delay - elapsed)
        self._last_call_time = time.time()
        
    def get_welcome_message(self) -> str:
        """Return the welcome message."""
        return WELCOME_MESSAGE
    
    def generate_response(self, room: Room) -> GeminiResponse:
        """Generate a therapeutic response using Gemini AI based on room conversation."""
        if self._model is None:
            initialized = self.initialize_gemini_client()
            if not initialized:
                return GeminiResponse(
                    content="Hello,  I am unable to assist you at the moment. Please try again later.",
                    success=False,
                    error_type="InitializationError"
                )
        
        try:
            self._enforce_rate_limit()

            max_context_window = current_app.config.get('GEMINI_CONTEXT_WINDOW', 50)
            formatted_history = format_conversation_history(
                room.messages,
                max_messages=max_context_window,
                include_summary=True
            )
            merged_history = merge_consecutive_user_messages(formatted_history)

            if not merged_history:
                return GeminiResponse(
                    content=WELCOME_MESSAGE, success=True)
            
            chat = self._model.start_chat(history=merged_history[:-1] if len(merged_history) > 1 else [])
            last_message = merged_history[-1]["parts"][0]["text"]
            response = chat.send_message(last_message)
            

            token_count = estimate_token_count(room.messages)

            return GeminiResponse(
                content=response.text,
                success=True,
                token_count=token_count
            )
        except google_exceptions.GoogleAPICallError as api_err:
            Logger.error(f"Google API call error: {api_err}")
            return GeminiResponse(
                content="I'm taking a moment to reflect. Please continue sharing.",

                success=False,
                error_message=str(api_err),
                error_type="GoogleAPICallError"
            )
        except Exception as e:
            Logger.error(f"Unexpected error during Gemini response generation: {e}")
            return GeminiResponse(
                content="I'm experiencing a brief technical issue. Please continue sharing.",
                success=False,
                error_message=str(e),
                error_type="UnexpectedError"
            )
        

gemini_service = GeminiService()