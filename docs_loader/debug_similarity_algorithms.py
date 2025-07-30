#!/usr/bin/env python3
"""
Debug script to test different similarity algorithms and distance metrics
"""
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from loguru import logger
import os

CHROMA_DIR = "../chroma_db"
LOGS_FOLDER = "logs"

logger.add(
    f"{LOGS_FOLDER}/debug_similarity.log", 
    rotation="1 week", 
    retention="4 weeks", 
    level="INFO"
)


def test_different_similarity_methods():
    """Test different similarity search methods"""
    
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Test query
    test_query = "executive summary for campaign 101"
    
    logger.info(f"Testing query: '{test_query}'")
    logger.info("="*60)
    
    # Method 1: Default ChromaDB (cosine distance)
    logger.info("Method 1: Default ChromaDB (cosine distance)")
    db1 = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
    docs1 = db1.similarity_search_with_score(test_query, k=3)
    
    for i, (doc, score) in enumerate(docs1):
        logger.info(f"  Doc {i+1}: Score={score:.4f}, Content: {doc.page_content[:100]}...")
    
    # Method 2: Try with different distance function
    logger.info("\nMethod 2: Testing with different distance function")
    try:
        # Try to configure with different distance function
        db2 = Chroma(
            persist_directory=CHROMA_DIR, 
            embedding_function=embeddings,
            # Try different distance functions
            distance_strategy="IP"  # Inner Product (cosine similarity)
        )
        docs2 = db2.similarity_search_with_score(test_query, k=3)
        
        for i, (doc, score) in enumerate(docs2):
            logger.info(f"  Doc {i+1}: Score={score:.4f}, Content: {doc.page_content[:100]}...")
    except Exception as e:
        logger.error(f"Error with IP distance: {e}")
    
    # Method 3: Try with L2 distance
    logger.info("\nMethod 3: Testing with L2 distance")
    try:
        db3 = Chroma(
            persist_directory=CHROMA_DIR, 
            embedding_function=embeddings,
            distance_strategy="L2"  # L2 distance
        )
        docs3 = db3.similarity_search_with_score(test_query, k=3)
        
        for i, (doc, score) in enumerate(docs3):
            logger.info(f"  Doc {i+1}: Score={score:.4f}, Content: {doc.page_content[:100]}...")
    except Exception as e:
        logger.error(f"Error with L2 distance: {e}")
    
    # Method 4: Try with IP distance (cosine similarity)
    logger.info("\nMethod 4: Testing with IP distance (cosine similarity)")
    try:
        db4 = Chroma(
            persist_directory=CHROMA_DIR, 
            embedding_function=embeddings,
            distance_strategy="IP"  # Inner Product
        )
        docs4 = db4.similarity_search_with_score(test_query, k=3)
        
        for i, (doc, score) in enumerate(docs4):
            logger.info(f"  Doc {i+1}: Score={score:.4f}, Content: {doc.page_content[:100]}...")
    except Exception as e:
        logger.error(f"Error with IP distance: {e}")


def test_threshold_adjustment():
    """Test different threshold values"""
    
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    db = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
    
    test_query = "executive summary for campaign 101"
    logger.info(f"\nTesting different thresholds for: '{test_query}'")
    logger.info("="*60)
    
    # Get all documents with scores
    docs_and_scores = db.similarity_search_with_score(test_query, k=10)
    
    # Test different thresholds
    thresholds = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.5]
    
    for threshold in thresholds:
        relevant_docs = [doc for doc, score in docs_and_scores if score < threshold]
        logger.info(f"Threshold {threshold}: {len(relevant_docs)} documents pass")
        
        if relevant_docs:
            logger.info(f"  First doc content: {relevant_docs[0].page_content[:100]}...")


if __name__ == "__main__":
    test_different_similarity_methods()
    test_threshold_adjustment() 