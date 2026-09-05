from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )

    def chunk_documents(self, documents):
        try:
            chunks = self.text_splitter.split_documents(documents)
            print(f"Successfully split {len(documents)} pages into {len(chunks)} chunks.")
            return chunks
        except Exception as e:
            print(f"Error during chunking: {str(e)}")
            return []

if __name__ == "__main__":
    from loader import DocumentLoader
    import os

    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "data"))

    loader = DocumentLoader(data_dir)
    docs = loader.load_pdfs()

    chunker = DocumentChunker(chunk_size=1000, chunk_overlap=200)
    final_chunks = chunker.chunk_documents(docs)
    
    if final_chunks:
        print(f"Example Chunk Content:\n{final_chunks[0].page_content[:200]}...")
        print(f"\nExample Chunk Metadata: {final_chunks[0].metadata}")
