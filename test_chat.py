#!/usr/bin/env python3
"""
Simple test script for chat_service.py
Run this to verify your chat service is working correctly.
"""

import os
from app.chat_service import get_chat_service

def test_chat_service():
    """Test the chat service with various scenarios"""

    print("=" * 60)
    print("CHAT SERVICE TEST")
    print("=" * 60)

    # Initialize service
    chat_service = get_chat_service()

    # Check 1: Service availability
    print("\n1. Checking service availability...")
    if chat_service.is_available():
        print("   ✓ Chat service is available")
        print(f"   Model: {chat_service.model}")
    else:
        print("   ✗ Chat service is NOT available")
        print("   Note: Make sure OPENAI_API_KEY is set in your environment")
        api_key = os.environ.get('OPENAI_API_KEY')
        if api_key:
            print(f"   API Key found: {api_key[:10]}...{api_key[-4:]}")
        else:
            print("   API Key: NOT FOUND")

    # Check 2: Safety filter test
    print("\n2. Testing safety filter...")
    safety_test_messages = [
        "what stock should I buy?",
        "tell me which stocks to invest in",
        "explain what P/E ratio means"
    ]

    for msg in safety_test_messages:
        response = chat_service.get_response(msg)
        filtered = response.get('filtered', False)
        print(f"   Message: '{msg}'")
        print(f"   Filtered: {filtered}")
        if filtered:
            print(f"   Response: {response['response'][:80]}...")
        print()

    # Check 3: Basic chat test (if service is available)
    if chat_service.is_available():
        print("\n3. Testing basic chat response...")
        test_message = "What is a stock portfolio?"
        print(f"   Question: {test_message}")

        response = chat_service.get_response(test_message)

        if response['success']:
            print("   ✓ Response received successfully")
            print(f"   Response preview: {response['response'][:150]}...")
        else:
            print(f"   ✗ Error: {response['error_type']}")
            print(f"   Fallback response: {response['response'][:100]}...")

        # Check 4: Test with context
        print("\n4. Testing with user context...")
        user_context = {
            'portfolio': [
                {'symbol': 'AAPL', 'shares': 10, 'current_price': 150.0},
                {'symbol': 'GOOGL', 'shares': 5, 'current_price': 2800.0}
            ],
            'total_value': 15500.0
        }

        context_message = "What's in my portfolio?"
        print(f"   Question: {context_message}")

        response = chat_service.get_response(
            context_message,
            user_context=user_context
        )

        if response['success']:
            print("   ✓ Context-aware response received")
            print(f"   Response preview: {response['response'][:150]}...")
        else:
            print(f"   ✗ Error: {response['error_type']}")

    else:
        print("\n3-4. Skipping API tests (service not available)")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_chat_service()
