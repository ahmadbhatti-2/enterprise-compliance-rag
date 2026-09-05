import os
from langchain_community.document_loaders import PyPDFLoader

class DocumentLoader:
    def __init__(self, data_path: str):
        self.data_path = data_path

    def load_pdfs(self):
        all_docs = []
        
        # Verify if path exists to avoid crash
        if not os.path.exists(self.data_path):
            print(f"Error: The path {self.data_path} does not exist.")
            return []

        pdf_files = [f for f in os.listdir(self.data_path) if f.endswith('.pdf')]
        
        if not pdf_files:
            print("No PDF files found in the data directory.")
            return []

        for pdf in pdf_files:
            file_path = os.path.join(self.data_path, pdf)
            try:
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                
                for doc in docs:
                    doc.metadata["source_file"] = pdf
                
                all_docs.extend(docs)
                print(f"Loaded: {pdf}")
            except Exception as e:
                print(f"Failed to load {pdf}: {str(e)}")
        
        return all_docs

if __name__ == "__main__":
    # DYNAMIC PATH CALCULATION:
    # 1. Get the directory where loader.py is located
    current_dir = os.path.dirname(os.path.abspath(__file__)) 
    # 2. Go up two levels (ingestion -> app -> backend) and then into 'data'
    data_dir = os.path.join(current_dir, "..", "..", "data")
    
    # Convert to absolute path for clarity
    data_dir = os.path.abspath(data_dir)
    
    print(f"Searching for PDFs in: {data_dir}")
    
    loader = DocumentLoader(data_dir)
    loaded_data = loader.load_pdfs()
    print(f"\nTotal pages loaded: {len(loaded_data)}")
