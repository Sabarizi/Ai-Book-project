import React from 'react';
import FloatingChatbot from '../components/FloatingChatbot';

// Root component that wraps the entire application
// This ensures the floating chatbot appears on all pages
export default function Root({ children }) {
  return (
    <>
      {children}
      <FloatingChatbot />
    </>
  );
}