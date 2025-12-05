"""
Chat service module for OpenAI integration.
Handles communication with OpenAI API and provides fallback responses.
"""

import os
from typing import Optional, Dict, List
from openai import OpenAI, OpenAIError, RateLimitError, APIConnectionError
from app.chat_prompts import (
    get_system_prompt_with_context,
    get_fallback_response,
    get_safety_filter_keywords
)

class ChatService:
    """Service class for handling AI chat interactions"""

    def __init__(self):
        """Initialize the chat service with OpenAI client"""
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.client = None
        self.model = "gpt-3.5-turbo"  # Using GPT-3.5 for cost efficiency
        self.max_tokens = 500  # Limit response length
        self.temperature = 0.7  # Balance between creativity and consistency

        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
                self.client = None

    def is_available(self) -> bool:
        """Check if the chat service is available"""
        return self.client is not None and self.api_key is not None

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
                'error_type': 'api_key'
            }

        try:
            # Build messages array for OpenAI
            messages = []

            # Add system prompt with context
            system_prompt = get_system_prompt_with_context(user_context)
            messages.append({
                'role': 'system',
                'content': system_prompt
            })

            # Add conversation history (limit to last 10 messages for context window)
            if conversation_history:
                for msg in conversation_history[-10:]:
                    messages.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })

            # Add current user message
            messages.append({
                'role': 'user',
                'content': user_message
            })

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=1,
                frequency_penalty=0.5,  # Reduce repetition
                presence_penalty=0.5    # Encourage diverse responses
            )

            # Extract response
            ai_response = response.choices[0].message.content.strip()

            return {
                'response': ai_response,
                'success': True,
                'error_type': None,
                'filtered': False
            }

        except RateLimitError:
            return {
                'response': get_fallback_response('rate_limit'),
                'success': False,
                'error_type': 'rate_limit'
            }

        except APIConnectionError:
            return {
                'response': get_fallback_response('network'),
                'success': False,
                'error_type': 'network'
            }

        except OpenAIError as e:
            print(f"OpenAI API error: {e}")
            return {
                'response': get_fallback_response('general'),
                'success': False,
                'error_type': 'api_error'
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
