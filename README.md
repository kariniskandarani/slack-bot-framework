# RAGDemoBot 🤖📚

A Slack bot powered by RAG (Retrieval-Augmented Generation) that answers questions from your documents using AI. Built with FastAPI, Slack Bolt, ChromaDB, and free LLM APIs.

## 📋 Project Overview

RAGDemoBot combines conversational AI with intelligent document search to provide accurate answers to user questions. The bot:

- **Answers questions** from uploaded PDF, TXT, MD, and CSV documents
- **Cites sources** to show which documents were referenced
- **Uses free LLM APIs** (Google Gemini, Groq) - no expensive local GPU needed
- **Responds to mentions** in channels and **direct messages**
- **Auto-loads documents** from the `documents/` folder on startup

### Technologies

- **FastAPI** - Modern web framework for building APIs
- **Slack Bolt** - Official framework for building Slack apps
- **ChromaDB** - Vector database for semantic document search
- **SentenceTransformers** - Free embeddings model (all-MiniLM-L6-v2)
- **Google Gemini API** - Primary free LLM (1,500 requests/day)
- **Groq API** - Fallback free LLM (llama models)
- **ngrok** - Secure tunneling for local development

## 🏗️ Project Structure

```text
SlackDemoBOT/
├── app.py                     # Main Slack bot application with RAG integration
├── requirements.txt           # Python dependencies
├── .env                      # Environment variables (API keys, tokens)
├── .env.example              # Environment template
├── slack_bot.log             # Application logs
├── README.md                 # This file
├── SLACK_SETUP_MANUAL.md     # Detailed Slack app setup guide
├── documents/                # Place your documents here (PDF, TXT, MD, CSV)
│   └── README.md            # Guide for using documents folder
├── chroma_db/               # ChromaDB vector database (auto-created)
├── rag_system/              # RAG system components
│   ├── __init__.py
│   ├── core/
│   │   ├── config.py        # RAG configuration
│   │   ├── rag_engine.py    # Main RAG orchestrator
│   │   └── vector_store.py  # ChromaDB integration
│   ├── processors/
│   │   └── document_processor.py  # Document parsing & chunking
│   └── llm/
│       └── llm_manager.py   # Multi-provider LLM management
└── tests/                   # Test scripts
    ├── test_rag_system.py              # RAG component tests
    ├── test_slack_rag_integration.py   # Integration tests
    └── check_env.py                    # Environment validation
```

