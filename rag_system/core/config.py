"""
RAG System Configuration
Centralized configuration for the RAG system
"""

import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

class RAGConfig:
    """Configuration class for RAG system"""
    
    # LLM Provider Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    HF_API_KEY = os.getenv("HF_API_KEY") 
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # LLM Model Configuration
    GEMINI_MODEL = "gemini-2.5-flash"
    GROQ_FAST_MODEL = "llama-3.1-8b-instant"
    GROQ_PREMIUM_MODEL = "llama-3.3-70b-versatile"
    
    # Default LLM Provider (primary choice)
    DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "gemini")
    
    # Document Processing Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    MAX_RESULTS = int(os.getenv("MAX_RESULTS", "5"))
    
    # ChromaDB Configuration
    CHROMA_DB_PATH = "./chroma_db"
    COLLECTION_NAME = "program_documents"
    
    # Embedding Model Configuration
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Free, fast, good quality
    
    # File Processing Configuration
    SUPPORTED_EXTENSIONS = [".pdf", ".txt", ".md", ".csv"]
    MAX_FILE_SIZE_MB = 50
    
    # RAG Response Configuration
    MAX_CONTEXT_LENGTH = 4000  # Maximum context to send to LLM
    TEMPERATURE = 0.7
    MAX_TOKENS = 500
    
    # Rate Limiting Configuration
    GEMINI_RATE_LIMIT = {
        "requests_per_minute": 15,
        "requests_per_day": 1500
    }
    
    GROQ_RATE_LIMIT = {
        "requests_per_minute": 30,
        "requests_per_day": 14400
    }
    
    # Slack Configuration
    SLACK_MAX_MESSAGE_LENGTH = 3000  # Slack's message limit
    
    @classmethod
    def get_working_providers(cls) -> List[str]:
        """Return list of configured LLM providers"""
        providers = []
        if cls.GEMINI_API_KEY:
            providers.append("gemini")
        if cls.GROQ_API_KEY:
            providers.append("groq")
        return providers
    
    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """Validate configuration and return status"""
        status = {
            "has_llm_provider": bool(cls.get_working_providers()),
            "has_chroma_path": bool(cls.CHROMA_DB_PATH),
            "chunk_size_valid": cls.CHUNK_SIZE > 0,
            "overlap_valid": 0 <= cls.CHUNK_OVERLAP < cls.CHUNK_SIZE,
        }
        return status
    
    @classmethod
    def print_config_summary(cls):
        """Print configuration summary for debugging"""
        print("🔧 RAG System Configuration:")
        print(f"   Working LLM Providers: {cls.get_working_providers()}")
        print(f"   Default Provider: {cls.DEFAULT_LLM_PROVIDER}")
        print(f"   Chunk Size: {cls.CHUNK_SIZE}")
        print(f"   Chunk Overlap: {cls.CHUNK_OVERLAP}")
        print(f"   ChromaDB Path: {cls.CHROMA_DB_PATH}")
        print(f"   Embedding Model: {cls.EMBEDDING_MODEL}")
        
        validation = cls.validate_config()
        print(f"   Configuration Valid: {all(validation.values())}")
        
        if not all(validation.values()):
            print("   Issues found:")
            for key, valid in validation.items():
                if not valid:
                    print(f"     ❌ {key}")