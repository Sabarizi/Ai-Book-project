/**
 * Text Selection Handler for Book Content
 * Detects text selection on book pages and sends to the chatbot
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
  // Debounce function to prevent multiple rapid calls
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // Function to get selected text
  function getSelectedText() {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
      const range = selection.getRangeAt(0);
      const selectedText = selection.toString().trim();

      // Only proceed if text is selected and it's from the book content area
      if (selectedText.length > 0) {
        // Check if the selection is within book content (main content areas)
        // Need to get the element from the range's common ancestor container
        let containerElement = range.commonAncestorContainer;

        // If it's a text node, get its parent element
        if (containerElement.nodeType === Node.TEXT_NODE) {
          containerElement = containerElement.parentNode;
        }

        // Check if this element or any of its ancestors match our content selectors
        if (containerElement.closest &&
            (containerElement.closest('.markdown') ||
             containerElement.closest('.container') ||
             containerElement.closest('article') ||
             containerElement.closest('.main-wrapper') ||
             containerElement.closest('main') ||
             containerElement.closest('.docContent') ||
             containerElement.closest('[class*="docItem"]'))) {
          return selectedText;
        }
      }
    }
    return null;
  }

  // Function to send selected text to chatbot (via custom event)
  function sendToChatbot(selectedText) {
    // Create a custom event to communicate with the chatbot
    const event = new CustomEvent('bookTextSelected', {
      detail: {
        text: selectedText,
        timestamp: Date.now()
      }
    });
    
    document.dispatchEvent(event);
  }

  // Debounced handler for mouseup event
  const handleMouseUp = debounce(function() {
    const selectedText = getSelectedText();
    
    if (selectedText && selectedText.length > 0) {
      console.log('Selected text detected:', selectedText.substring(0, 100) + (selectedText.length > 100 ? '...' : ''));
      sendToChatbot(selectedText);
    }
  }, 300); // 300ms delay to allow selection to complete

  // Add event listeners
  document.addEventListener('mouseup', handleMouseUp);
  
  // Also add double-click handler for easier activation
  document.addEventListener('dblclick', function() {
    const selectedText = getSelectedText();
    
    if (selectedText && selectedText.length > 0) {
      console.log('Double-clicked text selection detected:', selectedText.substring(0, 100) + (selectedText.length > 100 ? '...' : ''));
      sendToChatbot(selectedText);
    }
  });

  // Listen for when floating chatbot becomes available and handle the text
  window.addEventListener('floatingChatReady', function(e) {
    console.log('Floating chat is ready, registering text selection handler');
  });

  console.log('Text selection handler initialized for book content');
});

// Export function for potential reuse elsewhere
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    getSelectedText: function() {
      const selection = window.getSelection();
      return selection.toString().trim();
    }
  };
}