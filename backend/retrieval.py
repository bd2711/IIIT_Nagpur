import faiss
import numpy as np
import pickle
import os
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

class RAGRetriever:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", index_path: str = "vector_index.faiss"):
        self.model = SentenceTransformer(model_name)
        self.index_path = index_path
        self.metadata_path = index_path + ".meta"
        self.dimension = 384  # For all-MiniLM-L6-v2
        
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, "rb") as f:
                self.chunks_metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.chunks_metadata = []

    def add_documents(self, chunks: List[str], doc_name: str):
        if not chunks:
            return
            
        embeddings = self.model.encode(chunks)
        self.index.add(np.array(embeddings).astype("float32"))
        
        for i, chunk in enumerate(chunks):
            self.chunks_metadata.append({
                "doc_name": doc_name,
                "content": chunk,
                "chunk_index": i
            })
            
        # Persistence
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.chunks_metadata, f)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if self.index.ntotal == 0:
            return []
            
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding).astype("float32"), top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:
                meta = self.chunks_metadata[idx]
                results.append({
                    **meta,
                    "score": float(distances[0][i])
                })
        return results
