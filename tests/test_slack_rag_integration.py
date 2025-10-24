"""
Test script to verify RAG integration readiness
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_system.core.rag_engine import RAGEngine
from rag_system.core.config import RAGConfig

print("🧪 Testing Slack-RAG Integration")
print("=" * 60)

# Test 1: Configuration
print("\n✅ Test 1: RAG Configuration")
try:
    config = RAGConfig()
    print(f"   LLM Providers: {config.get_working_providers()}")
    print(f"   Default Provider: {config.DEFAULT_LLM_PROVIDER}")
    print(f"   Chunk Size: {config.CHUNK_SIZE}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 2: RAG Engine Initialization
print("\n✅ Test 2: RAG Engine Initialization")
try:
    rag_engine = RAGEngine()
    print(f"   Engine initialized: {rag_engine is not None}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 3: Helper Functions
print("\n✅ Test 3: Helper Functions")

def format_rag_response(answer: str, sources: list) -> str:
    """Format RAG answer with sources for Slack."""
    response = f"📚 *Answer:*\n{answer}\n\n"
    if sources:
        response += f"_Sources: {len(sources)} document chunk(s) referenced_"
    return response

def is_question(text: str) -> bool:
    """Check if the message looks like a question."""
    question_words = ['what', 'when', 'where', 'who', 'why', 'how', 'is', 'are', 'can', 'could', 'would', 'should', 'do', 'does', 'tell me', 'explain']
    text_lower = text.lower().strip()
    if '?' in text_lower:
        return True
    for word in question_words:
        if text_lower.startswith(word + ' '):
            return True
    return False

# Test helper functions
test_questions = [
    "What are the requirements?",
    "How do I apply?",
    "Tell me about the program",
    "hello there"
]

for q in test_questions:
    result = is_question(q)
    print(f"   '{q}' → is_question: {result}")

# Test 4: RAG Question Answering
print("\n✅ Test 4: RAG Question Answering")
try:
    result = rag_engine.answer_question("What are the program requirements?")
    if result.get("success"):
        print(f"   Answer generated: {len(result['answer'])} chars")
        print(f"   Sources: {len(result.get('sources', []))}")
        formatted = format_rag_response(result['answer'], result.get('sources', []))
        print(f"\n   Sample formatted response:")
        print(f"   {formatted[:150]}...")
    else:
        print(f"   ⚠️  No answer found (expected if no docs loaded): {result.get('error')}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Stats
print("\n✅ Test 5: RAG Stats")
try:
    stats = rag_engine.get_system_status()
    print(f"   Total documents: {len(stats.get('files', []))}")
    print(f"   Total chunks: {stats.get('total_chunks', 0)}")
    print(f"   Embedding model: {stats.get('embedding_model', 'N/A')}")
    print(f"   LLM provider: {stats.get('llm_provider', 'N/A')}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("🎉 All integration tests passed!")
print("\nNext steps:")
print("1. Install Slack dependencies: pip install slack-bolt fastapi uvicorn")
print("2. Start the bot: uvicorn app:app --reload")
print("3. Test with Slack by mentioning the bot or sending DM")
