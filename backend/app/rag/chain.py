import os
import sys
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(app_dir)

from retrieval.hybrid import HybridRetriever
from retrieval.reranker import DocumentReranker
from rag.prompts import PromptTemplates
from rag.memory import ChatMemory
from ingestion.loader import DocumentLoader
from ingestion.chunking import DocumentChunker

load_dotenv()

class RAGChain:
    """
    Core Orchestrator for the Retrieval-Augmented Generation (RAG) Pipeline.
    Integrates document ingestion, hybrid retrieval, cross-encoder reranking, 
    and the LLM generation chain with memory.
    """
    
    def __init__(self, persist_directory: str, data_path: str):
        # Enforcing deterministic outputs for strict compliance adherence
        self.llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0)
        
        self.reranker = DocumentReranker()
        self.memory = ChatMemory()
        self.hybrid_retriever = self._setup_hybrid_retriever(persist_directory, data_path)

    def _setup_hybrid_retriever(self, persist_directory, data_path):
        """Initializes the hybrid search engine (Vector + Keyword search)."""
        loader = DocumentLoader(data_path)
        docs = loader.load_pdfs()
        
        chunker = DocumentChunker()
        chunks = chunker.chunk_documents(docs)
        
        hybrid = HybridRetriever(persist_directory)
        
        # Initialize in-memory BM25 index for sparse/keyword-based retrieval
        hybrid.initialize_bm25(chunks)
        return hybrid

    def _clean_llm_response(self, response) -> str:
        """Standardizes variable response formats from the Gemini API to a clean plain string."""
        content = response.content
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and 'text' in item:
                    text_parts.append(item['text'])
                else:
                    text_parts.append(str(item))
            return " ".join(text_parts)
        return str(content)

    def _prepare_context(self, documents) -> str:
        """Compiles retrieved document chunks into a single formatted context string."""
        context_text = ""
        for doc in documents:
            source = doc.metadata.get("source_file") or doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page_label") or doc.metadata.get("page", "Unknown")
            context_text += f"\n[Source: {source}, Page: {page}]\n{doc.page_content}\n"
        return context_text

    def ask(self, query: str) -> dict:
        """
        Executes the full RAG pipeline for a given user query.
        Returns a dictionary containing the AI response and the cited source documents.
        """
        # Resolve conversational context for follow-up queries using historical memory
        history = self.memory.get_history()
        if history:
            condense_prompt = PromptTemplates.CONDENS_QUESTION_PROMPT.format(
                chat_history=history, 
                question=query
            )
            response = self.llm.invoke(condense_prompt)
            query = self._clean_llm_response(response)

        # Execute hybrid retrieval and isolate the highest-relevance chunks via cross-encoder
        initial_docs = self.hybrid_retriever.retrieve(query, k=10)
        top_docs = self.reranker.rerank(query, initial_docs)[:3]
        
        context = self._prepare_context(top_docs)
        self.last_context = context 
        
        # Synthesize the final response grounded strictly in the retrieved context
        final_prompt = PromptTemplates.SYSTEM_PROMPT.format(
            context=context, 
            question=query
        )
        
        ai_response = self.llm.invoke(final_prompt)
        answer = self._clean_llm_response(ai_response)
        
        self.memory.add_interaction(query, answer)
        
        # Construct the final payload comprising the generated answer and verifiable source citations
        return {
            "answer": answer,
            "source_documents": top_docs
        }

if __name__ == "__main__":
    # Standalone execution block for testing the ingestion and retrieval pipeline
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "vector_db/chroma_db"))
    
    rag_system = RAGChain(DB_DIR, DATA_DIR)
    
    print("\n--- AI Compliance Assistant Ready ---")
    q1 = "What is the purpose of AI RMF?"
    
    response_data = rag_system.ask(q1)
    
    print(f"\nUser: {q1}\nAI: {response_data['answer']}")
    print("\nSources Retrieved:")
    for document in response_data['source_documents']:
        file_name = document.metadata.get('source', 'Unknown')
        page_num = document.metadata.get('page', 'Unknown')
        print(f"- {file_name} (Page {page_num})")