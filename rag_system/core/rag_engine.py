"""
RAG Engine - Main orchestrator for the RAG system
Combines document processing, vector search, and LLM generation
"""

import logging
from typing import Dict, Any, List, Optional
from ..processors.document_processor import DocumentProcessor
from ..core.vector_store import ChromaVectorStore
from ..llm.llm_manager import LLMManager
from ..core.config import RAGConfig

logger = logging.getLogger(__name__)

class RAGEngine:
    """Main RAG engine that orchestrates the entire pipeline"""
    
    def __init__(self):
        """Initialize RAG engine with all components"""
        try:
            # Initialize components
            self.document_processor = DocumentProcessor()
            self.vector_store = ChromaVectorStore()
            self.llm_manager = LLMManager()
            
            logger.info("RAG Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG Engine: {str(e)}")
            raise
    
    def add_document(self, file_path: str) -> Dict[str, Any]:
        """
        Add a document to the RAG system
        
        Args:
            file_path: Path to the document to add
            
        Returns:
            Dict with processing results
        """
        try:
            logger.info(f"Adding document: {file_path}")
            
            # Step 1: Process the document
            processing_result = self.document_processor.process_file(file_path)
            
            if not processing_result['success']:
                return {
                    'success': False,
                    'error': f"Document processing failed: {processing_result['error']}",
                    'stage': 'processing'
                }
            
            # Step 2: Add to vector store
            vector_result = self.vector_store.add_document(
                chunks=processing_result['chunks'],
                metadata=processing_result['metadata']
            )
            
            if not vector_result['success']:
                return {
                    'success': False,
                    'error': f"Vector storage failed: {vector_result['error']}",
                    'stage': 'vector_storage'
                }
            
            # Success
            result = {
                'success': True,
                'filename': processing_result['metadata']['filename'],
                'file_type': processing_result['metadata']['file_type'],
                'file_size_mb': processing_result['metadata']['file_size_mb'],
                'chunks_created': len(processing_result['chunks']),
                'chunks_stored': vector_result['chunks_added'],
                'error': None
            }
            
            logger.info(f"Successfully added document: {result['filename']} ({result['chunks_created']} chunks)")
            return result
            
        except Exception as e:
            logger.error(f"Error adding document {file_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'stage': 'unknown'
            }
    
    def add_documents_from_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Add all supported documents from a directory
        
        Args:
            directory_path: Path to directory containing documents
            
        Returns:
            Dict with batch processing results
        """
        try:
            logger.info(f"Processing directory: {directory_path}")
            
            # Process all files in directory
            processing_results = self.document_processor.process_directory(directory_path)
            
            results = {
                'success': True,
                'total_files': len(processing_results),
                'successful_files': 0,
                'failed_files': 0,
                'file_results': [],
                'errors': []
            }
            
            # Add each file to vector store
            for file_result in processing_results:
                if file_result['success']:
                    # Add to vector store
                    vector_result = self.vector_store.add_document(
                        chunks=file_result['chunks'],
                        metadata=file_result['metadata']
                    )
                    
                    if vector_result['success']:
                        results['successful_files'] += 1
                        results['file_results'].append({
                            'filename': file_result['metadata']['filename'],
                            'success': True,
                            'chunks': len(file_result['chunks'])
                        })
                    else:
                        results['failed_files'] += 1
                        results['file_results'].append({
                            'filename': file_result['metadata']['filename'],
                            'success': False,
                            'error': vector_result['error']
                        })
                        results['errors'].append(f"{file_result['metadata']['filename']}: {vector_result['error']}")
                else:
                    results['failed_files'] += 1
                    results['file_results'].append({
                        'filename': file_result.get('file_path', 'unknown'),
                        'success': False,
                        'error': file_result['error']
                    })
                    results['errors'].append(f"{file_result.get('file_path', 'unknown')}: {file_result['error']}")
            
            logger.info(f"Directory processing complete: {results['successful_files']}/{results['total_files']} files successful")
            return results
            
        except Exception as e:
            logger.error(f"Error processing directory {directory_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'total_files': 0,
                'successful_files': 0,
                'failed_files': 0
            }
    
    def answer_question(self, question: str, user_id: str = None, 
                       filter_metadata: Dict = None) -> Dict[str, Any]:
        """
        Answer a question using RAG
        
        Args:
            question: User's question
            user_id: ID of the user asking (for logging)
            filter_metadata: Optional metadata filters for search
            
        Returns:
            Dict containing answer and metadata
        """
        try:
            logger.info(f"Answering question from user {user_id}: {question[:100]}...")
            
            # Step 1: Search for relevant context
            search_result = self.vector_store.search(
                query=question,
                n_results=RAGConfig.MAX_RESULTS,
                filter_metadata=filter_metadata
            )
            
            if not search_result['success']:
                return {
                    'success': False,
                    'answer': "Sorry, I encountered an error while searching for relevant information.",
                    'error': search_result['error'],
                    'stage': 'search'
                }
            
            # Check if we found any relevant context
            if not search_result['results']:
                return {
                    'success': True,
                    'answer': "I couldn't find any relevant information in the available documents to answer your question. Please try rephrasing your question or check if the relevant documents have been uploaded.",
                    'sources': [],
                    'context_found': False
                }
            
            # Step 2: Extract context chunks
            context_chunks = [result['content'] for result in search_result['results']]
            
            # Step 3: Generate answer using LLM
            llm_result = self.llm_manager.generate_rag_response(
                question=question,
                context_chunks=context_chunks
            )
            
            if not llm_result['success']:
                return {
                    'success': False,
                    'answer': "Sorry, I'm having trouble generating a response right now. Please try again later.",
                    'error': llm_result['error'],
                    'stage': 'generation'
                }
            
            # Step 4: Prepare sources information
            sources = []
            for result in search_result['results']:
                source_info = {
                    'filename': result['metadata'].get('filename', 'Unknown'),
                    'file_type': result['metadata'].get('file_type', 'Unknown'),
                    'chunk_index': result['metadata'].get('chunk_index', 0),
                    'relevance_score': round(1 - result['distance'], 3)  # Convert distance to relevance
                }
                sources.append(source_info)
            
            # Success response
            response = {
                'success': True,
                'answer': llm_result['response'],
                'sources': sources,
                'context_found': True,
                'metadata': {
                    'provider': llm_result['provider'],
                    'model': llm_result['model'],
                    'chunks_used': len(context_chunks),
                    'total_sources': len(sources),
                    'question': question,
                    'user_id': user_id
                },
                'error': None
            }
            
            logger.info(f"Successfully answered question using {len(context_chunks)} chunks from {len(set(s['filename'] for s in sources))} documents")
            return response
            
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return {
                'success': False,
                'answer': "Sorry, I encountered an unexpected error while processing your question.",
                'error': str(e),
                'stage': 'unknown'
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            # Get vector store stats
            vector_stats = self.vector_store.get_collection_stats()
            
            # Get LLM stats
            llm_stats = self.llm_manager.get_usage_stats()
            
            # Validate configuration
            config_status = RAGConfig.validate_config()
            
            return {
                'success': True,
                'system_healthy': all(config_status.values()) and vector_stats['success'],
                'vector_store': vector_stats,
                'llm_providers': llm_stats,
                'configuration': config_status,
                'rag_config': {
                    'chunk_size': RAGConfig.CHUNK_SIZE,
                    'chunk_overlap': RAGConfig.CHUNK_OVERLAP,
                    'max_results': RAGConfig.MAX_RESULTS,
                    'embedding_model': RAGConfig.EMBEDDING_MODEL
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'system_healthy': False
            }
    
    def list_documents(self) -> Dict[str, Any]:
        """List all documents in the system"""
        return self.vector_store.list_documents()
    
    def delete_document(self, filename: str) -> Dict[str, Any]:
        """Delete a document from the system"""
        return self.vector_store.delete_document(filename)
    
    def clear_all_documents(self) -> Dict[str, Any]:
        """Clear all documents from the system"""
        return self.vector_store.clear_collection()