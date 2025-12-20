"""
Standalone test for vector embeddings (no Flask required)
"""

from sentence_transformers import SentenceTransformer
import numpy as np


def main():
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "VECTOR SERVICE TEST SUITE" + " " * 18 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    # Initialize model
    print("Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print(f"✓ Model loaded! Dimension: {model.get_sentence_embedding_dimension()}\n")

    # TEST 1: Basic embedding
    print("=" * 60)
    print("TEST 1: Creating a single embedding")
    print("=" * 60)

    text = "What is a P/E ratio?"
    embedding = model.encode(text)

    print(f"Text: '{text}'")
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 10 values: {embedding[:10]}")
    print()

    # TEST 2: Batch embeddings
    print("=" * 60)
    print("TEST 2: Creating batch embeddings")
    print("=" * 60)

    texts = [
        "What is a stock?",
        "How do I buy shares?",
        "Explain dividend yield",
        "What is market capitalization?"
    ]

    embeddings = model.encode(texts)

    print(f"Created {len(embeddings)} embeddings")
    for i, (text, emb) in enumerate(zip(texts, embeddings)):
        print(f"{i+1}. '{text}' -> {len(emb)} dimensions")
    print()

    # TEST 3: Similarity test
    print("=" * 60)
    print("TEST 3: Testing semantic similarity")
    print("=" * 60)

    queries = [
        "What is a P/E ratio?",
        "Explain price to earnings ratio",  # Similar to first
        "How do I buy stocks?",  # Different topic
        "What is cryptocurrency?",  # Very different
        "Tell me about price earnings"  # Similar to first
    ]

    query_embeddings = model.encode(queries)
    base_embedding = query_embeddings[0]

    print(f"Base query: '{queries[0]}'")
    print("\nSimilarity to other queries:")
    print("-" * 60)

    for i, (query, emb) in enumerate(zip(queries[1:], query_embeddings[1:]), 1):
        # Calculate Euclidean distance (same as pgvector <-> operator)
        distance = np.linalg.norm(base_embedding - emb)

        # Calculate cosine similarity
        cosine_sim = np.dot(base_embedding, emb) / (
            np.linalg.norm(base_embedding) * np.linalg.norm(emb)
        )

        print(f"{i}. '{query}'")
        print(f"   Distance: {distance:.4f} (lower = more similar)")
        print(f"   Cosine similarity: {cosine_sim:.4f} (higher = more similar)")
        print()

    # TEST 4: Stock market RAG demo
    print("=" * 60)
    print("TEST 4: Stock market semantic search demo")
    print("=" * 60)

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

    print("Knowledge Base:")
    for i, doc in enumerate(knowledge_base, 1):
        print(f"{i}. {doc}")
    print()

    # Create embeddings for knowledge base
    kb_embeddings = model.encode(knowledge_base)

    # User queries
    user_queries = [
        "What is P/E ratio?",
        "How to calculate dividend yield?",
        "Explain market cap"
    ]

    for query in user_queries:
        print(f"\nUser Query: '{query}'")
        print("-" * 60)

        query_embedding = model.encode(query)

        # Calculate distances
        distances = []
        for kb_text, kb_emb in zip(knowledge_base, kb_embeddings):
            dist = np.linalg.norm(query_embedding - kb_emb)
            distances.append((kb_text, dist))

        # Sort by distance
        distances.sort(key=lambda x: x[1])

        # Show top 3
        print("Top 3 most relevant documents:")
        for i, (text, dist) in enumerate(distances[:3], 1):
            print(f"{i}. [Distance: {dist:.3f}] {text}")
        print()

    # Summary
    print("=" * 60)
    print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print()
    print("KEY INSIGHTS:")
    print("• Similar questions have LOW distance (~0.5-1.0)")
    print("• Different topics have HIGH distance (~1.5-2.5)")
    print("• This is how vector search finds relevant context!")
    print()
    print("NEXT STEPS:")
    print("1. Add 'embedding vector(384)' column to chat_message table")
    print("2. Store embeddings when users send messages")
    print("3. Search similar messages before sending to Ollama")
    print("4. Include relevant context in Ollama prompts (RAG)")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
