import os
import re
from typing import List
from pypdf import PdfReader

class DocumentIngestor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_text(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif ext == ".pdf":
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

    def chunk_text(self, text: str) -> List[str]:
        # Simple character-based chunking for hackathon purposes
        chunks = []
        text = re.sub(r'\s+', ' ', text).strip()
        
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += self.chunk_size - self.chunk_overlap
            
        return chunks

    def process_file(self, file_path: str):
        print(f"DEBUG: Processing file: {file_path}")
        text = self.extract_text(file_path)
        print(f"DEBUG: Extracted {len(text)} characters")
        chunks = self.chunk_text(text)
        print(f"DEBUG: Created {len(chunks)} chunks")
        return chunks
