#!/usr/bin/env python3
"""
Start script for the RAG chatbot backend server.
This script properly starts the FastAPI server with error handling.
"""

import uvicorn
import sys
import os
import logging
from pathlib import Path

def start_server():
    """
    Start the chatbot backend server using uvicorn.
    """
    try:
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        
        # Ensure the current directory is in the path so imports work
        current_dir = Path(__file__).parent.absolute()
        sys.path.insert(0, str(current_dir))
        
        # Start the server
        print("Starting AI Chatbot Backend Server...")
        print("Server will be available at: http://localhost:8000")
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # Set to False to avoid the warning
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    start_server()