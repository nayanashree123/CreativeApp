"""
Vectorizer module for RAG system.
Converts text documents into embeddings and creates FAISS indices.
Uses sentence-transformers for efficient embeddings.
"""

import json
import logging
import pickle
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class DocumentVectorizer:
    """
    Converts documents to embeddings and manages FAISS index creation.
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        dimension: int = 384,
        index_dir: str = None
    ):
        """
        Initialize vectorizer with sentence-transformers model.
        
        Args:
            model_name: Sentence-transformers model (all-MiniLM-L6-v2 is lightweight)
            dimension: Embedding dimension (depends on model)
            index_dir: Directory to store FAISS indices
        """
        self.model_name = model_name
        self.dimension = dimension
        self.index_dir = Path(index_dir) if index_dir else Path("knowledge/indices")
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Lazy load model
        self.model = None
        self.documents = []
        self.document_ids = []
        self.index = None
        
        logger.info(f"Vectorizer initialized (model: {model_name}, dim: {dimension})")
    
    def _load_model(self):
        """Lazy load sentence-transformers model on first use."""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.debug(f"Loading model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                logger.info(f"Model loaded successfully")
            except ImportError:
                raise RuntimeError("sentence-transformers not installed. Run: pip install sentence-transformers")
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Convert text to embedding vector.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding as numpy array (dimension,)
        """
        self._load_model()
        
        # Handle empty text
        if not text or not text.strip():
            return np.zeros(self.dimension, dtype=np.float32)
        
        # Truncate long texts (max 512 tokens ~2000 chars)
        text = text[:2000]
        
        embeddings = self.model.encode([text], convert_to_tensor=False)
        return embeddings[0].astype(np.float32)
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Convert multiple texts to embedding vectors (batch).
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Embeddings as numpy array (len(texts), dimension)
        """
        self._load_model()
        
        # Filter and truncate
        texts = [t[:2000] if t else "" for t in texts]
        
        embeddings = self.model.encode(texts, convert_to_tensor=False, show_progress_bar=False)
        return embeddings.astype(np.float32)
    
    def extract_documents(self, json_path: str) -> List[Dict[str, Any]]:
        """
        Extract documents from knowledge base JSON files.
        
        Args:
            json_path: Path to knowledge JSON file
            
        Returns:
            List of documents with id, title, text, metadata
        """
        documents = []
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Handle different knowledge base structures
        if "patterns" in data:
            # Startup patterns
            for pattern in data["patterns"]:
                doc_text = f"""
Pattern: {pattern.get('name', '')}
Description: {pattern.get('description', '')}
Success Rate: {pattern.get('success_rate', 0)}
Best For: {', '.join(pattern.get('best_for', []))}
Characteristics: {'; '.join(pattern.get('characteristics', []))}
Risks: {'; '.join(pattern.get('risks', []))}
"""
                documents.append({
                    "id": pattern.get("id", f"pattern_{len(documents)}"),
                    "title": pattern.get("name", "Unknown"),
                    "text": doc_text.strip(),
                    "type": "pattern",
                    "metadata": {
                        "success_rate": pattern.get("success_rate", 0),
                        "best_for": pattern.get("best_for", [])
                    }
                })
        
        elif "business_models" in data:
            # Business models
            for model in data["business_models"]:
                doc_text = f"""
Business Model: {model.get('name', '')}
Description: {model.get('description', '')}
Revenue Model: {model.get('revenue_model', '')}
Advantages: {'; '.join(model.get('advantages', []))}
Disadvantages: {'; '.join(model.get('disadvantages', []))}
Time to Revenue: {model.get('time_to_revenue_months', 0)} months
Typical ARPU: {model.get('typical_arpu', 'Unknown')}
"""
                documents.append({
                    "id": model.get("id", f"model_{len(documents)}"),
                    "title": model.get("name", "Unknown"),
                    "text": doc_text.strip(),
                    "type": "business_model",
                    "metadata": {
                        "revenue_model": model.get("revenue_model", ""),
                        "time_to_revenue": model.get("time_to_revenue_months", 0)
                    }
                })
        
        elif "case_studies" in data:
            # Case studies
            for case in data["case_studies"]:
                doc_text = f"""
