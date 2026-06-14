"""
Integration tests for RAG system.
Tests vectorizer, FAISS index creation, and retrieval.
"""

import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.rag import (
    initialize_knowledge_base,
    get_knowledge_retriever,
    reset_knowledge_base
)


def test_rag_system():
    """Full integration test of RAG system."""
    
    print("\n" + "=" * 70)
    print("🧪 RAG SYSTEM INTEGRATION TEST")
    print("=" * 70)
    
    # Test 1: Initialize knowledge base
    print("\n[TEST 1] Initialize Knowledge Base")
    print("-" * 70)
    
    try:
        retriever = initialize_knowledge_base(
            knowledge_dir="knowledge",
            rebuild=False  # Use existing or build if needed
        )
        print("✓ Knowledge base initialized")
        print(f"  Documents loaded: {retriever.index.ntotal}")
        print(f"  Model: {retriever.vectorizer.model_name}")
        print(f"  Dimension: {retriever.vectorizer.dimension}")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return False
    
    # Test 2: Retrieve for pattern query
    print("\n[TEST 2] Retrieve Documents - Pattern Query")
    print("-" * 70)
    
    query = "Vertical SaaS market positioning strategy"
    print(f"Query: {query}")
    
    try:
        results = retriever.retrieve(query, top_k=3)
        print(f"✓ Retrieved {len(results)} documents\n")
        
        for result in results:
            print(f"  Rank {result['rank']}: [{result['type']}] {result['title']}")
            print(f"    Similarity: {result['similarity']:.3f}")
            print(f"    Text preview: {result['text'][:100]}...\n")
    except Exception as e:
        print(f"✗ Retrieval failed: {e}")
        return False
    
    # Test 3: Retrieve for business model query
    print("[TEST 3] Retrieve Documents - Business Model Query")
    print("-" * 70)
    
    query = "SaaS subscription recurring revenue pricing"
    print(f"Query: {query}")
    
    try:
        results = retriever.retrieve(query, top_k=3)
        print(f"✓ Retrieved {len(results)} documents\n")
        
        for result in results:
            print(f"  Rank {result['rank']}: [{result['type']}] {result['title']}")
            print(f"    Similarity: {result['similarity']:.3f}\n")
    except Exception as e:
        print(f"✗ Retrieval failed: {e}")
        return False
    
    # Test 4: Retrieve for case study query
    print("[TEST 4] Retrieve Documents - Case Study Query")
    print("-" * 70)
    
    query = "AI startup failure risks lessons learned"
    print(f"Query: {query}")
    
    try:
        results = retriever.retrieve(query, top_k=3)
        print(f"✓ Retrieved {len(results)} documents\n")
        
        for result in results:
            print(f"  Rank {result['rank']}: [{result['type']}] {result['title']}")
            print(f"    Similarity: {result['similarity']:.3f}\n")
    except Exception as e:
        print(f"✗ Retrieval failed: {e}")
        return False
    
    # Test 5: Agent-specific retrieval
    print("[TEST 5] Agent-Specific Context Retrieval")
    print("-" * 70)
    
    dream = "AI-powered customer support automation platform for small businesses"
    agents = [
        "Dream Understanding Agent",
        "Market Analyst Agent",
        "Resource Analyst Agent",
        "Technology Architecture Agent",
        "Innovation & Differentiation Agent"
    ]
    
    for agent_name in agents:
        try:
            context = retriever.retrieve_for_agent(
                agent_name=agent_name,
                dream_text=dream,
                top_k=2
            )
            
            context_length = len(context)
            print(f"✓ {agent_name}")
            print(f"  Context length: {context_length} chars\n")
        except Exception as e:
            print(f"✗ {agent_name}: {e}\n")
            return False
    
    # Test 6: Batch retrieval
    print("[TEST 6] Batch Retrieval")
    print("-" * 70)
    
    queries = [
        "How to build a marketplace platform",
        "Low-code no-code platform strategy",
        "Payment processing API business model"
    ]
    
    try:
        batch_results = retriever.batch_retrieve(queries, top_k=2)
        print(f"✓ Batch retrieved for {len(queries)} queries\n")
        
        for query, results in zip(queries, batch_results):
            print(f"  Query: {query}")
            print(f"  Results: {len(results)} documents")
            for r in results:
                print(f"    - [{r['type']}] {r['title']} (sim: {r['similarity']:.2f})")
            print()
    except Exception as e:
        print(f"✗ Batch retrieval failed: {e}")
        return False
    
    # Test 7: Metrics
    print("[TEST 7] Retriever Metrics")
    print("-" * 70)
    
    try:
        metrics = retriever.get_metrics()
        print("✓ Retrieved metrics:")
        print(f"  Index: {metrics['index_name']}")
        print(f"  Total Documents: {metrics['total_documents']}")
        print(f"  Index Loaded: {metrics['index_loaded']}")
        print(f"  Vectorizer Model: {metrics['vectorizer']['model']}")
        print(f"  Embedding Dimension: {metrics['vectorizer']['dimension']}")
    except Exception as e:
        print(f"✗ Metrics retrieval failed: {e}")
        return False
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED")
    print("=" * 70)
    print("\nRAG System Status:")
    print(f"  ✓ Knowledge base built and indexed")
    print(f"  ✓ FAISS index loaded ({retriever.index.ntotal} vectors)")
    print(f"  ✓ Semantic search working")
    print(f"  ✓ Context injection ready for agents")
    
    return True


if __name__ == "__main__":
    success = test_rag_system()
    sys.exit(0 if success else 1)
