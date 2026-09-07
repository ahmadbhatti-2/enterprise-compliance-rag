# Enterprise Compliance & Risk Intelligence Platform

> A full-stack Retrieval-Augmented Generation (RAG) platform for querying enterprise compliance, AI risk, privacy, and governance documents.

The platform combines hybrid retrieval, semantic search, BM25 keyword search, reciprocal rank fusion, cross-encoder reranking, and Gemini-powered generation to provide grounded answers with document citations.

## Knowledge Base

The current knowledge base contains trusted guidance and frameworks from:

- NIST AI Risk Management Framework (AI RMF)
- NIST AI RMF Playbook
- NIST Generative AI Risk Profile
- NIST Privacy Framework
- NIST Risk Management Framework (RMF)

## Key Features

- Hybrid retrieval using semantic search and BM25 keyword search
- Reciprocal Rank Fusion (RRF) for combining retrieval results
- Cross-encoder reranking for improved relevance
- Gemini-powered grounded answer generation
- Document and page-level citations
- Conversation memory for follow-up questions
- ChromaDB vector storage
- Local Hugging Face embeddings
- FastAPI backend
- React frontend
- Custom RAG evaluation pipeline

## System Architecture

```text
User
  |
  v
React Frontend
  |
  v
FastAPI Backend
  |
  v
RAG Pipeline
  |
  +--> Semantic Retrieval
  |
  +--> BM25 Keyword Retrieval
  |
  v
Reciprocal Rank Fusion (RRF)
  |
  v
Cross-Encoder Reranking
  |
  v
Relevant Context
  |
  v
Gemini LLM
  |
  v
Grounded Answer + Citations

## Tech Stack

### Frontend

- React
- Vite
- Tailwind CSS

### Backend

- Python
- FastAPI
- Uvicorn

### RAG & Retrieval

- LangChain
- ChromaDB
- BM25
- Reciprocal Rank Fusion (RRF)
- Cross-Encoder Reranking

### AI Models

- Gemini
- Hugging Face sentence-transformer embeddings
- Cross-encoder reranker

### Document Processing

- PyPDF
- Recursive Character Text Splitter

## Project Structure

```text
enterprise-compliance-rag/
│
├── backend/
│   ├── app/
│   │   ├── config/
│   │   │   └── settings.py
│   │   │
│   │   ├── ingestion/
│   │   │   ├── loader.py
│   │   │   ├── chunking.py
│   │   │   └── index.py
│   │   │
│   │   ├── retrieval/
│   │   │   ├── retriever.py
│   │   │   ├── hybrid.py
│   │   │   └── reranker.py
│   │   │
│   │   ├── rag/
│   │   │   ├── chain.py
│   │   │   ├── memory.py
│   │   │   └── prompts.py
│   │   │
│   │   ├── evaluation/
│   │   │   ├── dataset.json
│   │   │   └── evaluate.py
│   │   │
│   │   └── main.py
│   │
│   ├── data/
│   ├── vector_db/
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   └── package.json
│
├── .gitignore
├── docker-compose.yml
└── README.md

## Local Setup

### Prerequisites

- Python 3.10+
- Node.js and npm
- Git
- Google Gemini API key

### Backend Setup

cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env

Add your Gemini API key to `backend/.env`:

GOOGLE_API_KEY=your_api_key_here

### Build the Vector Index

python -m app.ingestion.index

### Run the Backend

uvicorn app.main:app --reload

Backend API: http://localhost:8000

Swagger documentation: http://localhost:8000/docs

### Frontend Setup

cd frontend

npm install

npm run dev

Frontend: http://localhost:5173

## API Endpoints

### Health Check

GET `/health`

Returns the current backend health status.

### Chat

POST `/api/chat`

Request:

{
  "query": "What is the purpose of the AI Risk Management Framework?"
}

The endpoint returns a generated answer along with the retrieved document sources and page references.

### Interactive API Documentation

http://localhost:8000/docs

## Evaluation

The project includes a custom RAG evaluation pipeline to measure answer and retrieval quality.

The current evaluation covers:

- Faithfulness
- Answer Relevance
- Retrieval Recall
- Citation Correctness

Run the evaluation with:

python -m app.evaluation.evaluate

The evaluation uses a curated test dataset containing questions, expected answers, and ground-truth source pages.

Example evaluation output:

Faithfulness: 100.0%
Retrieval Recall: 100.0%
Answer Relevance: 5.00/5
Citation Correctness: 100.0%

> Note: These results are based on the current evaluation dataset and should not be interpreted as a comprehensive benchmark until the test set is expanded.

### Evaluation Dataset

The evaluation dataset is located at:

`backend/app/evaluation/dataset.json`

## Limitations

- The current knowledge base is limited to the included NIST documents.
- The evaluation dataset is currently small and should be expanded for broader performance measurement.
- Conversation memory is currently maintained in-process and is not persisted across application restarts.
- ChromaDB is configured as a local vector database.
- AI-generated responses should be verified against the original source documents for high-stakes compliance decisions.

## Disclaimer

This project is intended for educational, research, and portfolio demonstration purposes.

The included NIST publications provide frameworks, guidance, and recommended practices. They should not be considered legal advice, regulatory determinations, or a replacement for official policies or authoritative legal sources.

## Future Improvements

- Expand the evaluation dataset with broader question coverage
- Add more comprehensive retrieval and generation metrics
- Improve semantic citation verification
- Add persistent user and session management
- Add authentication and role-based access control
- Add production monitoring and observability
- Support scalable external vector database deployments

## Demo

The application provides a web-based interface for interacting with the enterprise compliance knowledge base.

The demo demonstrates:

- Asking compliance and risk-related questions
- Hybrid document retrieval
- Cross-encoder reranking
- Grounded answer generation
- Source citations
- Follow-up questions
- RAG evaluation

### Screenshots

Screenshots of the application interface and evaluation results will be added here.

### Application Interface

![Application Dashboard and RAG Answer](docs/screenshots/rag-answer.png)

## Environment Variables

Create a `.env` file inside the `backend` directory and add your Gemini API key:

GOOGLE_API_KEY=your_api_key_here

Do not commit `.env` or API keys to the repository.

## License

This project is intended for educational, research, and portfolio demonstration purposes.

## Author

Ahmad Bhatti

GitHub: https://github.com/ahmadbhatti-2