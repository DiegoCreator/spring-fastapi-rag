from typing import List
import os
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from models import DocumentChunk
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class AIService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.critical("API key missing! Service cannot start.")
            raise ValueError("API key missing in environment variables!")
        genai.configure(api_key=self.api_key)
        self.llm_model = genai.GenerativeModel("models/gemini-2.5-flash")
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.answer_cache = {}
        logger.info("AIService initialized successfully.")


    def get_embedding(self, text: str) -> List[float]:
        try:
            logger.info(f"Generating embedding for text (length: {len(text)})")
            return self.embedding_model.encode(text).tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise

    def similarity_search(self, query_embedding, db, k=3):
        results = db.query(DocumentChunk).order_by(
            DocumentChunk.embedding.cosine_distance(query_embedding)
        ).limit(k).all()

        logger.info(f"Retrieved {len(results)} documents from the database")
        return results

    def generate_answer(self, question: str, context: str, chat_history: list, semantic_history: str):
        cache_key = hash(question + context + str([m.content for m in chat_history]))

        history_lines = []
        semantic_lines = []

        for message in chat_history:
            if message.role == "user":
                history_lines.append(f"User: {message.content}")
            elif message.role == "assistant":
                history_lines.append(f"Assistant: {message.content}")

        formatted_history = "\n".join(history_lines)

        for message in semantic_history:
            semantic_lines.append(f"User (Past): {message.content}")
        formatted_semantic = "\n".join(semantic_lines)

        if cache_key in self.answer_cache:
            logger.info("Cache hit: Returning cached answer")
            return self.answer_cache[cache_key]

        logger.info("Cache miss: Generating new content via Gemini")

        prompt = f"""
        You are a helpful assistant. "Answer the user's question using the provided document context and the conversation history below.
        If the provided context doesn't answer, reply:
        "I'm sorry, but I don't have enough information to answer this question."
    
        Context:
        {context}
    
        User Question:
        {question}
        
        Semantic History:
        {formatted_semantic}
        
        Recent Conversation History:
        {formatted_history}
        """

        logger.debug(f"Prompt sent to Gemini: {prompt}")
        try:
            response = self.llm_model.generate_content(prompt)
            answer = response.text
            self.answer_cache[cache_key] = answer
            logger.info(f"Successfully generated answer. Length: {len(answer)}")
            return answer
        except Exception as e:
            logging.exception("Failed to generate content from Gemini API")
            return "An error occurred while generating the response"