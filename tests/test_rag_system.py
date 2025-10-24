"""
Test script for RAG System Components
Tests document processing, vector storage, and LLM integration
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag_system.core.config import RAGConfig
from rag_system.processors.document_processor import DocumentProcessor
from rag_system.core.vector_store import ChromaVectorStore
from rag_system.llm.llm_manager import LLMManager
from rag_system.core.rag_engine import RAGEngine

def test_configuration():
    """Test 1: Verify RAG configuration"""
    print("🔧 Test 1: Configuration")
    print("=" * 60)
    
    RAGConfig.print_config_summary()
    validation = RAGConfig.validate_config()
    
    if all(validation.values()):
        print("✅ Configuration is valid\n")
        return True
    else:
        print("❌ Configuration has issues\n")
        return False

def test_document_processor():
    """Test 2: Test document processor with a sample text file"""
    print("\n📄 Test 2: Document Processor")
    print("=" * 60)
    
    try:
        processor = DocumentProcessor()
        
        # Create a sample text file for testing
        test_file_path = "documents/test_sample.txt"
        os.makedirs("documents", exist_ok=True)
        
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write("""
            Program Information
            
            This is a test document for the RAG system.
            
            Eligibility Requirements:
            - Bachelor's degree required
            - Minimum 2 years of professional experience
            - Strong communication skills
            
            Application Process:
            1. Submit online application
            2. Provide official transcripts
            3. Submit three recommendation letters
            4. Complete entrance exam
            
            Financial Aid:
            Financial assistance is available through grants, scholarships, and loans.
            Students must complete the FAFSA form to be considered for financial aid.
            """)
        
        print(f"Created test file: {test_file_path}")
        
        # Process the file
        result = processor.process_file(test_file_path)
        
        if result['success']:
            print(f"✅ Document processed successfully")
            print(f"   File: {result['metadata']['filename']}")
            print(f"   Type: {result['metadata']['file_type']}")
            print(f"   Size: {result['metadata']['file_size_mb']:.3f} MB")
            print(f"   Chunks created: {len(result['chunks'])}")
            print(f"\n   Sample chunk (first 100 chars):")
            print(f"   {result['chunks'][0][:100]}...\n")
            return True
        else:
            print(f"❌ Document processing failed: {result['error']}\n")
            return False
            
    except Exception as e:
        print(f"❌ Error in document processor test: {str(e)}\n")
        return False

def test_vector_store():
    """Test 3: Test vector store operations"""
    print("\n🧮 Test 3: Vector Store")
    print("=" * 60)
    
    try:
        # Initialize vector store
        print("Initializing ChromaDB and embedding model...")
        vector_store = ChromaVectorStore()
        print("✅ Vector store initialized")
        
        # Test adding a document
        test_chunks = [
            "The program requires a bachelor's degree and 2 years of experience.",
            "Financial aid is available through grants and scholarships.",
            "Application deadline is March 15th for fall admission."
        ]
        
        test_metadata = {
            'filename': 'test_doc.txt',
            'file_type': 'txt',
            'file_size_mb': 0.001
        }
        
        print("\nAdding test document...")
        add_result = vector_store.add_document(test_chunks, test_metadata)
        
        if add_result['success']:
            print(f"✅ Document added: {add_result['chunks_added']} chunks")
        else:
            print(f"❌ Failed to add document: {add_result['error']}")
            return False
        
        # Test searching
        print("\nTesting search functionality...")
        search_result = vector_store.search("What are the requirements?", n_results=2)
        
        if search_result['success']:
            print(f"✅ Search successful: {search_result['total_results']} results")
            print(f"\n   Top result:")
            if search_result['results']:
                top_result = search_result['results'][0]
                print(f"   Content: {top_result['content'][:80]}...")
                print(f"   Relevance: {round(1 - top_result['distance'], 3)}")
        else:
            print(f"❌ Search failed: {search_result['error']}")
            return False
        
        # Get stats
        stats = vector_store.get_collection_stats()
        print(f"\n📊 Vector Store Stats:")
        print(f"   Total chunks: {stats['total_chunks']}")
        print(f"   Unique files: {stats['unique_files']}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error in vector store test: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False

def test_llm_manager():
    """Test 4: Test LLM manager"""
    print("\n🤖 Test 4: LLM Manager")
    print("=" * 60)
    
    try:
        llm_manager = LLMManager()
        print(f"✅ LLM Manager initialized with providers: {list(llm_manager.providers.keys())}")
        
        # Test RAG response generation
        test_question = "What are the program requirements?"
        test_context = [
            "The program requires a bachelor's degree and 2 years of professional experience.",
            "Strong communication and analytical skills are essential."
        ]
        
        print(f"\nTesting response generation...")
        print(f"Question: {test_question}")
        
        result = llm_manager.generate_rag_response(test_question, test_context)
        
        if result['success']:
            print(f"✅ Response generated successfully")
            print(f"   Provider: {result['provider']}")
            print(f"   Model: {result['model']}")
            print(f"\n   Response (first 150 chars):")
            print(f"   {result['response'][:150]}...")
            print()
            return True
        else:
            print(f"❌ Response generation failed: {result['error']}\n")
            return False
            
    except Exception as e:
        print(f"❌ Error in LLM manager test: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False

def test_rag_engine():
    """Test 5: Test complete RAG engine"""
    print("\n🎯 Test 5: Complete RAG Engine")
    print("=" * 60)
    
    try:
        # Initialize RAG engine
        print("Initializing RAG Engine...")
        rag_engine = RAGEngine()
        print("✅ RAG Engine initialized")
        
        # Test adding a document
        test_file = "documents/test_sample.txt"
        if os.path.exists(test_file):
            print(f"\nAdding document: {test_file}")
            add_result = rag_engine.add_document(test_file)
            
            if add_result['success']:
                print(f"✅ Document added successfully")
                print(f"   Chunks created: {add_result['chunks_created']}")
                print(f"   Chunks stored: {add_result['chunks_stored']}")
            else:
                print(f"❌ Failed to add document: {add_result['error']}")
                return False
        
        # Test answering a question
        print(f"\nTesting question answering...")
        question = "What are the eligibility requirements?"
        print(f"Question: {question}")
        
        answer_result = rag_engine.answer_question(question, user_id="test_user")
        
        if answer_result['success']:
            print(f"✅ Answer generated successfully")
            print(f"\n   Answer:")
            print(f"   {answer_result['answer']}")
            print(f"\n   Sources used: {answer_result['metadata']['chunks_used']} chunks")
            print(f"   LLM Provider: {answer_result['metadata']['provider']}")
            print()
            return True
        else:
            print(f"❌ Failed to generate answer: {answer_result['error']}\n")
            return False
            
    except Exception as e:
        print(f"❌ Error in RAG engine test: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 RAG System Component Tests")
    print("=" * 60)
    print()
    
    results = {
        'Configuration': test_configuration(),
        'Document Processor': test_document_processor(),
        'Vector Store': test_vector_store(),
        'LLM Manager': test_llm_manager(),
        'RAG Engine': test_rag_engine()
    }
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print("=" * 60)
    print(f"Total: {passed_tests}/{total_tests} tests passed")
    print()
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! RAG system is ready to use.")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")

if __name__ == "__main__":
    main()
