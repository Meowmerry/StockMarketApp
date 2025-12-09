"""
Chat service module using Ollama for local LLM inference.
Provides high-quality responses using models like Llama 3.2.
"""

from typing import Optional, Dict, List
import requests
from app.chat_prompts import (
    get_system_prompt_with_context,
    get_fallback_response,
    get_safety_filter_keywords
)

OLLAMA_API_URL = "http://localhost:11434/api/generate" # Direct HTTP API calls to Ollama server
MODEL_NAME = "llama3.2"  # Can be changed to other models like "mistral", "phi", etc.


class ChatService:
    """Service class for handling AI chat interactions using Ollama"""

    def __init__(self):
        self.model_name = MODEL_NAME
        self.api_url = OLLAMA_API_URL
        print(f"Initializing Ollama chat service with model: {self.model_name}")

    def is_available(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

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
        Get AI response for user message using Ollama.

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
                'filtered': True,
                'mock': False
            }

        # Check if service is available
        if not self.is_available():
            return {
                'response': get_fallback_response('api_key'),
                'success': False,
                'error_type': 'model_not_loaded',
                'mock': True
            }

        try:
            # Build system prompt
            system_context = ""
            if user_context:
                system_context = get_system_prompt_with_context(user_context) + "\n\n"

            # Build conversation history
            conversation_text = ""
            if conversation_history:
                for msg in conversation_history[-3:]:  # Last 3 exchanges
                    role = "User" if msg['role'] == 'user' else "Assistant"
                    conversation_text += f"{role}: {msg['content']}\n"

            # Create full prompt
            full_prompt = f"""{system_context}You are a helpful AI assistant specializing in stock market education. Answer questions about stocks, investing, and portfolio management in a clear, educational way. Do not provide personalized investment advice or stock recommendations.

{conversation_text}User: {user_message}
Assistant:"""

            # Call Ollama API
            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 200,  # Max tokens to generate
                }
            }

            response = requests.post(
                self.api_url,
                json=payload,
                timeout=30  # 30 second timeout
            )

            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '').strip()

                if not ai_response:
                    raise Exception("Empty response from model")

                return {
                    'response': ai_response,
                    'success': True,
                    'error_type': None,
                    'filtered': False,
                    'mock': False
                }
            else:
                raise Exception(f"Ollama API error: {response.status_code}")

        except requests.exceptions.Timeout:
            print("Ollama request timeout")
            return {
                'response': get_fallback_response('general'),
                'success': False,
                'error_type': 'timeout',
                'mock': True
            }

        except Exception as e:
            print(f"Unexpected error in Ollama chat service: {e}")
            return {
                'response': get_fallback_response('general'),
                'success': False,
                'error_type': 'unknown',
                'mock': True
            }


# Global instance
_chat_service = None


def get_chat_service() -> ChatService:
    """Get or create the global chat service instance"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
