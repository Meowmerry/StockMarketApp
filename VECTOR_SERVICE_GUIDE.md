# Vector Service Guide

## What You Just Created

You now have a `vector_service.py` that handles embeddings for semantic search in your stock market chatbot.

## Files Created

1. **app/vector_service.py** - Main service for creating and searching embeddings
2. **test_vector_standalone.py** - Test script (you just ran this!)
3. **requirements.txt** - Updated with pgvector, sentence-transformers, numpy

## How It Works

### 1. Creating Embeddings

```python
from app.vector_service import get_vector_service

service = get_vector_service()

# Convert text to a 384-dimensional vector
text = "What is a P/E ratio?"
embedding = service.create_embedding(text)
# Result: [0.0159, -0.0044, -0.0515, ...] (384 numbers)
```

### 2. Searching Similar Content

```python
# Search for messages similar to user's question
results = service.search_similar_messages(
    query="What is P/E ratio?",
    limit=5,  # Get top 5 results
    distance_threshold=1.5  # Only results with distance < 1.5
)

# Results are sorted by relevance
for msg in results:
    print(f"Distance: {msg['distance']}")  # Lower = more similar
    print(f"Content: {msg['content']}")
```

### 3. Understanding Distance Scores

From the test results you saw:

| Query Pair | Distance | Meaning |
|------------|----------|---------|
| "What is P/E ratio?" vs "Explain price to earnings" | 0.963 | Very similar! |
| "What is P/E ratio?" vs "How do I buy stocks?" | 1.398 | Different topics |
| "What is P/E ratio?" vs "What is cryptocurrency?" | 1.277 | Different topics |

**Rule of thumb:**
- Distance < 1.0 = Very similar
- Distance 1.0-1.5 = Somewhat related
- Distance > 1.5 = Different topics

## Key Functions in vector_service.py

### `create_embedding(text)`
Converts a single text to vector.

```python
embedding = service.create_embedding("What is a stock?")
```

### `create_embeddings_batch(texts)`
Convert multiple texts at once (faster!).

```python
texts = ["What is P/E?", "What is dividend?"]
embeddings = service.create_embeddings_batch(texts)
```

### `search_similar_messages(query, limit, ...)`
Search database for similar messages.

```python
results = service.search_similar_messages(
    query="Tell me about dividends",
    limit=3,
    session_id="abc123",  # Optional: filter by session
    user_id=1,  # Optional: filter by user
    distance_threshold=1.5
)
```

### `embed_chat_message(message_id)`
Create embedding for a specific chat message.

```python
service.embed_chat_message(message_id=42)
```

### `embed_all_messages()`
Create embeddings for all messages in database.

```python
stats = service.embed_all_messages()
print(f"Processed {stats['succeeded']} messages")
```

## Test Results Explained

When you ran the test, you saw:

### Test 1: Basic Embedding
- Text converted to 384 numbers
- This is what gets stored in PostgreSQL

### Test 2: Batch Processing
- 4 messages embedded at once
- More efficient than one-by-one

### Test 3: Similarity Testing
- "P/E ratio" vs "price to earnings" = 0.963 distance (similar!)
- "P/E ratio" vs "buy stocks" = 1.398 distance (different)
- Lower distance = more similar content

### Test 4: Real-World Demo
When user asks "What is P/E ratio?", vector search finds:
1. P/E ratio definition (distance: 0.704) ✓ Most relevant
2. Dividend yield (distance: 1.185) - Less relevant
3. Market cap (distance: 1.254) - Even less relevant

**This is RAG in action!** The chatbot can now find relevant context automatically.

## Next Steps: Integration

### Step 1: Add Vector Column to Database

```sql
-- Run this in PostgreSQL
ALTER TABLE chat_message
ADD COLUMN embedding vector(384);

-- Add index for fast search
CREATE INDEX ON chat_message
USING hnsw (embedding vector_cosine_ops);
```

### Step 2: Update Your Chat Routes

When user sends a message, create embedding:

```python
from app.vector_service import get_vector_service

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']

    # Create embedding
    vector_service = get_vector_service()
    embedding = vector_service.create_embedding(user_message)

    # Save to database with embedding
    new_message = ChatMessage(
        content=user_message,
        role='user',
        session_id=session_id,
        # This line stores the vector:
        embedding=embedding
    )
    db.session.add(new_message)
    db.session.commit()
```

### Step 3: Use RAG with Ollama

Before calling Ollama, search for relevant context:

```python
from app.vector_service import get_vector_service
from app.chat_service import get_chat_service

# 1. Search for relevant past messages
vector_service = get_vector_service()
relevant_messages = vector_service.search_similar_messages(
    query=user_message,
    limit=3
)

# 2. Build context from relevant messages
context = "\n".join([
    f"{msg['role']}: {msg['content']}"
    for msg in relevant_messages
])

# 3. Send to Ollama with context
chat_service = get_chat_service()
prompt = f"""Relevant past discussions:
{context}

User: {user_message}
Assistant:"""

response = chat_service.get_response(prompt)
```

## Benefits of Vector Search

### Before (Without Vectors)
- Only use last 3 messages from history
- Miss relevant information from earlier conversations
- No semantic understanding

### After (With Vectors)
- Search ALL messages for relevant content
- Find similar questions even with different wording
- Smarter context-aware responses

## Example Scenario

**User Conversation:**
1. Day 1: "What is a P/E ratio?" → Bot explains
2. Day 2: "How about dividend yield?" → Bot explains
3. Day 3: "Tell me more about price earnings"

**Without vectors:** Bot doesn't remember Day 1 explanation

**With vectors:**
- Searches database with "price earnings" query
- Finds Day 1 message (low distance!)
- Includes that context in Ollama prompt
- Bot gives consistent, informed answer

## Model Information

**Current model:** `all-MiniLM-L6-v2`
- Dimension: 384
- Speed: Fast
- Quality: Good
- Size: ~90MB

**Other options:**
- `all-mpnet-base-v2` (768 dims, better quality, slower)
- `paraphrase-multilingual-MiniLM-L12-v2` (multilingual)

## Common Issues

### "Module not found: sentence_transformers"
```bash
source venv/bin/activate
pip install sentence-transformers
```

### "No column named embedding"
You need to add the vector column to chat_message table first.

### "Distance always high"
Check that embeddings are being created correctly. Run test script to verify.

## Resources

- pgvector: https://github.com/pgvector/pgvector
- sentence-transformers: https://www.sbert.net/
- Your test script: `test_vector_standalone.py`

## Summary

You now have:
- ✅ Vector service installed and tested
- ✅ Embedding model working (384 dimensions)
- ✅ Understanding of how similarity search works
- ✅ Ready to integrate with your chatbot

Next: Add vector column to database and integrate with Ollama!
