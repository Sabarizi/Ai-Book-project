# Floating AI Chatbot Widget

This directory contains the floating AI Chatbot widget implementation for the Docusaurus project. The widget appears as a circular chat button on the bottom-right corner of every page, which opens a chat window when clicked.

## Project Structure

```
/src/components/FloatingChatbot/
  ChatWidget.jsx     # Main floating button component
  ChatWindow.jsx     # Chat window modal component
  chatbot.css        # Styling for the chatbot
  index.js          # Export file
/src/theme/Root.js   # Global wrapper to render chatbot on all pages
.env               # Environment variables
```

## Features

- Circular floating chat button on bottom-right corner of every page
- Smooth animations and modern UI design
- Unread message indicator
- Responsive design for mobile devices
- Integration with FastAPI backend
- Environment variable configuration

## Environment Variables

The chatbot uses the following environment variables:

- `REACT_APP_API_KEY`: API key for authentication (optional)
- `REACT_APP_BACKEND_URL`: Backend API endpoint URL

These are configured in the `.env` file at the project root.

## Backend Integration

The chatbot connects to the FastAPI backend at the configured URL. The default is `http://localhost:8000/chat`.

The backend should accept POST requests with:
```json
{
  "message": "user message",
  "api_key": "optional api key"
}
```

And return:
```json
{
  "reply": "bot response"
}
```

## How to Run

### Prerequisites
- Ensure your FastAPI backend is running
- Set up the environment variables in `.env`

### Setup
1. Make sure your backend is running (e.g., `uvicorn main:app --reload --port 8000`)
2. Start Docusaurus: `npm start`
3. The floating chatbot will appear on all pages

## Styling

The chatbot uses modern CSS with:
- Smooth animations and transitions
- Gradient backgrounds
- Responsive design
- Custom scrollbar styling
- Mobile-friendly layout

The styling matches the overall theme of the Docusaurus site while remaining distinct and visually appealing.