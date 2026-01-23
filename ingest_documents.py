"""
Ingest PDF documents from the knowledge folder into the vector store.
Run this script to process and index all PDFs before starting the API.

Usage:
    python ingest_documents.py [--force]
    
Options:
    --force: Force reingestion of all documents (deletes existing collection)
"""

import asyncio
import sys
import time
import logging

from document_processor import document_processor
from vector_store import vector_store

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def ingest_documents(force: bool = False):
    """Ingest all PDF documents from the knowledge folder."""
    try:
        logger.info("Starting document ingestion...")
        start_time = time.time()

        # Check if we need to reingest
        if force:
            logger.info(
                "Force reingestion requested - deleting existing collection...")
            vector_store.delete_collection()
        else:
            stats = vector_store.get_collection_stats()
            if stats["document_count"] > 0:
                logger.info(
                    f"Vector store already contains {stats['document_count']} documents")
                response = input(
                    "Do you want to continue and add more documents? (y/n): ")
                if response.lower() != 'y':
                    logger.info("Ingestion cancelled")
                    return

        # Process all PDFs in the knowledge directory
        logger.info("Processing PDF documents...")
        documents = document_processor.process_directory()

        if not documents:
            logger.error("No documents were processed successfully")
            return

        logger.info(f"Processed {len(documents)} chunks from PDFs")

        # Add to vector store
        logger.info("Adding documents to vector store...")
        vector_store.add_documents(documents)

        # Get final stats
        stats = vector_store.get_collection_stats()
        time_taken = time.time() - start_time

        logger.info("=" * 60)
        logger.info("Document Ingestion Complete!")
        logger.info("=" * 60)
        logger.info(
            f"Total documents in vector store: {stats['document_count']}")
        logger.info(f"Time taken: {time_taken:.2f} seconds")
        logger.info(f"Persist directory: {stats['persist_directory']}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}")
        raise


if __name__ == "__main__":
    # Check for --force flag
    force = "--force" in sys.argv

    if force:
        logger.warning(
            "Force reingestion mode - all existing data will be deleted!")

    # Run ingestion
    asyncio.run(ingest_documents(force=force))
