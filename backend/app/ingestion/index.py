import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

class VectorIndexer:
    def __init__(self, persist_directory: str):
        self.persist_directory = persist_directory
        # Using a high-performance local model; no API calls required
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def create_index(self, chunks):
        try:
            vector_db = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            print(f"Successfully indexed {len(chunks)} chunks to {self.persist_directory}")
            return vector_db
        except Exception as e:
            print(f"Indexing error: {str(e)}")
            return None

if __name__ == "__main__":
    from loader import DocumentLoader
    from chunking import DocumentChunker
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "data"))
    db_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "vector_db"))

    loader = DocumentLoader(data_dir)
    docs = loader.load_pdfs()

    chunker = DocumentChunker()
    chunks = chunker.chunk_documents(docs)

    indexer = VectorIndexer(db_dir)
    indexer.create_index(chunks)
