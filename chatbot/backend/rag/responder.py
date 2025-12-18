"""
Module for generating responses based on retrieved context.
"""
import os
from typing import List, Dict, Any, Optional
from .vector_store import SearchResult


class Responder:
    """
    Generates responses based on retrieved context and user queries.
    """
    
    def __init__(self):
        # Check which LLM provider to use
        if os.getenv("OPENAI_API_KEY"):
            try:
                import openai
                self.openai = openai
                self.openai.api_key = os.getenv("OPENAI_API_KEY")
                self.use_openai = True
            except ImportError:
                self.use_openai = False
        else:
            self.use_openai = False
    
    def generate_response(self, 
                         query: str, 
                         context: str,
                         selected_text: Optional[str] = None) -> str:
        """
        Generate a response based on the query and context.
        
        Args:
            query: The user's query
            context: Retrieved context from the vector store
            selected_text: Optional selected text for explanation/simplification
            
        Returns:
            Generated response
        """
        if selected_text:
            # If there's selected text, explain or simplify that text
            return self._explain_selected_text(selected_text, query)
        elif not context.strip():
            # If no context was found, respond appropriately
            return self._no_relevant_content_response(query)
        else:
            # Generate response based on context
            return self._generate_contextual_response(query, context)
    
    def _explain_selected_text(self, selected_text: str, query: str) -> str:
        """
        Explain or simplify the selected text based on the user's query.
        
        Args:
            selected_text: The text selected by the user
            query: The user's query about the selected text
            
        Returns:
            Explanation of the selected text
        """
        # Limit the length of the selected text for safety
        if len(selected_text) > 2000:
            selected_text = selected_text[:2000] + "... [text truncated for processing]"
        
        # Default approach: simple response based on the selected text
        if not self.use_openai:
            # If no LLM is available, return a simple response using the selected text
            action = "explain" if "explain" in query.lower() else "summarize" if "summarize" in query.lower() else "simplify"
            
            if action == "explain":
                return f"I can help explain this text from the book:\n\n{selected_text}\n\nThis text covers important concepts related to the topic you asked about."
            elif action == "summarize":
                return f"Here's a summary of the selected text:\n\n{selected_text[:200]}..."
            else:  # simplify
                return f"Here's the selected text simplified:\n\n{selected_text}"
        else:
            # If OpenAI is available, use it to explain the text
            try:
                prompt = f"""
You are an AI assistant for the book "Physical AI & Humanoid Robotics".
You must only provide information that is contained in the book.
Do not use external knowledge or make up information.

Selected Text:
{selected_text}

User Query:
{query}

Explain the selected text in simple language based only on the book content.
Focus on making the concepts easy to understand while staying accurate to the book.
If the selected text is clear and complete as is, provide context or additional explanation from the book.
"""

                response = self.openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.3  # Lower temperature for more consistent responses
                )

                response_text = response.choices[0].message.content.strip()
                return response_text
            except Exception as e:
                # Fallback if API call fails
                return f"Here's the selected text: {selected_text[:200]}... [Explanation generated without LLM due to error]"
    
    def _no_relevant_content_response(self, query: str) -> str:
        """
        Generate response when no relevant content is found.

        Args:
            query: The user's query

        Returns:
            Response indicating no relevant content
        """
        return "This information is not available in the book. The AI assistant can only provide information based on the content in this book."
    
    def _generate_contextual_response(self, query: str, context: str) -> str:
        """
        Generate response based on retrieved context.
        
        Args:
            query: The user's query
            context: Retrieved context from the vector store
            
        Returns:
            Generated response based on context
        """
        # Limit context length for API calls
        if len(context) > 3000:
            context = context[:3000] + "... [context truncated for processing]"
        
        if not self.use_openai:
            # Simple rule-based response when no LLM is available
            if context.strip():
                return f"Based on the book content, here's what I found about your query '{query}':\n\n{context[:200]}..."
            else:
                return "This information is not available in the book. The AI assistant can only provide information based on the content in this book."
        else:
            # Use OpenAI to generate response based on context
            try:
                prompt = f"""
You are an AI assistant for the book "Physical AI & Humanoid Robotics".
Answer the user's question based strictly and solely on the provided book context.
Do not use any external knowledge or make up information.
If the provided context does not contain relevant information to answer the question, respond with: "This information is not available in the book."

Book Context:
{context}

User Question: {query}

Provide a detailed answer based strictly on the book content.
If you cannot answer from the provided context, say: "This information is not available in the book."
"""

                response = self.openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.3  # Lower temperature for more consistent responses
                )

                # Double check the response to ensure it follows the rule
                response_text = response.choices[0].message.content.strip()

                # If the response indicates the information isn't in the book or is too short
                if "not available in the book" in response_text.lower() or "this information is not available in the book" in response_text.lower() or len(response_text) < 10:
                    return "This information is not available in the book."

                return response_text
            except Exception as e:
                # Fallback if API call fails
                if context.strip():
                    return f"Based on the book: {context[:150]}... [answer generated without LLM due to error]"
                else:
                    return "This information is not available in the book."
    
    def format_sources(self, results: List[SearchResult]) -> str:
        """
        Format source information for the response.
        
        Args:
            results: List of search results
            
        Returns:
            Formatted source information
        """
        if not results:
            return ""
        
        sources = []
        for result in results[:3]:  # Limit to top 3 sources
            source_file = result.metadata.get('source_file', 'Unknown')
            section = result.metadata.get('section', 'General Section')
            sources.append(f"- {section} ({source_file})")
        
        return "\n\nSources referenced: " + "\n".join(sources) if sources else ""