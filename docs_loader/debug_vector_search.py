#!/usr/bin/env python3
"""
Debug script for vector search behavior
"""
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from loguru import logger
import os

CHROMA_DIR = "../chroma_db"
LOGS_FOLDER = "logs"

logger.add(
    f"{LOGS_FOLDER}/debug_vector.log", 
    rotation="1 week", 
    retention="4 weeks", 
    level="INFO"
)


def debug_vector_search():
    """Debug vector search behavior"""
    
    # Initialize embeddings and DB
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    db = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
    
    # Test queries
    test_queries = [
        "executive summary for campaign 101",
        "campaign 101",
        "executive summary",
        "performance metrics",
        "conversion rate"
    ]
    
    for query in test_queries:
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing query: '{query}'")
        logger.info(f"{'='*50}")
        
        # Get documents with scores
        docs_and_scores = db.similarity_search_with_score(query, k=5)
        
        logger.info(f"Found {len(docs_and_scores)} documents")
        
        for i, (doc, score) in enumerate(docs_and_scores):
            logger.info(f"\nDocument {i+1}:")
            logger.info(f"Score: {score:.4f}")
            logger.info(f"Content preview: {doc.page_content[:200]}...")
            if hasattr(doc, 'metadata') and doc.metadata:
                logger.info(f"Metadata: {doc.metadata}")
            else:
                logger.info("Metadata: None")
            
            # Check if it would pass our threshold
            if score < 1.2:
                logger.info("✅ Would be included (score < 1.2)")
            else:
                logger.info("❌ Would be filtered out (score >= 1.2)")


if __name__ == "__main__":
    debug_vector_search() 