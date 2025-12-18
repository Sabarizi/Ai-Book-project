# AI Chatbot System

This directory contains the AI Chatbot System for the Docusaurus book project. It consists of a Python FastAPI backend and a React frontend component integrated into Docusaurus.

## Project Structure

```
/chatbot/
  /backend/                 # Python FastAPI backend
    main.py                 # Main application file
    requirements.txt        # Python dependencies
    README.md              # Backend documentation
/src/components/Chatbot/    # React frontend component
  Chatbot.jsx              # Main chatbot component
  chatbot.css              # Component styling
```

## Running the System

### Backend (Python FastAPI)

1. Navigate to the backend directory:
```bash
cd chatbot/backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the backend server:
```bash
uvicorn main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`

### Frontend (Docusaurus)

1. From the project root, start Docusaurus:
```bash
npm start
```

The Docusaurus site will be available at `http://localhost:3000`

## End-to-End Testing

1. Start the backend server (port 8000)
2. Start Docusaurus (port 3000)
3. Navigate to the homepage in your browser
4. Use the chatbot interface at the bottom of the page
5. Type a message and see the AI response

## API Endpoint

The backend provides a single POST endpoint:
- `POST /chat` - Accepts JSON: `{"message": "your message"}`
- Returns JSON: `{"reply": "AI response"}`

## Configuration

The frontend connects to `http://localhost:8000/chat` by default. To change this, modify the URL in `/src/components/Chatbot/Chatbot.jsx`.

## Features

- Rule-based AI responses focused on robotics and AI topics
- Responsive chat interface with message bubbles
- Typing indicators for better UX
- Error handling for network issues
- Clean, modern styling that fits with Docusaurus theme