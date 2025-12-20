"""
Script to populate the stock_document table with financial knowledge.
Run this to bootstrap your RAG chatbot!
"""

from app import create_app, db
from app.vector_service import get_vector_service

def populate_and_test():
    """Populate knowledge base and test semantic search"""

    app = create_app()

    with app.app_context():
        print("=" * 70)
        print("POPULATING STOCK KNOWLEDGE BASE")
        print("=" * 70)
        print()

        # Get vector service
        vector_service = get_vector_service()

        # Populate knowledge base
        stats = vector_service.populate_stock_knowledge_base()

        print()
        print(f"✓ Added {stats['succeeded']} documents successfully")
        print(f"✗ Failed: {stats['failed']}")
        print()

        # Test semantic search
        print("=" * 70)
        print("TESTING SEMANTIC SEARCH")
        print("=" * 70)
        print()

        test_queries = [
            "What is P/E ratio?",
            "How to calculate dividend yield?",
            "Explain diversification",
            "How do I buy stocks?"
        ]

        for query in test_queries:
            print(f"\nQuery: '{query}'")
            print("-" * 70)

            results = vector_service.search_stock_documents(
                query=query,
                limit=3
            )

            if results:
                print(f"Found {len(results)} relevant documents:\n")
                for i, doc in enumerate(results, 1):
                    print(f"{i}. [{doc['doc_type']}] Distance: {doc['distance']:.3f}")
                    print(f"   {doc['content'][:100]}...")
                    print()
            else:
                print("No results found")

        print("=" * 70)
        print("✓ KNOWLEDGE BASE READY!")
        print("=" * 70)
        print()
        print("Your chatbot now has:")
        print("  • Financial definitions (P/E ratio, EPS, market cap, etc.)")
        print("  • Investment guides (diversification, dollar-cost averaging)")
        print("  • FAQs (how to buy stocks, how markets work)")
        print()
        print("Next step: Integrate with Ollama for RAG-powered responses!")
        print()

if __name__ == "__main__":
    try:
        populate_and_test()
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\nMake sure:")
        print("1. PostgreSQL is running")
        print("2. stock_document table exists with embedding column")
        print("3. Virtual environment is activated")
