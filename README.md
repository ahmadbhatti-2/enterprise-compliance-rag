# Enterprise Compliance RAG

Full-stack RAG project for querying enterprise compliance documents such as NIST AI RMF, NIST RMF, NIST Privacy Framework, and GenAI risk guidance.

## Backend Setup

```bash
cd backend
pip install -r requirements.txt
copy .env.example .env
```

Add your API key in `backend/.env`.

## Build Index

```bash
cd backend
python -m app.ingestion.index
```

## Run API

```bash
cd backend
uvicorn app.main:app --reload
```

## Run CLI

```bash
cd backend
python -m app.main
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
