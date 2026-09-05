import os
import sys
from rank_bm25 import BM25Okapi

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(app_dir)

from retrieval.retriever import BaseRetriever

class HybridRetriever:
    def __init__(self, persist_directory: str):
        self.base_retriever = BaseRetriever(persist_directory)
        self.bm25 = None
        self.all_docs = []

    def initialize_bm25(self, chunks):
        self.all_docs = chunks
        tokenized_corpus = [doc.page_content.split(" ") for doc in chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def retrieve(self, query: str, k: int = 5):
        # 1. Semantic Search Results
        semantic_results = self.base_retriever.retrieve(query, k=k*2, search_type="mmr")
        
        # 2. Keyword Search Results
        tokenized_query = query.split(" ")
        bm25_results = self.bm25.get_top_n(tokenized_query, self.all_docs, n=k*2)
        
        # 3. Reciprocal Rank Fusion (RRF)
        # RRF combines rankings from different search methods to find the most consistent results
        reranked_scores = {}
        
        # Process Semantic Ranks
        for rank, doc in enumerate(semantic_results):
            content = doc.page_content
            reranked_scores[content] = reranked_scores.get(content, 0) + 1 / (60 + rank + 1)
            
        # Process BM25 Ranks
        for rank, doc in enumerate(bm25_results):
            content = doc.page_content
            reranked_scores[content] = reranked_scores.get(content, 0) + 1 / (60 + rank + 1)
            
        # Sort documents by their RRF score
        sorted_contents = sorted(reranked_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Map content back to original document objects
        final_results = []
        for content, score in sorted_contents:
            # Find the document object that matches this content
            doc = next(d for d in self.all_docs if d.page_content == content)
            final_results.append(doc)
            
        return final_results[:k]

if __name__ == "__main__":
    from ingestion.loader import DocumentLoader
    from ingestion.chunking import DocumentChunker

    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "data"))
    db_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "vector_db"))

    loader = DocumentLoader(data_dir)
    docs = loader.load_pdfs()
    chunker = DocumentChunker()
    chunks = chunker.chunk_documents(docs)

    hybrid = HybridRetriever(db_dir)
    hybrid.initialize_bm25(chunks)

    query = "NIST AI 100-1"
    results = hybrid.retrieve(query)
    
    for i, doc in enumerate(results):
        print(f"\nHybrid (RRF) Result {i+1}:")
        print(f"Content: {doc.page_content[:200]}...")
        print(f"Metadata: {doc.metadata}")
