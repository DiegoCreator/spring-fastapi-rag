import logging
from typing import List
import os
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from models import Document
from dotenv import load_dotenv

class AIService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key: raise ValueError("API key missing in environment variables!")
        genai.configure(api_key=self.api_key)
        self.llm_model = genai.GenerativeModel("models/gemini-2.5-flash")

        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

        self.answer_cache = {}


    def get_embedding(self, text: str) -> List[float]:
        return self.embedding_model.encode(text).tolist()

    def similarity_search(self, query_embedding, db, k=3):
        results = db.query(Document).order_by(
            Document.embedding.cosine_distance(query_embedding)
        ).limit(k).all()

        return results

    def generate_answer(self, question: str, context: str):
        cache_key = hash(question + context)

        if cache_key in self.answer_cache:
            return self.answer_cache[cache_key]

        prompt = f"""
        You are a helpful assistant. Answer the user's question below using only the information (context) provided.
        If the provided context doesn't answer, reply:
        "I'm sorry, but I don't have enough information to answer this question."
    
        Context:
        {context}
    
        User Question:
        {question}
        """

        try:
            response = self.llm_model.generate_content(prompt)
            answer = response.text
            self.answer_cache[cache_key] = answer
            return answer
        except Exception as e:
            logging.error(f"Error Gemini API: {str(e)}")
            return "An error occurred while generating the response"