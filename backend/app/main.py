import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Ensure the app directory is in the system path for modular imports
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(app_dir)

from app.rag.chain import RAGChain

load_dotenv()

app = FastAPI(title="Enterprise Compliance RAG API")

# Configure CORS to allow communication with the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve absolute paths for the data and vector store
BASE_DIR = os.path.abspath(os.path.join(current_dir, ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_DIR = os.path.join(BASE_DIR, "vector_db", "chroma_db")

# Initialize the RAG Chain as a singleton to avoid re-loading documents on every request
try:
    print("Initializing RAG System... Please wait.")
    rag_system = RAGChain(DB_DIR, DATA_DIR)
    print("RAG System is online and ready!")
except Exception as e:
    print(f"CRITICAL ERROR during initialization: {e}")
    rag_system = None

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "RAG System is online"}

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system is not initialized")
    try:
        # Execute the retrieval and generation pipeline
        answer = rag_system.ask(request.question)
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
