from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

class BaseRetriever:
    def __init__(self, persist_directory: str):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_db = Chroma(
            persist_directory=persist_directory, 
            embedding_function=self.embeddings
        )

    def retrieve(self, query: str, k: int = 5, search_type: str = "similarity"):
        if search_type == "mmr":
            # MMR reduces redundancy by diversifying the retrieved chunks
            return self.vector_db.max_marginal_relevance_search(query, k=k)
        
        return self.vector_db.similarity_search(query, k=k)

if __name__ == "__main__":
    import os
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "vector_db"))
    
    retriever = BaseRetriever(db_dir)
    
    # Test Query
    query = "What is the purpose of AI RMF?"
    results = retriever.retrieve(query, search_type="mmr")
    
    for i, doc in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"Content: {doc.page_content[:200]}...")
        print(f"Metadata: {doc.metadata}")
