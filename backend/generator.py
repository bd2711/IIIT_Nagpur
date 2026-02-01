import os
import openai
from dotenv import load_dotenv
from typing import List

load_dotenv()

from transformers import pipeline

class AnswerGenerator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        else:
            # Load a small, modern, local Generative model (SmolLM-Instruct)
            # This uses 'text-generation' which is available in your transformers install
            print("DEBUG: Loading local Instruct model (SmolLM-135M)...")
            self.local_qa = pipeline("text-generation", model="HuggingFaceTB/SmolLM-135M-Instruct")

    def generate_answer(self, query: str, contexts: List[str]) -> str:
        if not contexts:
            return "Information not found in provided documents"

        context_text = "\n\n".join(contexts)
        
        if self.api_key:
            # OpenAI Logic
            prompt = f"Context: {context_text}\n\nQuestion: {query}\n\nAnswer:"
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                return f"Error using OpenAI: {str(e)}. Falling back to local model."

        # LOGIC FOR LOCAL FREE GENERATIVE MODEL (SmolLM)
        try:
            # Stricter prompt for better grounding
            prompt = f"""Use ONLY the following context to answer the question. 
If the information is not in the context, your answer MUST be: "Information not found in provided documents".

Context: 
{context_text}

Question: 
{query}

Answer:"""
            
            # Generate answer
            result = self.local_qa(prompt, max_new_tokens=128, do_sample=False)
            full_text = result[0]['generated_text']
            
            # Extract only the answer part
            if "Answer:" in full_text:
                answer = full_text.split("Answer:")[-1].strip()
            else:
                answer = full_text[len(prompt):].strip()

            if not answer or len(answer) < 5:
                 return "Information not found in provided documents"
                
            return f"[Local AI Answer]: {answer}"
        except Exception as e:
            return f"Error with local model: {str(e)}"
