"""
Vector service for handling embeddings and semantic search.
Uses sentence-transformers for creating embeddings and pgvector for storage.
"""

from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer # type: ignore
from app.models import ChatMessage, StockDocument, db
import numpy as np # type: ignore


class VectorService:
    """Service for creating and searching vector embeddings"""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the vector service with an embedding model.

        Args:
            model_name: Name of the sentence-transformers model to use.
                       Default 'all-MiniLM-L6-v2' creates 384-dimensional vectors.
                       Other options:
                       - 'all-mpnet-base-v2' (768 dims, better quality, slower)
                       - 'paraphrase-multilingual-MiniLM-L12-v2' (multilingual)
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"Embedding model loaded. Dimension: {self.embedding_dim}")

    def create_embedding(self, text: str) -> List[float]:
        """
        Create a vector embedding for the given text.

        Args:
            text: The text to embed

        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Create embedding
        embedding = self.model.encode(text, convert_to_numpy=True)

        # Convert to list for database storage
        return embedding.tolist()

    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for multiple texts at once (more efficient).

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # Batch encoding is more efficient
        embeddings = self.model.encode(texts, convert_to_numpy=True)

        return [emb.tolist() for emb in embeddings]

    def search_similar_messages(
        self,
        query: str,
        limit: int = 5,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None,
        distance_threshold: float = 1.5
    ) -> List[Dict]:
        """
        Search for messages similar to the query using vector similarity.

        Args:
            query: The search query text
            limit: Maximum number of results to return
            session_id: Optional filter by session_id
            user_id: Optional filter by user_id
            distance_threshold: Maximum distance to include (lower = more similar)
                               0 = identical, higher = less similar
                               Typical range: 0.0 to 2.0

        Returns:
            List of dictionaries with message content and similarity scores
        """
        # Create embedding for the query
        query_embedding = self.create_embedding(query)

        # Build the base query
        # Cast the parameter to vector type to avoid type mismatch
        sql_query = """
            SELECT
                id,
                content,
                role,
                session_id,
                user_id,
                timestamp,
                embedding <-> CAST(:query_embedding AS vector) AS distance
            FROM chat_message
            WHERE embedding IS NOT NULL
        """

        params = {'query_embedding': query_embedding}

        # Add optional filters
        if session_id:
            sql_query += " AND session_id = :session_id"
            params['session_id'] = session_id

        if user_id:
            sql_query += " AND user_id = :user_id"
            params['user_id'] = user_id

        # Add distance threshold and ordering
        sql_query += """
            AND embedding <-> CAST(:query_embedding AS vector) < :threshold
            ORDER BY distance
            LIMIT :limit
        """
        params['threshold'] = distance_threshold
        params['limit'] = limit

        # Execute query
        result = db.session.execute(db.text(sql_query), params)

        # Format results
        messages = []
        for row in result:
            messages.append({
                'id': row.id,
                'content': row.content,
                'role': row.role,
                'session_id': row.session_id,
                'user_id': row.user_id,
                'timestamp': row.timestamp,
                'distance': float(row.distance),
                'similarity_score': 1 - (float(row.distance) / 2)  # Convert to 0-1 score
            })

        return messages

    def embed_chat_message(self, message_id: int) -> bool:
        """
        Create and store embedding for a specific chat message.

        Args:
            message_id: ID of the chat message to embed

        Returns:
            True if successful, False otherwise
        """
        message = ChatMessage.query.get(message_id)
        if not message:
            print(f"Message {message_id} not found")
            return False

        try:
            # Create embedding
            embedding = self.create_embedding(message.content)

            # Store in database
            # Note: This assumes chat_message table has an 'embedding' column
            db.session.execute(
                db.text("UPDATE chat_message SET embedding = :embedding WHERE id = :id"),
                {'embedding': embedding, 'id': message_id}
            )
            db.session.commit()

            print(f"Created embedding for message {message_id}")
            return True

        except Exception as e:
            print(f"Error creating embedding for message {message_id}: {e}")
            db.session.rollback()
            return False

    def embed_all_messages(self, batch_size: int = 100) -> Dict[str, int]:
        """
        Create embeddings for all chat messages that don't have one yet.
        Processes in batches for efficiency.

        Args:
            batch_size: Number of messages to process at once

        Returns:
            Dictionary with statistics (processed, succeeded, failed)
        """
        # Find messages without embeddings
        messages = ChatMessage.query.filter(
            ChatMessage.content.isnot(None)
        ).all()

        stats = {
            'total': len(messages),
            'processed': 0,
            'succeeded': 0,
            'failed': 0
        }

        print(f"Found {stats['total']} messages to process")

        # Process in batches
        for i in range(0, len(messages), batch_size):
            batch = messages[i:i + batch_size]

            try:
                # Create embeddings for batch
                texts = [msg.content for msg in batch]
                embeddings = self.create_embeddings_batch(texts)

                # Update database
                for msg, embedding in zip(batch, embeddings):
                    try:
                        db.session.execute(
                            db.text("UPDATE chat_message SET embedding = :embedding WHERE id = :id"),
                            {'embedding': embedding, 'id': msg.id}
                        )
                        stats['succeeded'] += 1
                    except Exception as e:
                        print(f"Error updating message {msg.id}: {e}")
                        stats['failed'] += 1

                db.session.commit()
                stats['processed'] += len(batch)

                print(f"Processed {stats['processed']}/{stats['total']} messages")

            except Exception as e:
                print(f"Error processing batch: {e}")
                db.session.rollback()
                stats['failed'] += len(batch)

        print(f"Embedding complete: {stats}")
        return stats

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model"""
        return self.embedding_dim

    def add_stock_document(
        self,
        content: str,
        doc_type: str,
        stock_id: Optional[int] = None
    ) -> Optional[int]:
        """
        Add a document to the stock_document table with embedding.

        Args:
            content: The document content
            doc_type: Type of document ('faq', 'stock_info', 'news', 'guide', 'definition')
            stock_id: Optional stock ID to associate with

        Returns:
            The ID of the created document, or None if failed
        """
        try:
            # Create embedding
            embedding = self.create_embedding(content)

            # Create document
            doc = StockDocument(
                content=content,
                embedding=embedding,
                doc_type=doc_type,
                stock_id=stock_id
            )

            db.session.add(doc)
            db.session.commit()

            print(f"Created stock document {doc.id} (type: {doc_type})")
            return doc.id

        except Exception as e:
            print(f"Error creating stock document: {e}")
            db.session.rollback()
            return None

    def search_stock_documents(
        self,
        query: str,
        limit: int = 5,
        doc_type: Optional[str] = None,
        stock_id: Optional[int] = None,
        distance_threshold: float = 1.5
    ) -> List[Dict]:
        """
        Search for stock documents similar to the query.

        Args:
            query: The search query text
            limit: Maximum number of results to return
            doc_type: Optional filter by document type
            stock_id: Optional filter by stock_id
            distance_threshold: Maximum distance to include

        Returns:
            List of dictionaries with document content and similarity scores
        """
        # Create embedding for the query
        query_embedding = self.create_embedding(query)

        # Build the base query
        # Cast the parameter to vector type to avoid type mismatch
        sql_query = """
            SELECT
                id,
                content,
                doc_type,
                stock_id,
                created_at,
                embedding <-> CAST(:query_embedding AS vector) AS distance
            FROM stock_document
            WHERE embedding IS NOT NULL
        """

        params = {'query_embedding': query_embedding}

        # Add optional filters
        if doc_type:
            sql_query += " AND doc_type = :doc_type"
            params['doc_type'] = doc_type

        if stock_id:
            sql_query += " AND stock_id = :stock_id"
            params['stock_id'] = stock_id

        # Add distance threshold and ordering
        sql_query += """
            AND embedding <-> CAST(:query_embedding AS vector) < :threshold
            ORDER BY distance
            LIMIT :limit
        """
        params['threshold'] = distance_threshold
        params['limit'] = limit

        # Execute query
        result = db.session.execute(db.text(sql_query), params)

        # Format results
        documents = []
        for row in result:
            documents.append({
                'id': row.id,
                'content': row.content,
                'doc_type': row.doc_type,
                'stock_id': row.stock_id,
                'created_at': row.created_at,
                'distance': float(row.distance),
                'similarity_score': 1 - (float(row.distance) / 2)
            })

        return documents

    def populate_stock_knowledge_base(self) -> Dict[str, int]:
        """
        Populate the stock_document table with basic financial knowledge.
        Great for bootstrapping your RAG system!

        Returns:
            Dictionary with statistics
        """
        knowledge_base = [
            # Financial definitions
            {
                'content': 'P/E ratio (Price-to-Earnings ratio) measures a stock\'s price relative to its earnings per share. It is calculated by dividing the current stock price by the earnings per share (EPS). A higher P/E ratio suggests investors expect higher growth.',
                'doc_type': 'definition'
            },
            {
                'content': 'Dividend yield is the annual dividend payment divided by the stock price, expressed as a percentage. It shows how much cash flow you get for each dollar invested in a stock.',
                'doc_type': 'definition'
            },
            {
                'content': 'Market capitalization (market cap) is the total value of a company\'s outstanding shares. It is calculated by multiplying the stock price by the number of shares outstanding.',
                'doc_type': 'definition'
            },
            {
                'content': 'EPS (Earnings Per Share) is a company\'s profit divided by the number of outstanding shares. It indicates how much money a company makes for each share of its stock.',
                'doc_type': 'definition'
            },
            {
                'content': 'A bull market is a market condition where prices are rising or are expected to rise. It is characterized by optimism, investor confidence, and expectations of strong results.',
                'doc_type': 'definition'
            },
            {
                'content': 'A bear market is a market condition where prices are falling or are expected to fall. It is typically defined as a decline of 20% or more from recent highs.',
                'doc_type': 'definition'
            },
            # Investment strategies
            {
                'content': 'Diversification is an investment strategy that spreads investments across different assets, sectors, or geographic regions to reduce risk. The goal is to not put all your eggs in one basket.',
                'doc_type': 'guide'
            },
            {
                'content': 'Dollar-cost averaging is an investment strategy where you invest a fixed amount of money at regular intervals, regardless of the stock price. This reduces the impact of volatility.',
                'doc_type': 'guide'
            },
            {
                'content': 'Value investing is a strategy of buying stocks that appear to be trading for less than their intrinsic value. Investors look for stocks with low P/E ratios and strong fundamentals.',
                'doc_type': 'guide'
            },
            # FAQs
            {
                'content': 'To buy stocks, you need to open a brokerage account, fund it with money, research stocks, and place buy orders through your broker\'s platform.',
                'doc_type': 'faq'
            },
            {
                'content': 'The stock market operates through exchanges where buyers and sellers meet to trade stocks. Prices are determined by supply and demand.',
                'doc_type': 'faq'
            },
            {
                'content': 'A good P/E ratio depends on the industry, but generally a P/E between 15-25 is considered reasonable for most stocks. Compare a stock\'s P/E to its industry average.',
                'doc_type': 'faq'
            }
        ]

        stats = {
            'total': len(knowledge_base),
            'succeeded': 0,
            'failed': 0
        }

        print(f"Populating knowledge base with {stats['total']} documents...")

        for doc_data in knowledge_base:
            doc_id = self.add_stock_document(
                content=doc_data['content'],
                doc_type=doc_data['doc_type']
            )

            if doc_id:
                stats['succeeded'] += 1
            else:
                stats['failed'] += 1

        print(f"Knowledge base population complete: {stats}")
        return stats


# Global instance
_vector_service = None


def get_vector_service() -> VectorService:
    """Get or create the global vector service instance"""
    global _vector_service
    if _vector_service is None:
        _vector_service = VectorService()
    return _vector_service


# Example usage and testing
if __name__ == "__main__":
    # Test the vector service
    service = VectorService()

    # Test single embedding
    text = "What is a P/E ratio?"
    embedding = service.create_embedding(text)
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")

    # Test similarity
    text1 = "What is a P/E ratio?"
    text2 = "Explain price to earnings ratio"
    text3 = "How do I buy stocks?"

    emb1 = np.array(service.create_embedding(text1))
    emb2 = np.array(service.create_embedding(text2))
    emb3 = np.array(service.create_embedding(text3))

    # Calculate cosine distance
    dist_similar = np.linalg.norm(emb1 - emb2)
    dist_different = np.linalg.norm(emb1 - emb3)

    print(f"\nSimilarity test:")
    print(f"'{text1}' vs '{text2}': distance = {dist_similar:.3f}")
    print(f"'{text1}' vs '{text3}': distance = {dist_different:.3f}")
    print("(Lower distance = more similar)")