Case Study: {case.get('name', '')}
Status: {case.get('status', '')}
Summary: {case.get('summary', '')}
Business Model: {case.get('business_model', '')}
Key Success Factors: {'; '.join(case.get('key_success_factors', []))}
Key Failure Factors: {'; '.join(case.get('key_failure_factors', []))}
Lessons: {'; '.join(case.get('lessons', []))}
"""
                documents.append({
                    "id": case.get("id", f"case_{len(documents)}"),
                    "title": case.get("name", "Unknown"),
                    "text": doc_text.strip(),
                    "type": "case_study",
                    "metadata": {
                        "status": case.get("status", ""),
                        "business_model": case.get("business_model", ""),
                        "lessons": case.get("lessons", [])
                    }
                })
        
        logger.info(f"Extracted {len(documents)} documents from {json_path}")
        return documents
    
    def vectorize_knowledge_base(self, knowledge_dir: str = "knowledge") -> Tuple[np.ndarray, List[str], List[Dict]]:
        """
        Vectorize all knowledge base documents.
        
        Args:
            knowledge_dir: Directory containing knowledge JSON files
            
        Returns:
            Tuple of (embeddings array, document ids, documents metadata)
        """
        all_documents = []
        all_ids = []
        knowledge_path = Path(knowledge_dir)
        
        # Process all JSON files
        for json_file in knowledge_path.glob("*.json"):
            try:
                docs = self.extract_documents(str(json_file))
                all_documents.extend(docs)
                logger.info(f"Processed {json_file.name}: {len(docs)} documents")
            except Exception as e:
                logger.error(f"Error processing {json_file.name}: {e}")
        
        if not all_documents:
            raise ValueError(f"No documents found in {knowledge_dir}")
        
        # Extract texts and embed
        texts = [doc["text"] for doc in all_documents]
        embeddings = self.embed_texts(texts)
        all_ids = [doc["id"] for doc in all_documents]
        
        self.documents = all_documents
        self.document_ids = all_ids
        
        logger.info(f"Vectorized {len(all_documents)} documents")
        logger.info(f"Embedding shape: {embeddings.shape}")
        
        return embeddings, all_ids, all_documents
    
    def create_faiss_index(self, embeddings: np.ndarray) -> Any:
        """
        Create FAISS index from embeddings.
        
        Args:
            embeddings: Array of embeddings (num_docs, dimension)
            
        Returns:
            FAISS index object
        """
        try:
            import faiss
        except ImportError:
            raise RuntimeError("faiss-cpu not installed. Run: pip install faiss-cpu")
        
        # Ensure C-contiguous layout
        embeddings = np.ascontiguousarray(embeddings)
        
        # Create index
        index = faiss.IndexFlatL2(self.dimension)
        index.add(embeddings)
        
        logger.info(f"Created FAISS index with {index.ntotal} vectors")
        
        self.index = index
        return index
    
    def save_index(self, index_name: str = "knowledge_index"):
        """
        Save FAISS index and metadata to disk.
        
        Args:
            index_name: Name of index to save
        """
        if self.index is None:
            raise ValueError("No index to save. Call create_faiss_index first.")
        
        try:
            import faiss
        except ImportError:
            raise RuntimeError("faiss-cpu not installed")
        
        index_file = self.index_dir / f"{index_name}.faiss"
        metadata_file = self.index_dir / f"{index_name}_metadata.pkl"
        
        # Save FAISS index
        faiss.write_index(self.index, str(index_file))
        logger.info(f"Saved FAISS index to {index_file}")
        
        # Save metadata
        metadata = {
            "document_ids": self.document_ids,
            "documents": self.documents,
            "model_name": self.model_name,
            "dimension": self.dimension
        }
        
        with open(metadata_file, 'wb') as f:
            pickle.dump(metadata, f)
        logger.info(f"Saved metadata to {metadata_file}")
    
    def load_index(self, index_name: str = "knowledge_index") -> Any:
        """
        Load FAISS index and metadata from disk.
        
        Args:
            index_name: Name of index to load
            
        Returns:
            FAISS index object
        """
        try:
            import faiss
        except ImportError:
            raise RuntimeError("faiss-cpu not installed")
        
        index_file = self.index_dir / f"{index_name}.faiss"
        metadata_file = self.index_dir / f"{index_name}_metadata.pkl"
        
        if not index_file.exists() or not metadata_file.exists():
            raise FileNotFoundError(f"Index files not found: {index_file}, {metadata_file}")
        
        # Load FAISS index
        self.index = faiss.read_index(str(index_file))
        logger.info(f"Loaded FAISS index from {index_file} ({self.index.ntotal} vectors)")
        
        # Load metadata
        with open(metadata_file, 'rb') as f:
            metadata = pickle.load(f)
        
        self.document_ids = metadata["document_ids"]
        self.documents = metadata["documents"]
        self.model_name = metadata["model_name"]
        self.dimension = metadata["dimension"]
        
        logger.info(f"Loaded metadata with {len(self.documents)} documents")
        
        return self.index
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get vectorizer statistics."""
        return {
            "model": self.model_name,
            "dimension": self.dimension,
            "total_documents": len(self.documents),
            "index_size": self.index.ntotal if self.index else 0,
            "index_dir": str(self.index_dir)
        }


if __name__ == "__main__":
    # Test vectorizer
    print("✓ DocumentVectorizer module loaded successfully")
