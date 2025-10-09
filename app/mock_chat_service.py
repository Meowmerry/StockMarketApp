"""
Mock chat service for testing without OpenAI API
Use this when you don't have OpenAI credits or want to test the UI
"""

from typing import Optional, Dict, List
import random


class MockChatService:
    """Mock service that simulates AI responses without using OpenAI"""

    def __init__(self):
        """Initialize the mock service"""
        self.responses = {
            "stocks": [
                "I can help you with stocks! Based on our database, we have technology stocks like Apple (AAPL), Microsoft (MSFT), and Google (GOOGL), as well as other sectors.",
                "Looking at available stocks, you'll find options in technology, automotive, and e-commerce sectors. What specific information would you like to know?",
            ],
            "portfolio": [
                "Your portfolio contains your stock holdings and trades. I can help you understand your positions and calculate your profit/loss.",
                "A portfolio shows all your investments in one place. Would you like me to summarize your current holdings?",
            ],
            "trading": [
                "Trading involves buying and selling stocks. A 'buy' order increases your holdings, while a 'sell' order reduces them. The difference between your purchase price and sale price determines your profit or loss.",
                "Stock trading is the process of exchanging shares. Remember, this is a demo app for educational purposes - always research before real trading!",
            ],
            "default": [
                "That's a great question! I'm here to help you learn about stocks and understand your portfolio.",
                "I can help with stock market basics, explain your portfolio, and answer questions about trading concepts.",
                "As an educational assistant, I'm here to explain stock concepts. What would you like to learn about?",
            ]
        }

    def is_available(self) -> bool:
        """Mock service is always available"""
        return True

    def get_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        user_context: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Get mock AI response for user message.

        Args:
            user_message: The user's message
            conversation_history: Previous messages (ignored in mock)
            user_context: User's portfolio and stock data

        Returns:
            Dictionary with 'response', 'success', and 'error_type' keys
        """
        message_lower = user_message.lower()

        # Determine response category
        if any(word in message_lower for word in ['stock', 'ticker', 'company', 'available']):
            category = 'stocks'
        elif any(word in message_lower for word in ['portfolio', 'holding', 'position']):
            category = 'portfolio'
        elif any(word in message_lower for word in ['trade', 'buy', 'sell', 'order']):
            category = 'trading'
        else:
            category = 'default'

        # Get random response from category
        response_text = random.choice(self.responses[category])

        # Add context if available
        if user_context and category == 'stocks':
            stocks = user_context.get('available_stocks', [])
            if stocks:
                stock_list = ", ".join([f"{s['ticker']}" for s in stocks[:5]])
                response_text += f"\n\nCurrently available: {stock_list}"
                if len(stocks) > 5:
                    response_text += f" and {len(stocks) - 5} more."

        if user_context and category == 'portfolio':
            portfolio = user_context.get('portfolio', {})
            holdings = portfolio.get('holdings', [])
            if holdings:
                response_text += f"\n\nYou currently have {len(holdings)} positions"
                total = portfolio.get('total_value', 0)
                response_text += f" worth ${total:,.2f}."

        # Add disclaimer
        response_text += "\n\n_Note: This is a simulated response. Connect a real OpenAI API key for full AI capabilities._"

        return {
            'response': response_text,
            'success': True,
            'error_type': None,
            'filtered': False,
            'mock': True  # Indicate this is a mock response
        }


# Global mock instance
_mock_chat_service = None


def get_mock_chat_service() -> MockChatService:
    """Get or create the global mock chat service instance"""
    global _mock_chat_service
    if _mock_chat_service is None:
        _mock_chat_service = MockChatService()
    return _mock_chat_service
