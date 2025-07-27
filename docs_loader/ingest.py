import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    PyPDFLoader, 
    UnstructuredHTMLLoader, 
    UnstructuredWordDocumentLoader
)

from loguru import logger
import shutil
import os
import pandas as pd
import hashlib
from datetime import datetime

WATCH_FOLDER = "docs/landing"
CHROMA_DIR = "../chroma_db"
LOGS_FOLDER = "logs"
DONE_FOLDER = "docs/done"
TRACKING_FILE = "processed_files.csv"

# Create done folder if it doesn't exist
os.makedirs(DONE_FOLDER, exist_ok=True)

logger.add(
    f"{LOGS_FOLDER}/docs_loader.log", 
    rotation="1 week", 
    retention="4 weeks", 
    level="INFO"
)


def get_file_hash(file_path):
    """Generate MD5 hash of file content"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def get_processed_files():
    """Get list of already processed files and their hashes from CSV using pandas"""
    if os.path.exists(TRACKING_FILE):
        df = pd.read_csv(TRACKING_FILE)
        # Return both filenames and content hashes
        return set(df['filename'].tolist()), set(df['content_hash'].tolist())
    return set(), set()


def add_processed_file(filename, file_path, content_hash):
    """Add file to processed files CSV using pandas"""
    new_row = pd.DataFrame([{
        'filename': filename,
        'original_path': file_path,
        'content_hash': content_hash,
        'processed_date': datetime.now().isoformat()
    }])
    
    if os.path.exists(TRACKING_FILE):
        df = pd.read_csv(TRACKING_FILE)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row
    
    df.to_csv(TRACKING_FILE, index=False)


def get_loader_for_file(file_path):
    """Get appropriate loader based on file extension"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        return PyPDFLoader(file_path)
    elif file_ext in ['.html', '.htm']:
        return UnstructuredHTMLLoader(file_path)
    elif file_ext == '.docx':
        return UnstructuredWordDocumentLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")


class DocumentHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_ext = os.path.splitext(event.src_path)[1].lower()
        if file_ext in ['.pdf', '.html', '.htm', '.docx']:
            filename = os.path.basename(event.src_path)
            content_hash = get_file_hash(event.src_path)
            processed_files, processed_hashes = get_processed_files()
            
            # Check both filename and content hash
            if filename in processed_files or content_hash in processed_hashes:
                logger.info(f"Skipping already processed file: {filename}")
                # Move to done folder without reprocessing
                done_path = os.path.join(DONE_FOLDER, filename)
                shutil.move(event.src_path, done_path)
                logger.info(
                    f"Moved {filename} to done folder (already processed)"
                )
            else:
                logger.info(f"New document detected: {event.src_path}")
                self.ingest_document(event.src_path)

    def ingest_document(self, file_path):
        try:
            filename = os.path.basename(file_path)
            content_hash = get_file_hash(file_path)
            
            # Get appropriate loader
            loader = get_loader_for_file(file_path)
            docs = loader.load()
            
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            db = Chroma(
                persist_directory=CHROMA_DIR, 
                embedding_function=embeddings
            )
            db.add_documents(docs)
            logger.success(f"Ingested and indexed: {file_path}")
            
            # Move file to done folder
            done_path = os.path.join(DONE_FOLDER, filename)
            shutil.move(file_path, done_path)
            logger.info(f"Moved {filename} to done folder")
            
            # Add to processed files tracking
            add_processed_file(filename, file_path, content_hash)
            logger.info(f"Added {filename} to processed files tracking")
            
        except Exception as e:
            logger.error(f"Failed to ingest {file_path}: {e}")


if __name__ == "__main__":
    logger.info(f"Starting document watcher for folder: {WATCH_FOLDER}")
    event_handler = DocumentHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
    observer.start()
    logger.info(f"Watching folder: {WATCH_FOLDER} for new documents...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Shutting down document watcher.")
    observer.join()