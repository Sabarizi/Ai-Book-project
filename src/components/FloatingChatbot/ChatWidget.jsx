import React, { useState, useEffect } from 'react';
import ChatWindow from './ChatWindow';
import './chatbot.css';

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [hasUnreadMessage, setHasUnreadMessage] = useState(false);

  // Function to handle new messages and show unread indicator
  const handleNewMessage = (message) => {
    if (!isOpen && message.sender === 'bot') {
      setHasUnreadMessage(true);
    }
  };

  // Close unread indicator when chat is opened
  useEffect(() => {
    if (isOpen) {
      setHasUnreadMessage(false);
    }
  }, [isOpen]);

  return (
    <>
      {isOpen && (
        <ChatWindow
          onClose={() => setIsOpen(false)}
          onNewMessage={handleNewMessage}
        />
      )}
      <button
        className={`chat-float-button ${isOpen ? 'hidden' : ''} ${hasUnreadMessage ? 'unread' : ''}`}
        onClick={() => setIsOpen(true)}
        aria-label="Open chat"
      >
        {hasUnreadMessage && <span className="unread-indicator" />}
        <span className="chat-icon">💬</span>
      </button>
    </>
  );
};

export default ChatWidget;