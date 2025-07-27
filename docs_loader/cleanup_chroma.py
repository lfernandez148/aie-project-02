# cleanup_chroma.py
import shutil
import os
from loguru import logger

# Setup logging similar to ingest.py
LOGS_FOLDER = "logs"
CHROMA_DIR = "../chroma_db"

logger.add(
    f"{LOGS_FOLDER}/cleanup.log", 
    rotation="1 week", 
    retention="4 weeks", 
    level="INFO"
)


def cleanup_chroma():
    """Clean up ChromaDB and tracking files for fresh start"""
    
    logger.info("Starting ChromaDB cleanup process")
    
    # Remove ChromaDB directory
    if os.path.exists(CHROMA_DIR):
        try:
            shutil.rmtree(CHROMA_DIR)
            logger.success(f"Removed ChromaDB directory: {CHROMA_DIR}")
        except Exception as e:
            logger.error(f"Failed to remove ChromaDB directory: {e}")
    else:
        logger.info(f"ChromaDB directory not found: {CHROMA_DIR}")
    
    # Remove tracking CSV
    tracking_file = "processed_files.csv"
    if os.path.exists(tracking_file):
        try:
            os.remove(tracking_file)
            logger.success(f"Removed tracking file: {tracking_file}")
        except Exception as e:
            logger.error(f"Failed to remove tracking file: {e}")
    else:
        logger.info(f"Tracking file not found: {tracking_file}")
    
    logger.success("Cleanup complete! Ready for fresh document ingestion.")


if __name__ == "__main__":
    cleanup_chroma() 