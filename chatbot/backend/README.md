# AI Chatbot Backend

This is the backend server for the AI Chatbot system, built with Python and FastAPI. It provides a REST API endpoint for processing chat messages and returning AI-generated responses.

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Navigate to the backend directory:
```bash
cd chatbot/backend
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

### Running the Server

Start the backend server with:
```bash
uvicorn main:app --reload --port 8000
```

The server will start at `http://localhost:8000` and will automatically reload when you make changes to the code.

### API Endpoints

- `GET /` - Health check endpoint
- `GET /health` - Detailed health check
- `POST /chat` - Chat endpoint (accepts JSON: `{"message": "your message"}`)

## Usage

Once the server is running, you can test the chat endpoint:

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

## Configuration

The backend uses a simple rule-based AI response system. You can modify the `get_bot_response()` function in `main.py` to customize the bot's behavior or integrate with more advanced AI models.

## Troubleshooting

- If you encounter issues with the server not starting, ensure all dependencies are installed
- Check that port 8000 is available and not being used by another application
- Use `--reload` flag during development to automatically restart on code changes