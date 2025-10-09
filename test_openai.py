#!/usr/bin/env python3
"""
Test script to verify OpenAI API connection
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_connection():
    """Test if OpenAI API key is valid and working"""

    print("=" * 60)
    print("OpenAI API Connection Test")
    print("=" * 60)

    # Check if API key is set
    api_key = os.environ.get('OPENAI_API_KEY')

    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("\nPlease add it to your .env file:")
        print("OPENAI_API_KEY=sk-your-actual-key-here")
        return False

    # Show masked key
    if api_key.startswith('sk-'):
        masked_key = api_key[:8] + "..." + api_key[-4:]
        print(f"✅ API Key found: {masked_key}")
    else:
        print("⚠️  API Key format looks incorrect (should start with 'sk-')")
        return False

    # Try to import OpenAI
    try:
        from openai import OpenAI
        print("✅ OpenAI library imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import OpenAI library: {e}")
        print("\nInstall it with: pip install openai")
        return False

    # Try to create client
    try:
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client created successfully")
    except Exception as e:
        print(f"❌ Failed to create OpenAI client: {e}")
        return False

    # Try to make a simple API call
    print("\n🔄 Testing API call...")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello! API is working!'"}
            ],
            max_tokens=50
        )

        ai_response = response.choices[0].message.content
        print(f"✅ API call successful!")
        print(f"\nAI Response: {ai_response}")

        # Show usage info
        print(f"\nTokens used: {response.usage.total_tokens}")
        print(f"  - Prompt: {response.usage.prompt_tokens}")
        print(f"  - Completion: {response.usage.completion_tokens}")

        return True

    except Exception as e:
        print(f"❌ API call failed: {e}")
        print("\nPossible reasons:")
        print("  1. Invalid API key")
        print("  2. API key doesn't have permission")
        print("  3. No credits/quota available")
        print("  4. Network connectivity issues")
        print("\nCheck your OpenAI dashboard: https://platform.openai.com/account/usage")
        return False

if __name__ == '__main__':
    print("\n")
    success = test_openai_connection()
    print("\n" + "=" * 60)

    if success:
        print("✅ All tests passed! Your OpenAI API is ready to use.")
        print("\nYou can now:")
        print("  1. Run your Flask app: python run.py")
        print("  2. Visit http://localhost:5001/chat")
        print("  3. Test the chatbot")
    else:
        print("❌ Tests failed. Please fix the issues above.")
        print("\nNeed help?")
        print("  - Check .env file has correct OPENAI_API_KEY")
        print("  - Verify key at: https://platform.openai.com/api-keys")
        print("  - Check usage limits: https://platform.openai.com/account/usage")

    print("=" * 60)
    print("\n")
