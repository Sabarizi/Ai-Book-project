"""
Module for handling authentication for the chatbot.
"""
import os
from typing import Optional
import secrets


class Authentication:
    """
    Handles authentication for the chatbot API.
    """
    
    def __init__(self):
        # Get the expected API key from environment
        self.expected_api_key = os.getenv("CHATBOT_API_KEY")
        # If no API key is set in environment, generate a temporary one for development
        if not self.expected_api_key:
            self.expected_api_key = secrets.token_urlsafe(32)
            print(f"Generated temporary API key: {self.expected_api_key}")
            print("Set CHATBOT_API_KEY environment variable to use a permanent key")
    
    def is_authenticated(self, provided_api_key: Optional[str]) -> bool:
        """
        Check if the provided API key is valid.
        
        Args:
            provided_api_key: API key provided by the client
            
        Returns:
            True if authenticated, False otherwise
        """
        if not self.expected_api_key:
            # If no expected key is set, authentication is disabled
            return True
        
        if not provided_api_key:
            return False
        
        # Use secrets.compare_digest for timing-attack-resistant comparison
        return secrets.compare_digest(provided_api_key, self.expected_api_key)
    
    def get_auth_required_message(self) -> str:
        """
        Get the message to return when authentication is required.
        
        Returns:
            Authentication required message
        """
        return "Please authenticate to access the book assistant."