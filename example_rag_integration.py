"""
Example: How to integrate vector_service with your Ollama chatbot (RAG pattern)

This shows the complete flow of:
1. User sends message
2. Create embedding and search for similar past messages
3. Send relevant context to Ollama
4. Get smarter, context-aware response
"""

from app.vector_service import get_vector_service
from app.chat_service import get_chat_service
from app.models import ChatMessage, db
from typing import List, Dict


def chat_with_rag(user_message: str, session_id: str, user_context: Dict = None) -> Dict:
    """
    Enhanced chat function that uses RAG (Retrieval-Augmented Generation)

    Args:
        user_message: The user's question
        session_id: Current chat session ID
        user_context: Optional user portfolio/stock data

    Returns:
        Dictionary with response and metadata
    """
    # Initialize services
    vector_service = get_vector_service()
    chat_service = get_chat_service()

    # STEP 1: Search for relevant past messages (RAG)
    print(f"\n1. Searching for relevant context...")
    relevant_messages = vector_service.search_similar_messages(
        query=user_message,
        limit=3,  # Get top 3 most relevant messages
        session_id=session_id,  # Only search this session
        distance_threshold=1.5  # Only include if reasonably similar
    )

    print(f"   Found {len(relevant_messages)} relevant messages")
    for msg in relevant_messages:
        print(f"   - [{msg['distance']:.2f}] {msg['content'][:50]}...")

    # STEP 2: Build context from relevant messages
    print(f"\n2. Building context...")
    context_text = ""
    if relevant_messages:
        context_text = "Relevant past discussion:\n"
        for msg in relevant_messages:
            role = "User" if msg['role'] == 'user' else "Assistant"
            context_text += f"{role}: {msg['content']}\n"
        context_text += "\n"

    # STEP 3: Call Ollama with enhanced context
    print(f"\n3. Calling Ollama with context...")

    # Build full prompt with RAG context
    enhanced_prompt = f"""{context_text}Current question: {user_message}

Answer based on the context above if relevant, otherwise provide a general answer."""

    # Call Ollama
    response = chat_service.get_response(
        user_message=enhanced_prompt,
        user_context=user_context
    )

    print(f"   Ollama responded (success: {response['success']})")

    # STEP 4: Save messages with embeddings
    print(f"\n4. Saving messages with embeddings...")

    # Save user message with embedding
    user_embedding = vector_service.create_embedding(user_message)
    user_msg = ChatMessage(
        content=user_message,
        role='user',
        session_id=session_id,
        embedding=user_embedding
    )
    db.session.add(user_msg)

    # Save assistant response with embedding
    if response['success']:
        assistant_embedding = vector_service.create_embedding(response['response'])
        assistant_msg = ChatMessage(
            content=response['response'],
            role='assistant',
            session_id=session_id,
            embedding=assistant_embedding
        )
        db.session.add(assistant_msg)

    db.session.commit()
    print(f"   Messages saved with embeddings")

    return {
        'response': response['response'],
        'success': response['success'],
        'context_used': len(relevant_messages) > 0,
        'relevant_messages_count': len(relevant_messages)
    }


def chat_without_rag(user_message: str, user_context: Dict = None) -> Dict:
    """
    Original chat function without RAG (for comparison)
    """
    chat_service = get_chat_service()

    response = chat_service.get_response(
        user_message=user_message,
        user_context=user_context
    )

    return response


# Example usage comparison
if __name__ == "__main__":
    print("=" * 70)
    print("RAG vs NO-RAG COMPARISON")
    print("=" * 70)

    # Simulate a conversation
    session_id = "test_session_123"

    # Conversation history (these would be in database)
    conversation = [
        {
            'message': "What is a P/E ratio?",
            'response': "P/E ratio stands for Price-to-Earnings ratio. It measures a stock's price relative to its earnings per share. It's calculated by dividing the current stock price by earnings per share."
        },
        {
            'message': "How do I calculate it?",
            'response': "To calculate P/E ratio: divide the current stock price by the earnings per share (EPS). For example, if a stock trades at $100 and has EPS of $5, the P/E ratio is 20."
        }
    ]

    print("\nCONVERSATION HISTORY:")
    print("-" * 70)
    for i, conv in enumerate(conversation, 1):
        print(f"{i}. User: {conv['message']}")
        print(f"   Bot: {conv['response'][:80]}...")
        print()

    # New question
    new_question = "What was that ratio we talked about earlier?"

    print("\nNEW QUESTION:")
    print("-" * 70)
    print(f"User: {new_question}")
    print()

    # WITHOUT RAG
    print("\n📦 WITHOUT RAG (traditional approach):")
    print("-" * 70)
    print("Context: Only last 3 messages from conversation")
    print("Problem: 'that ratio' is ambiguous without earlier context")
    print("Result: Bot might not understand which ratio")
    print()

    # WITH RAG
    print("\n🔍 WITH RAG (vector search):")
    print("-" * 70)
    print("1. Converts question to vector")
    print("2. Searches ALL past messages for similarity")
    print("3. Finds P/E ratio discussion (even from beginning)")
    print("4. Includes that context in Ollama prompt")
    print("5. Bot gives informed answer!")
    print()

    print("=" * 70)
    print("KEY INSIGHT")
    print("=" * 70)
    print("""
RAG enables semantic memory:
- Traditional: Only remembers recent messages
- RAG: Searches ALL messages for relevant context
- Result: Smarter, more consistent responses
    """)

    print("\nTO USE IN YOUR APP:")
    print("-" * 70)
    print("""
# In your chat route (routes.py)
from example_rag_integration import chat_with_rag

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    session_id = request.json['session_id']

    # Use RAG-enhanced chat instead of regular chat
    result = chat_with_rag(user_message, session_id)

    return jsonify(result)
    """)