## ⚙️ Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Slack workspace with admin permissions
- ngrok installed
- Google Gemini API key (free tier: https://aistudio.google.com/app/apikey)
- Optional: Groq API key (free tier: https://console.groq.com/)

### 2. Install Dependencies

```bash
# Install all Python packages including RAG dependencies
pip install -r requirements.txt
```

**Core packages:**

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `slack-bolt` - Slack SDK
- `python-dotenv` - Environment variable management

**RAG packages:**

- `chromadb` - Vector database for semantic search
- `sentence-transformers` - Free embedding models
- `google-generativeai` - Google Gemini API
- `groq` - Groq API (fast LLM inference)
- `pypdf2` - PDF document processing
- `pandas` - CSV processing
- `tiktoken` - Token counting

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Slack Configuration
bot_user_oauth_token=xoxb-your-bot-token-here
signing_secret=your-signing-secret-here

# LLM API Keys (get free keys from the providers)
GEMINI_API_KEY=AIzaSy...your-gemini-key-here
GROQ_API_KEY=gsk_...your-groq-key-here  # Optional but recommended
HF_API_KEY=hf_...your-huggingface-key   # Optional

# RAG Configuration (optional - defaults are fine)
DEFAULT_LLM_PROVIDER=gemini
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_RESULTS=5
```

**Where to find these:**

1. **Slack tokens**: Go to [https://api.slack.com/apps](https://api.slack.com/apps)
   - Select your RAGDemoBot app
   - **Bot Token**: OAuth & Permissions → Bot User OAuth Token
   - **Signing Secret**: Basic Information → Signing Secret

2. **Gemini API key** (FREE - 1,500 requests/day):
   - Visit: https://aistudio.google.com/app/apikey
   - Click "Get API key" → "Create API key in new project"
   - Copy the key to your `.env` file

3. **Groq API key** (FREE - 14,400 requests/day):
   - Visit: https://console.groq.com/
   - Sign up and create an API key
   - Copy the key to your `.env` file

4. **HuggingFace token** (Optional - for embedding models):
   - Visit: https://huggingface.co/settings/tokens
   - Create a read token
   - Copy to `.env` file

### 4. Slack App Configuration

📖 **For detailed Slack app setup instructions, see [SLACK_SETUP_MANUAL.md](SLACK_SETUP_MANUAL.md)**

#### Event Subscriptions

1. Go to **Event Subscriptions** in your Slack app settings
2. **Enable Events**: Turn on
3. **Request URL**: `https://your-ngrok-url.ngrok.io/slack/events`
4. **Subscribe to bot events**: Add `app_mention` and `message.im`

#### OAuth Scopes

Required scopes in **OAuth & Permissions**:

- `app_mentions:read` - Read mentions
- `chat:write` - Send messages
- `im:history` - Read direct message history
- `im:read` - View direct message information

#### App Home

Enable direct messaging in **App Home**:

- Check "Allow users to send Slash commands and messages from the messages tab"

## 🚀 Usage

### Starting the Application

#### Step 1: Start FastAPI Server

```bash
# Using uvicorn directly
uvicorn app:app --reload --port 8000
```

#### Step 2: Expose Local Server with ngrok

```bash
# Start ngrok tunnel with verbose logging
ngrok http 8000 --log stdout
```

This will output something like:

```text
started tunnel obj=tunnels name=command_line addr=http://localhost:8000 url=https://abc123.ngrok-free.app
```

#### Step 3: Update Slack Event URL

Copy the ngrok URL and update your Slack app's Event Subscriptions:

- **Request URL**: `https://abc123.ngrok-free.app/slack/events`

### Testing the Bot

#### 1. Add Documents

Add your documents to the `documents/` folder:

```bash
# Supported formats: PDF, TXT, MD, CSV
documents/
├── program_guide.pdf
├── faq.md
├── requirements.txt
└── employee_data.csv
```

The bot will automatically load these documents on startup!

#### 2. Invite the Bot

Invite the bot to a Slack channel where you want to use it.

#### 3. Ask Questions

**In a channel** (mention the bot):

```text
@RAGDemoBot What are the program requirements?
```

**In a direct message** (no mention needed):

```text
What are the eligibility criteria?
```

**Bot response example:**

```text
📚 Answer:
The program requirements for eligibility are:
• A bachelor's degree (Context 1, Context 2)
• Minimum 2 years of professional experience (Context 1, Context 2)
• Strong communication skills (Context 1)

Sources: 4 document chunk(s) referenced
```

#### 4. Use Commands

**Help command:**

```text
@RAGDemoBot help
```

**List documents:**

```text
@RAGDemoBot list-docs
```

**View statistics:**

```text
@RAGDemoBot stats
```

## 🔧 Code Structure Explanation

### RAG System Architecture

```
User Question → Slack → FastAPI → RAG Engine
                                      ↓
              ┌───────────────────────┴──────────────────────┐
              ↓                       ↓                      ↓
    Document Processor      Vector Store              LLM Manager
    (chunk documents)    (semantic search)      (generate answers)
              ↓                       ↓                      ↓
        Text Chunks → Embeddings → ChromaDB → Context → Gemini/Groq
                                                              ↓
                                                      Formatted Answer
                                                              ↓
                                                      Slack Message
```

### Main Components

#### 1. RAG Engine Initialization (`app.py`)

```python
from rag_system.core.rag_engine import RAGEngine
from rag_system.core.config import RAGConfig

# Initialize RAG Engine
rag_engine = RAGEngine()
logger.info(f"RAG providers available: {RAGConfig.get_working_providers()}")

# Auto-load documents from documents/ folder
load_existing_documents()
```

#### 2. Event Listener with RAG

```python
@slack_app.event("app_mention")
def handle_app_mention(event, say, logger):
    message = extract_message_from_mention(event)
    
    # Use RAG to answer questions
    if rag_engine and is_question(message):
        result = rag_engine.answer_question(message)
        
        if result.get("success"):
            response = format_rag_response(
                result["answer"],
                result.get("sources", [])
            )
            say(response)
```

#### 3. RAG Components

**Document Processing** (`rag_system/processors/document_processor.py`):

- Extracts text from PDF, TXT, MD, CSV files
- Chunks text into semantic segments (default: 1000 chars, 200 overlap)
- Preserves context while staying within token limits

**Vector Store** (`rag_system/core/vector_store.py`):

- Stores document embeddings in ChromaDB
- Uses sentence-transformers for free, high-quality embeddings
- Performs cosine similarity search to find relevant chunks

**LLM Manager** (`rag_system/llm/llm_manager.py`):

- Multi-provider support: Gemini (primary), Groq (fallback)
- Automatic fallback if one provider fails
- Rate limiting to stay within free tiers
- Context-aware prompt engineering

**RAG Engine** (`rag_system/core/rag_engine.py`):

- Orchestrates the entire RAG pipeline
- Combines search results with LLM generation
- Formats responses with source citations
```

### Data Flow

```
📱 User asks question in Slack
    ↓
🌐 Slack sends event → ngrok → localhost:8000/slack/events
    ↓
🔧 FastAPI handler → RAG Engine
    ↓
📄 Document Processor: Chunk documents into semantic pieces
    ↓
🧮 Vector Store: Convert chunks to embeddings, store in ChromaDB
    ↓
🔍 Semantic Search: Find most relevant chunks (cosine similarity)
    ↓
🤖 LLM Manager: Send context + question to Gemini/Groq
    ↓
✨ Generate answer with source citations
    ↓
📤 Format for Slack → Send response
    ↓
📱 User sees answer with sources
```

## 🎯 RAG Features

### Supported Document Types

- **PDF** (.pdf) - Extracts text from PDFs using PyPDF2
- **Text** (.txt) - Plain text documents
- **Markdown** (.md) - Markdown formatted documents
- **CSV** (.csv) - Tabular data converted to text

### Free LLM Providers

The bot uses **100% free LLM APIs** with automatic fallback:

1. **Google Gemini** (Primary)
   - Model: `gemini-2.5-flash`
   - Rate limit: 15 requests/min, 1,500 requests/day
   - Fast, high-quality responses

2. **Groq** (Fallback)
   - Models: `llama-3.1-8b-instant`, `llama-3.3-70b-versatile`
   - Rate limit: 30 requests/min, 14,400 requests/day
   - Ultra-fast inference, good quality

### RAG Configuration

All settings in `rag_system/core/config.py` and `.env`:

```python
# Chunking
CHUNK_SIZE = 1000          # Characters per chunk
CHUNK_OVERLAP = 200        # Overlap between chunks

# Search
MAX_RESULTS = 5            # Top-K results for semantic search

# LLM
TEMPERATURE = 0.7          # Response creativity (0-1)
MAX_TOKENS = 500           # Response length limit
MAX_CONTEXT_LENGTH = 4000  # Context sent to LLM
```

## 🧪 Testing

### 1. RAG System Tests

```bash
# Test all RAG components
python tests/test_rag_system.py
```

This validates:
- ✅ Configuration
- ✅ Document processing (PDF, TXT, MD, CSV)
- ✅ Vector storage and search
- ✅ LLM generation
- ✅ End-to-end RAG pipeline

### 2. Integration Tests

```bash
# Test Slack-RAG integration
python tests/test_slack_rag_integration.py
```

### 3. Environment Validation

```bash
# Check API keys and configuration
python tests/check_env.py
```

### 4. Test with Sample Documents

A test document is already in `documents/test_sample.txt`. Try asking:

- "What are the program requirements?"
- "What experience is needed?"
- "How do I qualify?"

## 📝 Logging

The application logs to both console and file:

- **File**: `slack_bot.log`
- **Console**: Real-time output
- **Format**: `timestamp - logger_name - level - message`

Example log entries:

```bash
2025-10-24 12:00:00,000 - app - INFO - Slack app initialized successfully
2025-10-24 12:00:01,000 - app - INFO - RAG Engine initialized successfully
2025-10-24 12:00:01,100 - app - INFO - RAG providers available: ['gemini', 'groq']
2025-10-24 12:00:02,000 - app - INFO - Loading document: program_guide.pdf
2025-10-24 12:00:03,500 - app - INFO - Successfully loaded: program_guide.pdf (15 chunks)
2025-10-24 12:05:30,456 - app - INFO - Processing question from user U12345: What are the requirements?
2025-10-24 12:05:32,789 - app - INFO - RAG response sent to user U12345
```

## 📊 Bot Commands

### In Channels (mention required)

| Command | Description | Example |
|---------|-------------|---------|
| `@bot [question]?` | Ask a question | `@bot What are the program requirements?` |
| `@bot help` | Show help message | `@bot help` |
| `@bot list-docs` | List uploaded documents | `@bot list-docs` |
| `@bot stats` | Show RAG statistics | `@bot stats` |

### In Direct Messages (no mention needed)

| Command | Description | Example |
|---------|-------------|---------|
| `[question]?` | Ask a question | `What are the eligibility criteria?` |
| `help` | Show help message | `help` |
| `list-docs` | List uploaded documents | `list-docs` |
| `stats` | Show RAG statistics | `stats` |

## 🔍 Troubleshooting

### Common Issues

#### 1. **ChromaDB installation fails on Windows**

```bash
# Error: "Microsoft Visual C++ 14.0 or greater is required"
# Solution: Install ChromaDB 1.2.1+ which has pre-built wheels
pip install chromadb --no-build-isolation
```

#### 2. **No answers from RAG**

- Check documents are in `documents/` folder
- Verify documents loaded on startup (check logs)
- Ensure questions relate to document content
- Try running: `python tests/test_rag_system.py`

#### 3. **LLM API errors**

```bash
# Check API keys are valid
python -c "from rag_system.core.config import RAGConfig; print(RAGConfig.get_working_providers())"

# Should show: ['gemini', 'groq']
```

#### 4. **Module not found errors**

```bash
# Ensure virtual environment is activated and dependencies installed
pip install -r requirements.txt
```

#### 5. **Environment variables not loaded**

```bash
# Check .env file exists and has correct format
python tests/check_env.py
```

#### 6. **Slack events not received**

- Verify ngrok URL in Slack Event Subscriptions
- Check ngrok is running: `ngrok http 8000 --log stdout`
- Ensure FastAPI app is running on port 8000

#### 7. **Bot doesn't respond**

- Check bot is installed in the workspace
- Verify `app_mention` and `message.im` events are subscribed
- For direct messages: Ensure "Messages Tab" is enabled in App Home
- Check logs in `slack_bot.log`

#### 8. **Rate limiting**

Free tier limits:
- Gemini: 15 req/min, 1,500 req/day
- Groq: 30 req/min, 14,400 req/day

The bot automatically falls back to Groq if Gemini rate limit is hit.

## 🔐 Security Notes

- Never commit `.env` file to version control
- Rotate Slack tokens regularly
- Use HTTPS in production (ngrok provides this automatically)
- Validate all incoming Slack events

## 📚 Learning Resources

- **[SLACK_SETUP_MANUAL.md](SLACK_SETUP_MANUAL.md)** - Complete step-by-step Slack app creation guide
- [Slack Bolt Python Documentation](https://slack.dev/bolt-python/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Google Gemini API](https://ai.google.dev/docs)
- [Groq API Documentation](https://console.groq.com/docs)
- [SentenceTransformers](https://www.sbert.net/)
- [ngrok Documentation](https://ngrok.com/docs)
- [Slack API Documentation](https://api.slack.com/)

## 🚀 Deployment

### Cloud Deployment Considerations

When deploying to production:

1. **Environment Variables**: Use secrets manager (AWS Secrets Manager, Azure Key Vault, etc.)
2. **Database**: Consider persistent ChromaDB storage or cloud vector databases
3. **Webhooks**: Replace ngrok with permanent HTTPS endpoint
4. **Rate Limiting**: Implement request queuing for high traffic
5. **Document Updates**: Add API endpoints for document management
6. **Monitoring**: Set up logging aggregation and alerting

### Docker Deployment (Future)

```dockerfile
# Dockerfile example
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests for new functionality
4. Ensure all tests pass (`python tests/test_rag_system.py`)
5. Update documentation
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Submit a pull request

---

Built with ❤️ using FastAPI, Slack Bolt, ChromaDB, and free LLM APIs (Gemini, Groq)
