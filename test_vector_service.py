"""
Test script for vector_service.py
Run this to see how embeddings work before integrating with the database.
"""

from app.vector_service import VectorService
import numpy as np


def test_basic_embedding():
    """Test creating a single embedding"""
    print("=" * 60)
    print("TEST 1: Creating a single embedding")
    print("=" * 60)

    service = VectorService()

    text = "What is a P/E ratio?"
    embedding = service.create_embedding(text)

    print(f"Text: '{text}'")
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 10 values: {embedding[:10]}")
    print(f"Embedding type: {type(embedding)}")
    print()


def test_batch_embedding():
    """Test creating multiple embeddings at once"""
    print("=" * 60)
    print("TEST 2: Creating batch embeddings")
    print("=" * 60)

    service = VectorService()

    texts = [
        "What is a stock?",
        "How do I buy shares?",
        "Explain dividend yield",
        "What is market capitalization?"
    ]

    embeddings = service.create_embeddings_batch(texts)

    print(f"Created {len(embeddings)} embeddings")
    for i, (text, emb) in enumerate(zip(texts, embeddings)):
        print(f"{i+1}. '{text}' -> {len(emb)} dimensions")
    print()


def test_similarity():
    """Test semantic similarity between texts"""
    print("=" * 60)
    print("TEST 3: Testing semantic similarity")
    print("=" * 60)

    service = VectorService()

    # Create test queries
    queries = [
        "What is a P/E ratio?",
        "Explain price to earnings ratio",
        "How do I buy stocks?",
        "What is cryptocurrency?",
        "Tell me about price earnings"
    ]

    # Create embeddings
    embeddings = service.create_embeddings_batch(queries)

    # Compare first query with all others
    base_query = queries[0]
    base_embedding = np.array(embeddings[0])

    print(f"Base query: '{base_query}'")
    print("\nSimilarity to other queries:")
    print("-" * 60)

    for i, (query, emb) in enumerate(zip(queries[1:], embeddings[1:]), 1):
        emb_array = np.array(emb)

        # Calculate Euclidean distance (same as pgvector <-> operator)
        distance = np.linalg.norm(base_embedding - emb_array)

        # Calculate cosine similarity for comparison
        cosine_sim = np.dot(base_embedding, emb_array) / (
            np.linalg.norm(base_embedding) * np.linalg.norm(emb_array)
        )

        print(f"{i}. '{query}'")
        print(f"   Distance: {distance:.4f} (lower = more similar)")
        print(f"   Cosine similarity: {cosine_sim:.4f} (higher = more similar)")
        print()

    print("\nINTERPRETATION:")
    print("- Queries about P/E ratio should have LOW distance (similar)")
    print("- Unrelated queries should have HIGH distance (different)")
    print()


def test_stock_market_examples():
    """Test with stock market specific examples"""
    print("=" * 60)
    print("TEST 4: Stock market semantic search demo")
    print("=" * 60)

    service = VectorService()

    # Simulate knowledge base
    knowledge_base = [
        "P/E ratio (Price-to-Earnings) measures a stock's price relative to its earnings per share",
        "Dividend yield is calculated by dividing annual dividends by stock price",
        "Market capitalization is the total value of a company's outstanding shares",
        "Bull market refers to a period of rising stock prices",
        "Bear market is characterized by falling stock prices",
        "Diversification means spreading investments across different assets",
        "Dollar cost averaging is investing fixed amounts at regular intervals"
    ]

    # User queries
    user_queries = [
        "What is P/E ratio?",
        "How to calculate dividend yield?",
        "Explain market cap"
    ]

    print("Knowledge Base:")
    for i, doc in enumerate(knowledge_base, 1):
        print(f"{i}. {doc}")
    print()

    # Create embeddings for knowledge base
    kb_embeddings = service.create_embeddings_batch(knowledge_base)

    # Test each query
    for query in user_queries:
        print(f"\nUser Query: '{query}'")
        print("-" * 60)

        query_embedding = np.array(service.create_embedding(query))

        # Calculate distances to all knowledge base items
        distances = []
        for kb_text, kb_emb in zip(knowledge_base, kb_embeddings):
            dist = np.linalg.norm(query_embedding - np.array(kb_emb))
            distances.append((kb_text, dist))

        # Sort by distance (most similar first)
        distances.sort(key=lambda x: x[1])

        # Show top 3 results
        print("Top 3 most relevant documents:")
        for i, (text, dist) in enumerate(distances[:3], 1):
            print(f"{i}. [Distance: {dist:.3f}] {text}")
        print()


def test_embedding_dimension():
    """Show embedding dimension info"""
    print("=" * 60)
    print("TEST 5: Embedding model information")
    print("=" * 60)

    service = VectorService()

    print(f"Model: all-MiniLM-L6-v2")
    print(f"Embedding dimension: {service.get_embedding_dimension()}")
    print(f"This is the value you'll use for vector(384) in PostgreSQL")
    print()

    print("Other popular models:")
    print("- all-MiniLM-L6-v2: 384 dims (fast, good quality) ✓ Current")
    print("- all-mpnet-base-v2: 768 dims (slower, better quality)")
    print("- paraphrase-multilingual-MiniLM: 384 dims (multilingual)")
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "VECTOR SERVICE TEST SUITE" + " " * 18 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    try:
        test_basic_embedding()
        test_batch_embedding()
        test_similarity()
        test_stock_market_examples()
        test_embedding_dimension()

        print("=" * 60)
        print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Add 'embedding' column to chat_message table")
        print("2. Use vector_service in your chat routes")
        print("3. Integrate with Ollama for RAG")
        print()

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print("\nMake sure you have:")
        print("1. Installed sentence-transformers: pip install sentence-transformers")
        print("2. Internet connection (first run downloads the model)")
