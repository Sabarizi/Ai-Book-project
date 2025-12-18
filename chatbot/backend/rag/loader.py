"""
Module for loading Docusaurus markdown files.
"""
import os
import re
from typing import List, Dict, Any
from pathlib import Path
import frontmatter  # For parsing markdown with frontmatter


class DocusaurusLoader:
    """
    Loads Docusaurus markdown files and extracts their content with metadata.
    """
    
    def __init__(self, docs_path: str = "../../../docs"):
        self.docs_path = Path(docs_path)
        
    def load_documents(self) -> List[Dict[str, Any]]:
        """
        Load all markdown documents from the docs directory.
        
        Returns:
            List of documents with content and metadata
        """
        documents = []
        
        # Get all markdown files
        md_files = list(self.docs_path.rglob("*.md")) + list(self.docs_path.rglob("*.mdx"))
        
        for file_path in md_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse frontmatter if present
                try:
                    post = frontmatter.loads(content)
                    metadata = post.metadata
                    content = post.content
                except:
                    # If no frontmatter, create basic metadata
                    metadata = {}
                
                # Extract title from content if not in frontmatter
                if 'title' not in metadata:
                    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                    if title_match:
                        metadata['title'] = title_match.group(1)
                    else:
                        metadata['title'] = file_path.stem
                
                # Extract document structure
                doc_parts = self._extract_document_structure(content, metadata.get('title', file_path.stem))
                
                # Create document for each section
                for part in doc_parts:
                    doc = {
                        'content': part['content'],
                        'metadata': {
                            **metadata,
                            'source_file': str(file_path.relative_to(self.docs_path)),
                            'section': part['section'],
                            'chapter': self._extract_chapter_from_path(file_path),
                            'book_title': 'Physical AI & Humanoid Robotics'
                        }
                    }
                    documents.append(doc)
                    
            except Exception as e:
                print(f"Error loading file {file_path}: {e}")
                
        return documents
    
    def _extract_document_structure(self, content: str, main_title: str) -> List[Dict[str, str]]:
        """
        Extract document into semantic sections based on headings.
        """
        sections = []
        
        # Split content by headings (h2 and h3)
        lines = content.split('\n')
        current_section = {'title': main_title, 'content': '', 'level': 0}
        
        for line in lines:
            # Check for H2 headings
            h2_match = re.match(r'^##\s+(.+)$', line)
            if h2_match:
                if current_section['content'].strip():
                    sections.append({
                        'section': current_section['title'],
                        'content': current_section['content'].strip()
                    })
                
                current_section = {
                    'title': h2_match.group(1), 
                    'content': f"{h2_match.group(1)}\n", 
                    'level': 2
                }
                continue
            
            # Check for H3 headings
            h3_match = re.match(r'^###\s+(.+)$', line)
            if h3_match:
                if current_section['content'].strip():
                    sections.append({
                        'section': current_section['title'],
                        'content': current_section['content'].strip()
                    })
                
                current_section = {
                    'title': f"{current_section['title']} - {h3_match.group(1)}", 
                    'content': f"{h3_match.group(1)}\n", 
                    'level': 3
                }
                continue
            
            # Add content to current section
            current_section['content'] += f"{line}\n"
        
        # Add the last section if it has content
        if current_section['content'].strip():
            sections.append({
                'section': current_section['title'],
                'content': current_section['content'].strip()
            })
        
        return sections
    
    def _extract_chapter_from_path(self, file_path: Path) -> str:
        """
        Extract chapter/module information from file path.
        """
        # Example: docs/modules/module-01-introduction-physical-ai/...
        parts = file_path.parts
        for i, part in enumerate(parts):
            if 'module' in part.lower() and 'modules' in parts[i-1].lower():
                return part.replace('module-', 'Module ').replace('-', ' ').title()
        
        return 'General'