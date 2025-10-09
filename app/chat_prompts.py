"""
Chat prompts and templates for the StockBot AI assistant.
This module contains system prompts, templates, and helper functions
for generating context-aware responses.
"""

# Base system prompt for StockBot
SYSTEM_PROMPT = """You are StockBot, an educational assistant for a stock trading demo application.

Your role is to:
- Explain stock market concepts, terminology, and trading basics
- Help users understand their portfolio and trades
- Answer questions about stocks in the database
- Provide educational information about investing

You must NOT:
- Give personalized investment advice or recommendations
- Predict stock prices or market movements
- Recommend specific stocks to buy or sell
- Provide financial planning or tax advice

Always remind users that this is a demo application for educational purposes only.
If asked for investment advice, politely decline and suggest consulting a licensed financial advisor.

Be friendly, concise, and educational in your responses."""


def get_system_prompt_with_context(user_context: dict = None) -> str:
    """
    Generate a system prompt with optional user context.

    Args:
        user_context: Dictionary containing user data like portfolio, recent trades, etc.

    Returns:
        Complete system prompt with context injected
    """
    context_parts = [SYSTEM_PROMPT]

    if user_context:
        context_parts.append("\n\n--- User Context ---")

        # Add portfolio information
        if 'portfolio' in user_context and user_context['portfolio']:
            portfolio = user_context['portfolio']
            context_parts.append(f"\nUser's Portfolio Summary:")
            context_parts.append(f"- Total Portfolio Value: ${portfolio.get('total_value', 0):,.2f}")
            context_parts.append(f"- Number of Holdings: {portfolio.get('holdings_count', 0)}")

            if portfolio.get('holdings'):
                context_parts.append("\nCurrent Holdings:")
                for holding in portfolio['holdings'][:5]:  # Limit to 5 holdings
                    context_parts.append(
                        f"  • {holding['ticker']}: {holding['quantity']} shares @ ${holding['avg_price']:.2f} "
                        f"(Current: ${holding['current_price']:.2f})"
                    )

        # Add available stocks context
        if 'available_stocks' in user_context and user_context['available_stocks']:
            stocks = user_context['available_stocks']
            context_parts.append(f"\n\nAvailable Stocks in Database ({len(stocks)} total):")
            for stock in stocks[:10]:  # Limit to 10 stocks
                context_parts.append(
                    f"  • {stock['ticker']} - {stock['name']} (${stock['price']:.2f}) - {stock['sector']}"
                )

        # Add recent trades context
        if 'recent_trades' in user_context and user_context['recent_trades']:
            trades = user_context['recent_trades']
            context_parts.append(f"\n\nUser's Recent Trades ({len(trades)} total):")
            for trade in trades[:5]:  # Limit to 5 trades
                context_parts.append(
                    f"  • {trade['side'].upper()} {trade['quantity']} {trade['ticker']} @ ${trade['price']:.2f} "
                    f"on {trade['timestamp']}"
                )

    return "\n".join(context_parts)


def get_fallback_response(error_type: str = "general") -> str:
    """
    Get a fallback response when OpenAI API is unavailable.

    Args:
        error_type: Type of error ('api_key', 'rate_limit', 'network', 'general')

    Returns:
        User-friendly fallback message
    """
    fallback_messages = {
        "api_key": (
            "I'm sorry, but the AI chatbot is not configured properly. "
            "Please contact the administrator to set up the OpenAI API key."
        ),
        "rate_limit": (
            "I'm currently experiencing high demand. Please try again in a few moments."
        ),
        "network": (
            "I'm having trouble connecting to the AI service. Please check your internet connection and try again."
        ),
        "general": (
            "I'm sorry, but I'm having trouble processing your request right now. "
            "Please try again later or contact support if the issue persists."
        )
    }

    return fallback_messages.get(error_type, fallback_messages["general"])


# Example prompts for common questions
EXAMPLE_PROMPTS = [
    "What stocks are available in the app?",
    "Explain what a stock portfolio is",
    "How do I interpret my portfolio performance?",
    "What's the difference between buying and selling stocks?",
    "Can you summarize my current holdings?",
]


def get_safety_filter_keywords() -> list:
    """
    Returns keywords that might indicate requests for inappropriate advice.
    Used for additional safety filtering before sending to AI.
    """
    return [
        "should i buy",
        "should i sell",
        "is it a good time",
        "what stock should",
        "recommend a stock",
        "best stock to buy",
        "guarantee",
        "sure thing",
        "can't lose",
    ]
