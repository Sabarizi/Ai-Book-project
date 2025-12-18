from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
import asyncio

from rag import RAGSystem

app = FastAPI(title="AI Chatbot Backend", version="1.0.0")

# Initialize RAG system with correct docs path
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
docs_path = os.path.join(current_dir, "..", "..", "docs")
book_embeddings_path = os.path.join(current_dir, "book_embeddings.pkl")

# Initialize RAG system to use the existing embeddings file
rag_system = RAGSystem(docs_path=docs_path)
rag_system.vector_store.storage_path = book_embeddings_path

# Load embeddings on startup (this will load from book_embeddings.pkl if it exists)
rag_system.load_and_embed_documents()

# Define the request and response models
class ChatRequest(BaseModel):
    message: str
    selected_text: Optional[str] = None  # For text selection explanation
    api_key: Optional[str] = None  # For authentication

class ChatResponse(BaseModel):
    reply: str

def get_bot_response(user_message: str, selected_text: Optional[str] = None, api_key: Optional[str] = None) -> str:
    """
    RAG-based AI response generator.
    Uses book content to answer questions or explains selected text.
    """
    try:
        # Use the RAG system to generate response
        result = rag_system.query(
            user_query=user_message,
            selected_text=selected_text,
            api_key=api_key
        )

        # Return the reply from the RAG system
        return result["reply"]
    except Exception as e:
        # Log the error for debugging
        print(f"Error in get_bot_response: {str(e)}")
        return "I'm sorry, I encountered an error processing your request. Please try again."

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint that processes user messages and returns AI responses.
    """
    try:
        bot_reply = get_bot_response(
            user_message=request.message,
            selected_text=request.selected_text,
            api_key=request.api_key
        )
        return ChatResponse(reply=bot_reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/")
async def health_check():
    """
    Health check endpoint to verify the server is running.
    """
    return {"status": "healthy", "message": "Chatbot backend is running"}

@app.get("/health")
async def detailed_health():
    """
    Detailed health check endpoint.
    """
    return {
        "status": "ok",
        "service": "chatbot-backend",
        "version": "1.0.0",
        "endpoints": ["/", "/health", "/chat"]
    }

# For local development and testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)