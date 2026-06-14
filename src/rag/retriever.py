"""
Retriever module for RAG system.
Searches FAISS index and returns relevant context for agent queries.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import numpy as np

from src.rag.vectorizer import DocumentVectorizer

logger = logging.getLogger(__name__)


class KnowledgeRetriever:
    """
    Retrieves relevant documents from knowledge base based on query similarity.
    Uses FAISS index for efficient semantic search.
    """
    
    def __init__(
        self,
        index_name: str = "knowledge_index",
        index_dir: str = "knowledge/indices",
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize retriever with FAISS index.
        
        Args:
            index_name: Name of FAISS index to load
            index_dir: Directory containing indices
            model_name: Sentence-transformers model for embedding queries
        """
        self.index_name = index_name
        self.index_dir = Path(index_dir)
        self.vectorizer = DocumentVectorizer(model_name=model_name, index_dir=str(index_dir))
        self.index = None
        self.documents = []
        self.document_ids = []
        
        logger.debug(f"KnowledgeRetriever initialized (index: {index_name})")
    
    def load_index(self) -> bool:
        """
        Load FAISS index and metadata.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.index = self.vectorizer.load_index(self.index_name)
            self.documents = self.vectorizer.documents
            self.document_ids = self.vectorizer.document_ids
            
            logger.info(f"Loaded index with {len(self.documents)} documents")
            return True
        except FileNotFoundError:
            logger.warning(f"Index not found: {self.index_name}")
            return False
    
    def ensure_index_loaded(self):
        """Ensure index is loaded, raise if not available."""
        if self.index is None:
            if not self.load_index():
                raise RuntimeError(f"Could not load index: {self.index_name}")
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        distance_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top-k most similar documents to query.
        
        Args:
            query: Query text to search for
            top_k: Number of documents to retrieve
            distance_threshold: Optional threshold to filter by distance (0.0 most similar)
            
        Returns:
            List of retrieved documents with scores
        """
        self.ensure_index_loaded()
        
        if not query or not query.strip():
            logger.warning("Empty query provided")
            return []
        
        # Embed query
        query_embedding = self.vectorizer.embed_text(query)
        query_embedding = np.expand_dims(query_embedding, axis=0)
        
        # Search FAISS index (returns distances and indices)
        distances, indices = self.index.search(query_embedding, min(top_k, len(self.documents)))
        
        # Convert distances to similarity scores (L2 distance)
        # Lower distance = higher similarity, normalize to 0-1
        max_distance = np.max(distances[0]) + 1e-6  # Avoid division by zero
        similarities = 1.0 - (distances[0] / max_distance)
        
        # Build results
        results = []
        for idx, (doc_idx, distance, similarity) in enumerate(zip(indices[0], distances[0], similarities)):
            if doc_idx < 0 or doc_idx >= len(self.documents):
                continue
            
            # Apply distance threshold if provided
            if distance_threshold is not None and distance > distance_threshold:
                break
            
            doc = self.documents[doc_idx]
            results.append({
                "rank": idx + 1,
                "id": doc["id"],
                "title": doc.get("title", "Unknown"),
                "text": doc.get("text", ""),
                "type": doc.get("type", "unknown"),
                "distance": float(distance),
                "similarity": float(similarity),
                "metadata": doc.get("metadata", {})
            })
        
        logger.debug(f"Retrieved {len(results)} documents for query: {query[:50]}...")
        return results
    
    def retrieve_for_agent(
        self,
        agent_name: str,
        dream_text: str,
        top_k: int = 3,
        context_limit: int = 2000
    ) -> str:
        """
        Retrieve context specifically for an agent's analysis.
        
        Args:
            agent_name: Name of the agent
            dream_text: The dream/business idea being analyzed
            top_k: Number of documents to retrieve
            context_limit: Max characters in returned context
            
        Returns:
            Formatted context string for agent prompt injection
        """
        self.ensure_index_loaded()
        
        # Customize query based on agent type
        agent_queries = {
            "Dream Understanding Agent": f"Business idea validation: {dream_text}",
            "Market Analyst Agent": f"Market analysis for: {dream_text}. TAM, competition, opportunity",
            "Resource Analyst Agent": f"Resource requirements and budgeting for: {dream_text}",
            "Technology Architecture Agent": f"Technology stack and architecture for: {dream_text}",
            "Innovation & Differentiation Agent": f"Innovation and differentiation for: {dream_text}"
        }
        
        # Get agent-specific query or default
        query = agent_queries.get(agent_name, dream_text)
        
        # Retrieve documents
        results = self.retrieve(query, top_k=top_k)
        
        if not results:
            logger.debug(f"No context retrieved for {agent_name}")
            return ""
        
        # Format context
        context_parts = [f"Retrieved Relevant Patterns & Case Studies:"]
        current_length = len(context_parts[0])
        
        for result in results:
            section = f"\n\n[{result['type'].upper()} - {result['title']} (similarity: {result['similarity']:.2f})]"
            section += f"\n{result['text'][:500]}..."  # Truncate individual documents
            
            if current_length + len(section) > context_limit:
                break
            
            context_parts.append(section)
            current_length += len(section)
        
        context = "\n".join(context_parts)
        
        logger.info(f"Generated {len(results)} context pieces for {agent_name} ({len(context)} chars)")
        return context
    
    def batch_retrieve(
        self,
        queries: List[str],
        top_k: int = 5
    ) -> List[List[Dict[str, Any]]]:
        """
        Retrieve documents for multiple queries.
        
        Args:
            queries: List of query texts
            top_k: Number of documents per query
            
        Returns:
            List of result lists (one per query)
        """
        self.ensure_index_loaded()
        
        # Embed all queries at once
        query_embeddings = self.vectorizer.embed_texts(queries)
        
        # Search
        distances, indices = self.index.search(query_embeddings, min(top_k, len(self.documents)))
        
        # Process results for each query
        all_results = []
        for q_idx, (query_distances, query_indices) in enumerate(zip(distances, indices)):
            # Convert to similarity scores
            max_distance = np.max(query_distances) + 1e-6
            similarities = 1.0 - (query_distances / max_distance)
            
            results = []
            for doc_idx, distance, similarity in zip(query_indices, query_distances, similarities):
                if doc_idx < 0 or doc_idx >= len(self.documents):
                    continue
                
                doc = self.documents[doc_idx]
                results.append({
                    "id": doc["id"],
                    "title": doc.get("title", "Unknown"),
                    "text": doc.get("text", ""),
                    "type": doc.get("type", "unknown"),
                    "distance": float(distance),
                    "similarity": float(similarity),
                    "metadata": doc.get("metadata", {})
                })
            
            all_results.append(results)
        
        logger.debug(f"Batch retrieved for {len(queries)} queries")
        return all_results
    
    def get_similar_documents(
        self,
        document_id: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find documents similar to a given document.
        
        Args:
            document_id: ID of reference document
            top_k: Number of similar documents to return
            
        Returns:
            List of similar documents
        """
        self.ensure_index_loaded()
        
        # Find document index
        doc_idx = None
        for i, doc_id in enumerate(self.document_ids):
            if doc_id == document_id:
                doc_idx = i
                break
        
        if doc_idx is None:
            logger.warning(f"Document not found: {document_id}")
            return []
        
        # Get embedding from index
        # This is approximate - we retrieve the document and re-embed
        ref_doc = self.documents[doc_idx]
        query_embedding = self.vectorizer.embed_text(ref_doc["text"])
        query_embedding = np.expand_dims(query_embedding, axis=0)
        
        # Search (will include self)
        distances, indices = self.index.search(query_embedding, min(top_k + 1, len(self.documents)))
        
        # Skip self and return
        results = []
        for idx, (doc_idx_result, distance) in enumerate(zip(indices[0], distances[0])):
            if doc_idx_result < 0 or doc_idx_result >= len(self.documents) or doc_idx_result == doc_idx:
                continue
            
            if len(results) >= top_k:
                break
            
            doc = self.documents[doc_idx_result]
            results.append({
                "id": doc["id"],
                "title": doc.get("title", "Unknown"),
                "distance": float(distance),
                "type": doc.get("type", "unknown")
            })
        
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get retriever statistics."""
        return {
            "index_name": self.index_name,
            "total_documents": len(self.documents) if self.documents else 0,
            "index_loaded": self.index is not None,
            "vectorizer": self.vectorizer.get_metrics()
        }


if __name__ == "__main__":
    # Test retriever
    print("✓ KnowledgeRetriever module loaded successfully")
