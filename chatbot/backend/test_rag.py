"""
Test script to verify the RAG functionality.
"""
import requests
import json
import os
from pathlib import Path

def test_rag_functionality():
    """
    Test the RAG functionality by making requests to the backend.
    """
    base_url = "http://localhost:8000"
    
    print("Testing RAG functionality...")
    
    # Test 1: Query about book content
    print("\n1. Testing query about book content...")
    response = requests.post(
        f"{base_url}/chat",
        json={
            "message": "What is Physical AI?",
            "api_key": os.getenv("CHATBOT_API_KEY")  # Use the API key if set
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['reply']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
    # Test 2: Test selected text explanation
    print("\n2. Testing selected text explanation...")
    selected_text = """
    Physical AI represents a paradigm shift from traditional artificial intelligence approaches that operate in abstract, digital spaces to systems that exist and interact within the physical world. Unlike classical AI systems that process data in isolation, Physical AI systems are inherently embodied, meaning they must perceive, reason, and act within the constraints and opportunities of the physical environment.
    """
    
    response = requests.post(
        f"{base_url}/chat",
        json={
            "message": "Can you explain this?",
            "selected_text": selected_text,
            "api_key": os.getenv("CHATBOT_API_KEY")
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Explanation: {result['reply']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
    # Test 3: Test authentication requirement
    print("\n3. Testing authentication requirement...")
    response = requests.post(
        f"{base_url}/chat",
        json={
            "message": "What is Physical AI?",
            "api_key": "invalid_key"  # Use wrong API key
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Response with invalid key: {result['reply']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
    # Test 4: Test without API key
    print("\n4. Testing without API key...")
    response = requests.post(
        f"{base_url}/chat",
        json={
            "message": "What is Physical AI?",
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Response without API key: {result['reply']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
    print("\nTesting completed!")

if __name__ == "__main__":
    test_rag_functionality()