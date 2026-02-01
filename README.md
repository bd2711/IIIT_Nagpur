# Context-Aware Document QA System (RAG)

A hackathon-grade prototype for answering questions strictly based on uploaded documents using a Retrieval-Augmented Generation (RAG) pipeline.

## 🚀 Features
- **Strict Grounding**: Answers only using provided context.
- **Refusal Logic**: Refuses to answer if info is not found (similarity threshold).
- **Explainability**: Shows source document names and specific snippets used.
- **Local First**: Uses `sentence-transformers` and `FAISS` for local embeddings and retrieval.
- **Fallback Mode**: Works with mock generation if no OpenAI API key is provided.

## 🛠️ Prerequisites
- Python 3.9+
- Node.js 18+
- [Optional] OpenAI API Key (set in `backend/.env`)

## 📦 Setup & Run

### 1. Backend
1. Navigate to `backend/`
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `venv\Scripts\activate` (Windows)
4. Install requirements: `pip install -r requirements.txt`
5. (Optional) Create `.env` with `OPENAI_API_KEY=your_key`
6. Run server: `python main.py`

### 2. Frontend
1. Navigate to `frontend/`
2. Install dependencies: `npm install`
3. Run development server: `npm run dev`

## 🧪 Example Questions
- **Positive**: "What is the main topic of this document?"
- **Refusal**: "What is the capital of France?" (if not mentioned in doc)

## 📁 Structure
- `backend/`: FastAPI server, ingestion, retrieval, and generation logic.
- `frontend/`: React + Vite application.
- `sample_docs/`: Placeholder for your test documents.
