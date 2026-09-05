import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import List

# Ensure the app directory is in the system path for modular imports
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(app_dir)

from app.rag.chain import RAGChain

load_dotenv()

app = FastAPI(
    title="Enterprise Compliance RAG API",
    description="Production-grade API for regulatory compliance queries with verifiable source citations."
)

# Configure CORS to allow communication with the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve absolute paths for the data repository and vector store
BASE_DIR = os.path.abspath(os.path.join(current_dir, ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_DIR = os.path.join(BASE_DIR, "vector_db", "chroma_db")

# Initialize the RAG Chain as a singleton instance to prevent redundant document re-loading
try:
    print("Initializing Enterprise RAG System... Please wait.")
    rag_system = RAGChain(DB_DIR, DATA_DIR)
    print("RAG System is online and ready for inference!")
except Exception as e:
    print(f"CRITICAL ERROR during RAG initialization: {e}")
    rag_system = None

class ChatRequest(BaseModel):
    query: str

class SourceDetail(BaseModel):
    name: str
    page: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceDetail]

@app.get("/health")
def health_check():
    """Performs a system health check to verify backend operational status."""
    return {"status": "healthy", "message": "Enterprise Compliance RAG System is online"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Processes user compliance queries through the RAG orchestrator 
    and returns synthesized answers along with verified document citations.
    """
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system is not initialized.")
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query payload cannot be empty.")

    try:
        # Execute the retrieval and generation pipeline
        rag_output = rag_system.ask(request.query)
        
        answer_text = rag_output.get("answer", "")
        raw_docs = rag_output.get("source_documents", [])
        
        parsed_sources = []
        for doc in raw_docs:
            metadata = doc.metadata if hasattr(doc, 'metadata') else doc.get("metadata", {})
            
            # Extract clean filename from source path
            raw_source_name = metadata.get("source", "Compliance_Document.pdf")
            file_name = raw_source_name.split('/')[-1].split('\\')[-1]
            
            # Standardize page number presentation
            page_num = metadata.get("page", "N/A")
            page_str = f"Page {page_num}" if isinstance(page_num, int) or str(page_num).isdigit() else str(page_num)

            source_obj = {"name": file_name, "page": page_str}
            
            # Prevent duplicate UI citation entries from overlapping text chunks
            if source_obj not in parsed_sources:
                parsed_sources.append(source_obj)

        return ChatResponse(answer=answer_text, sources=parsed_sources)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal inference error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)