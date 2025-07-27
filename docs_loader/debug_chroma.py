# debug_chroma.py
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from loguru import logger
import os

CHROMA_DIR = "../chroma_db"
LOGS_FOLDER = "logs"

logger.add(
    f"{LOGS_FOLDER}/debug_chroma.log", 
    rotation="1 week", 
    retention="4 weeks", 
    level="INFO"
)


def debug_chroma():
    logger.info("=== ChromaDB Debug Information ===")
    
    # Check if ChromaDB directory exists
    if not os.path.exists(CHROMA_DIR):
        logger.error(f"ChromaDB directory '{CHROMA_DIR}' does not exist!")
        return
    
    logger.info(f"ChromaDB directory exists: {CHROMA_DIR}")
    
    # Initialize embeddings and ChromaDB
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    try:
        db = Chroma(
            persist_directory=CHROMA_DIR, 
            embedding_function=embeddings
        )
        
        # Get collection info
        collection = db._collection
        count = collection.count()
        logger.info(f"Total documents in ChromaDB: {count}")
        
        if count == 0:
            logger.warning("No documents found in ChromaDB!")
            logger.info(
                "Make sure you've run the ingest service and processed some "
                "documents."
            )
            return
        
        # Test a simple query
        logger.info("=== Testing Query ===")
        test_query = "campaign"
        docs = db.similarity_search(test_query, k=3)
        logger.info(f"Query: '{test_query}'")
        logger.info(f"Found {len(docs)} documents")
        
        for i, doc in enumerate(docs):
            logger.info(f"--- Document {i+1} ---")
            logger.info(f"Content preview: {doc.page_content[:200]}...")
            if hasattr(doc, 'metadata'):
                logger.info(f"Metadata: {doc.metadata}")
        
        # Show some document IDs
        logger.info("=== Sample Document IDs ===")
        results = collection.get(limit=5)
        if results['ids']:
            logger.info(f"Sample IDs: {results['ids'][:3]}")
        
    except Exception as e:
        logger.error(f"Error accessing ChromaDB: {e}")

if __name__ == "__main__":
    debug_chroma() 