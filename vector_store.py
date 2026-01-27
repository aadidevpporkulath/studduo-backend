from typing import List, Dict, Any, Optional
import logging
import hashlib
import asyncio
import threading

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.embeddings import HuggingFaceEmbeddings

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB vector store for document embeddings with async support."""

    def __init__(self, preload: bool = False):
        # Eager or lazy initialization based on preload flag
        self.embeddings = None
        self.client = None
        self.collection = None
        self.collection_name = "notegpt_documents"
        self.query_embedding_cache: Dict[str, List[float]] = {}
        self._initialized = False
        self._init_lock = threading.Lock()

        if preload:
            logger.info("Pre-loading vector store on startup...")
            self._initialize()

    def _initialize(self):
        """Thread-safe initialization of embeddings and ChromaDB."""
        if self._initialized:
            return

        with self._init_lock:
            # Double-check after acquiring lock
            if self._initialized:
                return

            logger.info("Initializing vector store...")
        
        # Load embeddings model (this may take a moment)
        try:
            # Use smaller model for memory efficiency on Render (512MB limit)
            # sentence-transformers/all-MiniLM-L6-v2 is ~90MB vs larger models
            self.embeddings = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2",
                encode_kwargs={"normalize_embeddings": True},
                model_kwargs={"device": "cpu"},
            )
            logger.info("HuggingFace embeddings loaded successfully (all-MiniLM-L6-v2)")
        except Exception as e:
            logger.error(f"Failed to load embeddings: {e}")
            raise

        # Initialize ChromaDB client
        try:
            self.client = chromadb.PersistentClient(
                path=settings.chroma_persist_dir,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise

        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name=self.collection_name
            )
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
        
        self._initialized = True
        logger.info("Vector store initialized successfully")
        self.query_embedding_cache: Dict[str, List[float]] = {}

    async def initialize_async(self):
        """Async initialization wrapper for startup."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._initialize)

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to the vector store."""
        self._initialize()  # Ensure initialized
        
        if not documents:
            logger.warning("No documents to add")
            return

        texts = [doc["text"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]

        # Generate IDs
        ids = [
            f"{doc['metadata']['source']}_{doc['metadata']['chunk_id']}"
            for doc in documents
        ]

        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} documents...")
        embeddings = self.embeddings.embed_documents(texts)

        # Add to ChromaDB in batches
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]

            self.collection.add(
                documents=batch_texts,
                embeddings=batch_embeddings,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
            logger.info(f"Added batch {i//batch_size + 1}")

        logger.info(
            f"Successfully added {len(documents)} documents to vector store")

    def _get_query_cache_key(self, query: str) -> str:
        """Generate cache key for query embedding."""
        return hashlib.md5(query.encode()).hexdigest()

    def _get_cached_embedding(self, query: str) -> Optional[List[float]]:
        """Retrieve cached embedding for a query."""
        cache_key = self._get_query_cache_key(query)
        if cache_key in self.query_embedding_cache:
            logger.debug(f"Cache hit for query embedding: {query[:50]}...")
            return self.query_embedding_cache[cache_key]
        return None

    def _cache_embedding(self, query: str, embedding: List[float]) -> None:
        """Cache embedding for a query."""
        cache_key = self._get_query_cache_key(query)
        self.query_embedding_cache[cache_key] = embedding
        logger.debug(
            f"Cached embedding for query: {query[:50]}... (cache size: {len(self.query_embedding_cache)})")

        # Limit cache size to prevent memory issues (keep last 1000 queries)
        if len(self.query_embedding_cache) > 1000:
            # Remove oldest entries (simple FIFO)
            keys_to_remove = list(self.query_embedding_cache.keys())[:-1000]
            for key in keys_to_remove:
                del self.query_embedding_cache[key]
            logger.info(
                f"Cache pruned. Current size: {len(self.query_embedding_cache)}")

    def similarity_search(
        self,
        query: str,
        k: int = None,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents with embedding caching."""
        self._initialize()  # Ensure initialized
        
        if k is None:
            k = settings.top_k_results

        # Check cache first before generating embedding
        query_embedding = self._get_cached_embedding(query)

        if query_embedding is None:
            # Generate and cache the embedding
            logger.debug(f"Generating embedding for query: {query[:50]}...")
            query_embedding = self.embeddings.embed_query(query)
            self._cache_embedding(query, query_embedding)

        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filter_metadata if filter_metadata else None
        )

        # Format results
        documents = []
        if results and results['documents'] and len(results['documents']) > 0:
            for i, doc_text in enumerate(results['documents'][0]):
                documents.append({
                    "text": doc_text,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else None
                })

        return documents

    async def similarity_search_async(
        self,
        query: str,
        k: int = None,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Async version of similarity search for better concurrency."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.similarity_search, query, k, filter_metadata)

    def delete_collection(self) -> None:
        """Delete the entire collection."""
        self._initialize()  # Ensure initialized
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        self._initialize()  # Ensure initialized
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "persist_directory": settings.chroma_persist_dir
        }


# Singleton instance with preload=True for faster first requests
vector_store = VectorStore(preload=False)  # Will be initialized on app startup
