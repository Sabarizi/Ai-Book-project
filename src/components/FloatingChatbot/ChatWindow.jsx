import React, { useState, useRef, useEffect } from 'react';
import './chatbot.css';

const ChatWindow = ({ onClose, onNewMessage }) => {
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! I'm your AI assistant. How can I help you today?", sender: 'bot' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input when chat window opens
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  // Add event listener for text selection from book pages
  useEffect(() => {
    const handleBookTextSelected = (event) => {
      const { text } = event.detail;
      if (text && text.trim()) {
        // Send the selected text to the chatbot as if the user typed it
        sendMessage(text);
      }
    };

    document.addEventListener('bookTextSelected', handleBookTextSelected);

    // Clean up the event listener
    return () => {
      document.removeEventListener('bookTextSelected', handleBookTextSelected);
    };
  }, []);

  // Function to send message to backend
  const sendMessage = async (selectedText = null) => {
    if ((!inputValue.trim() && !selectedText) || isLoading) return;

    const userMessage = selectedText || inputValue.trim();
    const userMessageObj = {
      id: Date.now(),
      text: userMessage,
      sender: 'user'
    };

    // Add user message to chat
    setMessages(prev => [...prev, userMessageObj]);
    if (!selectedText) {
      setInputValue(''); // Only clear input if not triggered by text selection
    }
    setIsLoading(true);

    try {
      // Get API key and backend URL from environment
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000/chat';
      const apiKey = process.env.REACT_APP_API_KEY || '';

      // Send message to backend
      const response = await fetch(backendUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          selected_text: selectedText ? userMessage : null,  // Only send selected_text when it's from text selection
          api_key: apiKey
        }),
      });

      if (!response.ok) {
        // Handle specific error codes
        if (response.status === 500) {
          throw new Error(`Server error: ${response.status}`);
        } else if (response.status === 404) {
          throw new Error('Backend server not found. Make sure the backend is running on http://localhost:8000');
        } else {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      }

      const data = await response.json();

      // Add bot response to chat
      const botMessageObj = {
        id: Date.now() + 1,
        text: data.reply,
        sender: 'bot'
      };

      setMessages(prev => [...prev, botMessageObj]);
      onNewMessage(botMessageObj); // Notify parent of new message
    } catch (error) {
      console.error('Error sending message:', error);

      // Check if it's a network error
      let errorMessage = "Sorry, I encountered an error. Please try again.";
      if (error.message.includes('fetch') || error.message.includes('network')) {
        errorMessage = "Cannot connect to the backend server. Please make sure the backend is running on http://localhost:8000";
      } else if (error.message.includes('500')) {
        errorMessage = "The server encountered an error. Please check the backend logs.";
      } else if (error.message.includes('404')) {
        errorMessage = "Cannot connect to the backend server. Please check if it's running on http://localhost:8000";
      }

      // Add error message to chat
      const errorMessageObj = {
        id: Date.now() + 1,
        text: errorMessage,
        sender: 'bot'
      };

      setMessages(prev => [...prev, errorMessageObj]);
      onNewMessage(errorMessageObj); // Notify parent of new message
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="fixed-chat-window">
      <div className="chat-header">
        <div className="chat-title">AI Assistant 🤖</div>
        <button className="close-button" onClick={onClose} aria-label="Close chat">
          ×
        </button>
      </div>

      <div className="chat-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.sender}-message`}
          >
            <div className="message-content">
              {message.text}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message bot-message">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <textarea
          ref={inputRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          disabled={isLoading}
          rows={1}
        />
        <button
          onClick={sendMessage}
          disabled={!inputValue.trim() || isLoading}
          className="send-button"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatWindow;