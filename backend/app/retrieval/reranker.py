import os
import sys
from sentence_transformers import CrossEncoder

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(app_dir)

from retrieval.hybrid import HybridRetriever

class DocumentReranker:
    def __init__(self):
        # Using a high-precision Cross-Encoder model for final scoring
        self.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    def rerank(self, query: str, documents):
        if not documents:
            return []

        # Create (query, document) pairs for the model to evaluate
        pairs = [[query, doc.page_content] for doc in documents]
        
        # Predict relevance scores
        scores = self.model.predict(pairs)
        
        # Sort documents by score in descending order
        scored_docs = sorted(zip(scores, documents), key=lambda x: x[0], reverse=True)
        
        return [doc for score, doc in scored_docs]

if __name__ == "__main__":
    from ingestion.loader import DocumentLoader
    from ingestion.chunking import DocumentChunker

    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "data"))
    db_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "vector_db"))

    # 1. Hybrid Retrieval (The 'Rough' Filter)
    loader = DocumentLoader(data_dir)
    docs = loader.load_pdfs()
    chunker = DocumentChunker()
    chunks = chunker.chunk_documents(docs)

    hybrid = HybridRetriever(db_dir)
    hybrid.initialize_bm25(chunks)
    
    query = "What is the purpose of AI RMF?"
    # Get a larger pool of candidates for the reranker to refine
    initial_results = hybrid.retrieve(query, k=10) 
    print(f"Hybrid Retrieval: Found {len(initial_results)} candidates.")

    # 2. Reranking (The 'Precision' Filter)
    reranker = DocumentReranker()
    final_results = reranker.rerank(query, initial_results)
    
    print("\n--- Top Reranked Results ---")
    for i, doc in enumerate(final_results[:3]):
        print(f"\nRank {i+1}:")
        print(f"Content: {doc.page_content[:200]}...")
        print(f"Metadata: {doc.metadata}")
