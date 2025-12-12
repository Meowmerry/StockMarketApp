"""
Chat service module for AI chat integration.
Handles communication with ParlAI/blended_skill_talk model and provides fallback responses.
"""

from typing import Optional, Dict, List
from transformers import AutoTokenizer,AutoModelForCausalLM
import torch
from app.chat_prompts import (
    get_system_prompt_with_context,
    get_fallback_response,
    get_safety_filter_keywords
)
MODEL_NAME = "ProsusAI/finbert"
"""

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto"
)
pipe = pipeline(
    task="text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=128,
    return_full_text=False,
)

"""
class ChatService:
    """Service class for handling AI chat interactions"""

    def __init__(self):
        # """Initialize the chat service with ParlAI blended_skill_talk model"""
        # self.model_name = "facebook/blenderbot-400M-distill"  # ParlAI blended_skill_talk model
        self.model_name = MODEL_NAME
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.max_length = 250  # Maximum length for generation
        self.max_new_tokens=20
        # self.return_full_text=False
        self.conversation_history = []

        try:
            print(f"Loading {self.model_name} model...")
            # self.tokenizer = BlenderbotTokenizer.from_pretrained(self.model_name)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name,use_fast=True)
            # self.model = BlenderbotForConditionalGeneration.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            print(f"Model loaded successfully on {self.device}")
        except Exception as e:
            print(f"Failed to initialize ParlAI model: {e}")
            self.tokenizer = None
            self.model = None

    def is_available(self) -> bool:
        """Check if the chat service is available"""
        return self.model is not None and self.tokenizer is not None

    def _check_safety_filter(self, message: str) -> Optional[str]:
        """
        Check if message contains requests for inappropriate advice.

        Args:
            message: User's message to check

        Returns:
            Warning message if filter triggered, None otherwise
        """
        message_lower = message.lower()
        keywords = get_safety_filter_keywords()

        for keyword in keywords:
            if keyword in message_lower:
                return (
                    "I can't provide personalized investment advice or stock recommendations. "
                    "However, I'd be happy to explain stock concepts, help you understand "
                    "your portfolio, or answer educational questions about investing!"
                )

        return None

    def get_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        user_context: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Get AI response for user message.

        Args:
            user_message: The user's message
            conversation_history: Previous messages in the conversation
            user_context: User's portfolio and stock data for context

        Returns:
            Dictionary with 'response', 'success', and 'error_type' keys
        """
        # Check safety filter first
        safety_warning = self._check_safety_filter(user_message)
        if safety_warning:
            return {
                'response': safety_warning,
                'success': True,
                'error_type': None,
                'filtered': True
            }

        # Check if service is available
        if not self.is_available():
            return {
                'response': get_fallback_response('api_key'),
                'success': False,
                'error_type': 'model_not_loaded'
            }

        try:
            # Build conversation context
            context_parts = []

            # Add system context if available
            if user_context:
                system_prompt = get_system_prompt_with_context(user_context)
                context_parts.append(system_prompt)

            # Add conversation history (limit to last 5 exchanges for context)
            
            if conversation_history:
                for msg in conversation_history[-2:]:
                    prefix = "User: " if msg['role'] == 'user' else "Assistant: "
                    context_parts.append(f"{prefix}{msg['content']}")

            # Combine context with current message
            if context_parts:
                full_input = " ".join(context_parts) + f" User: {user_message}"
            else:
                full_input = user_message

            # Tokenize input
            inputs = self.tokenizer(
                [full_input],
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True
            ).to(self.device)

            # Generate response
            with torch.no_grad():
                output_ids = self.model.generate(
                    **inputs,
                    max_length=self.max_length,
                    num_beams=5,
                    early_stopping=True,
                    no_repeat_ngram_size=3,
                    temperature=0.7,
                    do_sample=True,
                    top_k=50,
                    top_p=0.95, 
                    max_new_tokens=self.max_new_tokens
                )

            # Decode response
            ai_response = self.tokenizer.decode(
                output_ids[0],
                skip_special_tokens=True
            ).strip()

            return {
                'response': ai_response,
                'success': True,
                'error_type': None,
                'filtered': False
            }

        except RuntimeError as e:
            print(f"Model runtime error: {e}")
            return {
                'response': get_fallback_response('general'),
                'success': False,
                'error_type': 'runtime_error'
            }

        except Exception as e:
            print(f"Unexpected error in chat service: {e}")
            return {
                'response': get_fallback_response('general'),
                'success': False,
                'error_type': 'unknown'
            }


# Global instance
_chat_service = None


def get_chat_service() -> ChatService:
    """Get or create the global chat service instance"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
