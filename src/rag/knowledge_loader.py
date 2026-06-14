"""
Knowledge Loader for RAG System.
Manages initialization, index building, and retriever access.
Provides singleton instance for use throughout application.
"""

import logging
from pathlib import Path
from typing import Optional
from src.rag.vectorizer import DocumentVectorizer
from src.rag.retriever import KnowledgeRetriever

logger = logging.getLogger(__name__)

# Singleton instance
_retriever: Optional[KnowledgeRetriever] = None


class KnowledgeLoader:
    """
    Manages knowledge base initialization and access.
    Builds FAISS indices from knowledge JSON files on first use.
    """
    
    def __init__(
        self,
        knowledge_dir: str = "knowledge",
        index_dir: str = "knowledge/indices",
        model_name: str = "all-MiniLM-L6-v2",
        rebuild_index: bool = False
    ):
        """
        Initialize knowledge loader.
        
        Args:
            knowledge_dir: Directory containing knowledge JSON files
            index_dir: Directory to store FAISS indices
            model_name: Sentence-transformers model name
            rebuild_index: Force rebuild index even if it exists
        """
        self.knowledge_dir = Path(knowledge_dir)
        self.index_dir = Path(index_dir)
        self.model_name = model_name
        self.rebuild_index = rebuild_index
        
        # Create directories if needed
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        self.vectorizer = None
        self.retriever = None
        
        logger.info(
            f"KnowledgeLoader initialized\n"
            f"  Knowledge dir: {self.knowledge_dir}\n"
            f"  Index dir: {self.index_dir}\n"
            f"  Model: {model_name}"
        )
    
    def build_index(self) -> bool:
        """
        Build FAISS index from knowledge base files.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Building FAISS index from knowledge base...")
        
        try:
            # Initialize vectorizer
            self.vectorizer = DocumentVectorizer(
                model_name=self.model_name,
                index_dir=str(self.index_dir)
            )
            
            # Vectorize knowledge base
            embeddings, doc_ids, documents = self.vectorizer.vectorize_knowledge_base(
                str(self.knowledge_dir)
            )
            
            # Create and save FAISS index
            self.vectorizer.create_faiss_index(embeddings)
            self.vectorizer.save_index("knowledge_index")
            
            logger.info(f"✓ Index built successfully ({len(documents)} documents)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to build index: {e}", exc_info=True)
            return False
    
    def load(self) -> KnowledgeRetriever:
        """
        Load or build knowledge base and return retriever instance.
        
        Returns:
            KnowledgeRetriever instance
            
        Raises:
            RuntimeError if index cannot be loaded or built
        """
        # Check if index exists
        index_file = self.index_dir / "knowledge_index.faiss"
        
        if not index_file.exists() or self.rebuild_index:
            logger.info("Index not found or rebuild requested, building...")
            if not self.build_index():
                raise RuntimeError("Failed to build knowledge base index")
        
        # Initialize retriever
        self.retriever = KnowledgeRetriever(
            index_name="knowledge_index",
            index_dir=str(self.index_dir),
            model_name=self.model_name
        )
        
        # Load index
        if not self.retriever.load_index():
            raise RuntimeError("Failed to load knowledge index")
        
        logger.info(f"✓ Knowledge base loaded ({self.retriever.index.ntotal} vectors)")
        
        return self.retriever
    
    def get_metrics(self) -> dict:
        """Get knowledge base statistics."""
        if not self.retriever:
            return {"status": "not_loaded"}
        
        return self.retriever.get_metrics()


def initialize_knowledge_base(
    knowledge_dir: str = "knowledge",
    index_dir: str = "knowledge/indices",
    model_name: str = "all-MiniLM-L6-v2",
    rebuild: bool = False
) -> KnowledgeRetriever:
    """
    Initialize knowledge base and return retriever.
    
    Args:
        knowledge_dir: Directory containing knowledge files
        index_dir: Directory for FAISS indices
        model_name: Embedding model name
        rebuild: Force rebuild index
        
    Returns:
        KnowledgeRetriever instance
    """
    global _retriever
    
    if _retriever is not None and not rebuild:
        logger.debug("Using existing knowledge base retriever")
        return _retriever
    
    loader = KnowledgeLoader(
        knowledge_dir=knowledge_dir,
        index_dir=index_dir,
        model_name=model_name,
        rebuild_index=rebuild
    )
    
    _retriever = loader.load()
    return _retriever


def get_knowledge_retriever() -> Optional[KnowledgeRetriever]:
    """
    Get the singleton retriever instance.
    Returns None if not yet initialized.
    """
    return _retriever


def reset_knowledge_base():
    """Reset the singleton retriever instance."""
    global _retriever
    _retriever = None
    logger.info("Knowledge base retriever reset")


if __name__ == "__main__":
    # Test knowledge loader
    print("✓ KnowledgeLoader module loaded successfully")
