# Quick Start: Your RAG System is Ready! ✅

## What You Have Now

### ✅ Database Setup
- **stock_document table** with `embedding vector(384)` column
- **24 documents** populated with financial knowledge:
  - 12 definitions (P/E ratio, EPS, market cap, dividends, etc.)
  - 6 guides (diversification, dollar-cost averaging, value investing)
  - 6 FAQs (how to buy stocks, how markets work, etc.)

### ✅ Vector Service
- **[app/vector_service.py](app/vector_service.py)** - Fully functional
- **[app/models.py](app/models.py)** - StockDocument model added
- **Semantic search working** - Finding relevant documents with ~0.6 distance scores!

### ✅ Test Results
```
Query: 'What is P/E ratio?'
Found: P/E ratio definition (distance: 0.638) ✓

Query: 'How to calculate dividend yield?'
Found: Dividend yield definition (distance: 0.697) ✓

Query: 'Explain diversification'
Found: Diversification guide (distance: 0.562) ✓

Query: 'How do I buy stocks?'
Found: Stock buying FAQ (distance: 0.569) ✓
```

## How to Use It

### 1. Search for Relevant Documents

```python
from app.vector_service import get_vector_service

vector_service = get_vector_service()

# Search knowledge base
results = vector_service.search_stock_documents(
    query="What is a P/E ratio?",
    limit=3
)

for doc in results:
    print(f"[{doc['distance']:.2f}] {doc['content']}")
```

### 2. Integrate with Ollama (RAG Pattern)

Update your [chat_service.py](app/chat_service.py):

```python
from app.vector_service import get_vector_service

def get_response_with_rag(user_message: str):
    # 1. Search for relevant knowledge
    vector_service = get_vector_service()
    relevant_docs = vector_service.search_stock_documents(
        query=user_message,
        limit=3,
        distance_threshold=1.5
    )

    # 2. Build context from relevant documents
    context = ""
    if relevant_docs:
        context = "Relevant information:\n"
        for doc in relevant_docs:
            context += f"- {doc['content']}\n"
        context += "\n"

    # 3. Send to Ollama with context
    prompt = f"""{context}User question: {user_message}

Answer based on the information above:"""

    # Call Ollama
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3.2", "prompt": prompt}
    )

    return response.json()['response']
```

### 3. Add More Documents

```python
from app.vector_service import get_vector_service

vector_service = get_vector_service()

# Add stock-specific information
vector_service.add_stock_document(
    content="Apple Inc. (AAPL) is a technology company...",
    doc_type="stock_info",
    stock_id=1  # Link to Stock model
)

# Add news
vector_service.add_stock_document(
    content="Stock market reached new highs today...",
    doc_type="news"
)

# Add custom FAQ
vector_service.add_stock_document(
    content="What is the difference between stocks and bonds?...",
    doc_type="faq"
)
```

## Key Functions

### `search_stock_documents(query, limit, doc_type, stock_id)`
Search for documents semantically similar to query.

### `add_stock_document(content, doc_type, stock_id)`
Add a new document with automatic embedding.

### `populate_stock_knowledge_base()`
Bootstrap with 12 financial knowledge documents (already done!).

## Files You Can Use

1. **[populate_knowledge_base.py](populate_knowledge_base.py)** - Already ran, added 24 docs
2. **[test_vector_standalone.py](test_vector_standalone.py)** - Test embeddings without database
3. **[example_rag_integration.py](example_rag_integration.py)** - Example integration with chat
4. **[VECTOR_SERVICE_GUIDE.md](VECTOR_SERVICE_GUIDE.md)** - Full documentation

## Current Database State

```sql
-- View all documents
SELECT id, doc_type, LEFT(content, 50) as preview
FROM stock_document
ORDER BY doc_type, id;

-- Count by type
SELECT doc_type, COUNT(*)
FROM stock_document
GROUP BY doc_type;

-- Search similar (raw SQL)
SELECT content, embedding <-> '[your_vector]'::vector AS distance
FROM stock_document
ORDER BY distance
LIMIT 5;
```

## What Makes This RAG?

**R**etrieval - Search stock_document for relevant content
**A**ugmented - Add that content to Ollama prompt
**G**eneration - Ollama generates informed response

**Before RAG:**
```
User: "What is P/E ratio?"
Ollama: [Generic answer from training data]
```

**With RAG:**
```
User: "What is P/E ratio?"
→ Search finds: "P/E ratio measures stock price relative to EPS..."
→ Ollama gets this as context
Ollama: [Specific answer based on your knowledge base] ✓
```

## Next Steps

### Option 1: Test RAG with Ollama
Integrate `search_stock_documents()` into your chat routes.

### Option 2: Add More Documents
Populate with:
- Stock-specific analysis for each ticker
- Company news and reports
- User portfolio insights
- Custom educational content

### Option 3: Add Chat Message Embeddings
Store embeddings for `chat_message` table to enable conversation memory:

```sql
ALTER TABLE chat_message ADD COLUMN embedding vector(384);
```

Then use `search_similar_messages()` to find relevant past conversations.

## Performance Notes

- **Distance < 0.7** = Very relevant (like the P/E ratio search)
- **Distance 0.7-1.0** = Relevant
- **Distance 1.0-1.5** = Somewhat related
- **Distance > 1.5** = Not very relevant

Your search threshold is set to 1.5, which is good for most cases.

## Troubleshooting

### No results found
- Lower the `distance_threshold` (default: 1.5)
- Check if embeddings exist: `SELECT COUNT(*) FROM stock_document WHERE embedding IS NOT NULL;`

### Slow queries
- Add an index: `CREATE INDEX ON stock_document USING hnsw (embedding vector_cosine_ops);`

### Want to reset?
```sql
DELETE FROM stock_document;
```
Then run `python populate_knowledge_base.py` again.

---

**Your RAG system is ready to use!** 🚀

The embedding in stock_document is already populated and working perfectly.
