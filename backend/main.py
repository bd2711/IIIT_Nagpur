import os
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import QueryRequest, QueryResponse, UploadResponse, SourceSnippet
from ingestion import DocumentIngestor
from retrieval import RAGRetriever
from generator import AnswerGenerator

app = FastAPI(title="Context-Aware Document QA System")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Components
ingestor = DocumentIngestor()
retriever = RAGRetriever()
generator = AnswerGenerator()

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.post("/upload", response_model=UploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    uploaded_files = []
    total_chunks = 0
    
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        try:
            chunks = ingestor.process_file(file_path)
            retriever.add_documents(chunks, file.filename)
            uploaded_files.append(file.filename)
            total_chunks += len(chunks)
        except Exception as e:
            print(f"Error processing {file.filename}: {str(e)}")
            
    return {
        "message": f"{len(uploaded_files)} files processed and indexed successfully",
        "files": uploaded_files,
        "total_chunks": total_chunks
    }

@app.get("/files")
async def list_files():
    # Helper to get unique doc names from retriever metadata
    if not hasattr(retriever, 'chunks_metadata'):
        return []
    unique_docs = list(set([m['doc_name'] for m in retriever.chunks_metadata]))
    return unique_docs

@app.post("/clear")
async def clear_index():
    global retriever
    try:
        if os.path.exists(retriever.index_path):
            os.remove(retriever.index_path)
        if os.path.exists(retriever.metadata_path):
            os.remove(retriever.metadata_path)
        # Clear uploads folder too
        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                file_path = os.path.join(UPLOAD_DIR, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')
            
        # Re-init retriever
        retriever = RAGRetriever()
        
        return {"message": "Index and uploaded files cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    relevant_chunks = retriever.retrieve(request.query, top_k=request.top_k)
    print(f"DEBUG: Query: '{request.query}'")
    
    if not relevant_chunks:
        return {
            "answer": "Information not found in provided documents.",
            "sources": [],
            "refused": True
        }

    # Debug logs for scores
    for i, chunk in enumerate(relevant_chunks):
        print(f"DEBUG: Chunk {i} Score: {chunk['score']:.4f}, Doc: {chunk['doc_name']}")

    # Strict threshold check (L2 distance: lower is better)
    if relevant_chunks[0]["score"] > 1.1:
         print( f"DEBUG: Refusal triggered. Best score {relevant_chunks[0]['score']} > 1.1")
         return {
            "answer": "Information not found in provided documents (Similarity too low).",
            "sources": [],
            "refused": True
        }

    contexts = [c["content"] for c in relevant_chunks]
    answer = generator.generate_answer(request.query, contexts)
    
    sources = [
        SourceSnippet(
            doc_name=c["doc_name"],
            content=c["content"],
            chunk_index=c["chunk_index"],
            score=c["score"]
        ) for c in relevant_chunks
    ]
    
    return {
        "answer": answer,
        "sources": sources,
        "refused": False
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
