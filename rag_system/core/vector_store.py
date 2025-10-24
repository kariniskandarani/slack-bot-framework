"""
ChromaDB Vector Store Manager
Handles document storage and retrieval using ChromaDB
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

from ..core.config import RAGConfig

logger = logging.getLogger(__name__)

class ChromaVectorStore:
    """ChromaDB vector store for document storage and retrieval"""
    
    def __init__(self, db_path: str = None, collection_name: str = None):
        """
        Initialize ChromaDB vector store
        
        Args:
            db_path: Path to ChromaDB database (default from config)
            collection_name: Name of the collection (default from config)
        """
        if chromadb is None:
            raise ImportError("ChromaDB is required. Install with: pip install chromadb")
        
        if SentenceTransformer is None:
            raise ImportError("SentenceTransformers is required. Install with: pip install sentence-transformers")
        
        self.db_path = db_path or RAGConfig.CHROMA_DB_PATH
        self.collection_name = collection_name or RAGConfig.COLLECTION_NAME
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {RAGConfig.EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(RAGConfig.EMBEDDING_MODEL)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Program documentation for RAG system"}
        )
        
        logger.info(f"ChromaDB initialized at {self.db_path}, collection: {self.collection_name}")
    
    def add_document(self, chunks: List[str], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a document's chunks to the vector store
        
        Args:
            chunks: List of text chunks from the document
            metadata: Document metadata
            
        Returns:
            Dict with status and details
        """
        try:
            if not chunks:
                return {'success': False, 'error': 'No chunks provided'}
            
            # Generate unique IDs for chunks
            base_id = f"{metadata.get('filename', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            chunk_ids = [f"{base_id}_chunk_{i}" for i in range(len(chunks))]
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(chunks)} chunks")
            embeddings = self.embedding_model.encode(chunks).tolist()
            
            # Prepare metadata for each chunk
            chunk_metadata = []
            for i, chunk in enumerate(chunks):
                chunk_meta = {
                    **metadata,  # Original document metadata
                    'chunk_index': i,
                    'chunk_length': len(chunk),
                    'total_chunks': len(chunks),
                    'indexed_at': datetime.now().isoformat(),
                    'chunk_id': chunk_ids[i]
                }
                chunk_metadata.append(chunk_meta)
            
            # Add to ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=chunk_metadata,
                ids=chunk_ids
            )
            
            logger.info(f"Successfully added {len(chunks)} chunks to vector store")
            
            return {
                'success': True,
                'chunks_added': len(chunks),
                'chunk_ids': chunk_ids,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error adding document to vector store: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'chunks_added': 0
            }
    
    def search(self, query: str, n_results: int = None, filter_metadata: Dict = None) -> Dict[str, Any]:
        """
        Search for relevant document chunks
        
        Args:
            query: Search query
            n_results: Number of results to return (default from config)
            filter_metadata: Metadata filters to apply
            
        Returns:
            Dict containing search results and metadata
        """
        try:
            n_results = n_results or RAGConfig.MAX_RESULTS
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Search ChromaDB
            search_params = {
                'query_embeddings': [query_embedding],
                'n_results': n_results
            }
            
            if filter_metadata:
                search_params['where'] = filter_metadata
            
            results = self.collection.query(**search_params)
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i],
                        'id': results['ids'][0][i]
                    })
            
            return {
                'success': True,
                'query': query,
                'results': formatted_results,
                'total_results': len(formatted_results),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            return {
                'success': False,
                'query': query,
                'results': [],
                'total_results': 0,
                'error': str(e)
            }
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            # Get collection info
            collection_count = self.collection.count()
            
            # Get all metadata to analyze
            all_results = self.collection.get()
            
            # Analyze metadata
            files = set()
            file_types = set()
            total_chunks = len(all_results['ids']) if all_results['ids'] else 0
            
            if all_results['metadatas']:
                for metadata in all_results['metadatas']:
                    if 'filename' in metadata:
                        files.add(metadata['filename'])
                    if 'file_type' in metadata:
                        file_types.add(metadata['file_type'])
            
            return {
                'success': True,
                'total_chunks': total_chunks,
                'unique_files': len(files),
                'file_types': list(file_types),
                'files': list(files),
                'collection_name': self.collection_name,
                'db_path': self.db_path
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_document(self, filename: str) -> Dict[str, Any]:
        """
        Delete all chunks from a specific document
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            Dict with deletion status
        """
        try:
            # Find all chunks for this file
            results = self.collection.get(
                where={"filename": filename}
            )
            
            if not results['ids']:
                return {
                    'success': False,
                    'error': f'No chunks found for file: {filename}',
                    'deleted_count': 0
                }
            
            # Delete the chunks
            self.collection.delete(ids=results['ids'])
            
            logger.info(f"Deleted {len(results['ids'])} chunks for file: {filename}")
            
            return {
                'success': True,
                'deleted_count': len(results['ids']),
                'filename': filename,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error deleting document {filename}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'deleted_count': 0
            }
    
    def list_documents(self) -> Dict[str, Any]:
        """
        List all documents in the collection
        
        Returns:
            Dict containing list of documents with their metadata
        """
        try:
            # Get all results
            all_results = self.collection.get()
            
            # Group by filename
            documents = {}
            
            if all_results['metadatas']:
                for metadata in all_results['metadatas']:
                    filename = metadata.get('filename', 'unknown')
                    
                    if filename not in documents:
                        documents[filename] = {
                            'filename': filename,
                            'file_type': metadata.get('file_type', 'unknown'),
                            'file_size_mb': metadata.get('file_size_mb', 0),
                            'total_chunks': 0,
                            'indexed_at': metadata.get('indexed_at', 'unknown')
                        }
                    
                    documents[filename]['total_chunks'] += 1
            
            return {
                'success': True,
                'documents': list(documents.values()),
                'total_documents': len(documents),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            return {
                'success': False,
                'documents': [],
                'total_documents': 0,
                'error': str(e)
            }
    
    def clear_collection(self) -> Dict[str, Any]:
        """Clear all documents from the collection"""
        try:
            # Get all IDs
            all_results = self.collection.get()
            
            if all_results['ids']:
                # Delete all
                self.collection.delete(ids=all_results['ids'])
                deleted_count = len(all_results['ids'])
            else:
                deleted_count = 0
            
            logger.info(f"Cleared {deleted_count} chunks from collection")
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            return {
                'success': False,
                'deleted_count': 0,
                'error': str(e)
            }