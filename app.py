from fastapi import FastAPI, Request, HTTPException
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from dotenv import load_dotenv
import os
import logging
from pathlib import Path

# Import RAG system components
from rag_system.core.rag_engine import RAGEngine
from rag_system.core.config import RAGConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('slack_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

# Initialize Slack Bolt app
try:
    slack_app = App(
        token=os.getenv("bot_user_oauth_token"),
        signing_secret=os.getenv("signing_secret")
    )
    logger.info("Slack app initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Slack app: {e}")
    raise

handler = SlackRequestHandler(slack_app)
app = FastAPI()

# Initialize RAG Engine
try:
    rag_engine = RAGEngine()
    logger.info("RAG Engine initialized successfully")
    logger.info(f"RAG providers available: {RAGConfig.get_working_providers()}")
except Exception as e:
    logger.error(f"Failed to initialize RAG Engine: {e}")
    rag_engine = None

# Auto-load documents from documents folder on startup
def load_existing_documents():
    """Load all documents from the documents folder into RAG system."""
    if not rag_engine:
        logger.warning("RAG engine not available, skipping document loading")
        return
    
    docs_folder = Path("documents")
    if not docs_folder.exists():
        logger.warning("Documents folder does not exist")
        return
    
    supported_extensions = ['.pdf', '.txt', '.md', '.csv']
    loaded_count = 0
    
    for file_path in docs_folder.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            try:
                logger.info(f"Loading document: {file_path.name}")
                result = rag_engine.add_document(str(file_path))
                if result.get("success"):
                    loaded_count += 1
                    logger.info(f"Successfully loaded: {file_path.name} ({result.get('chunks_created', 0)} chunks)")
                else:
                    logger.error(f"Failed to load {file_path.name}: {result.get('error')}")
            except Exception as e:
                logger.error(f"Error loading {file_path.name}: {e}")
    
    logger.info(f"Document loading complete: {loaded_count} files loaded")

# Load documents on startup
load_existing_documents()

# Helper function to format RAG response for Slack
def format_rag_response(answer: str, sources: list) -> str:
    """Format RAG answer with sources for Slack."""
    response = f"📚 *Answer:*\n{answer}\n\n"
    
    if sources:
        response += f"_Sources: {len(sources)} document chunk(s) referenced_"
    
    return response

# Helper function to check if user is asking a question
def is_question(text: str) -> bool:
    """Check if the message looks like a question."""
    question_words = ['what', 'when', 'where', 'who', 'why', 'how', 'is', 'are', 'can', 'could', 'would', 'should', 'do', 'does', 'tell me', 'explain']
    text_lower = text.lower().strip()
    
    # Check for question mark
    if '?' in text_lower:
        return True
    
    # Check for question words at the start
    for word in question_words:
        if text_lower.startswith(word + ' '):
            return True
    
    return False


# Example event listener
@slack_app.event("app_mention")
def handle_app_mention(event, say, logger):
    """Handle app mention events with RAG-powered responses."""
    try:
        user = event["user"]
        text = event.get("text", "")
        
        # Remove the bot mention from the text
        # Extract just the user's message
        message = text.split(">", 1)[-1].strip()
        
        # Check for admin commands
        if message.lower().startswith("help"):
            help_text = """
*📚 RAG-Powered Slack Bot - Commands*

*Asking Questions:*
• Just mention me with your question: `@bot What are the program requirements?`
• I'll search through uploaded documents and provide answers with sources

*Admin Commands:*
• `@bot help` - Show this help message
• `@bot list-docs` - List all uploaded documents
• `@bot stats` - Show RAG system statistics

*Tips:*
• Ask specific questions for better answers
• Make sure relevant documents are uploaded to the `documents/` folder
• I support PDF, TXT, MD, and CSV files
            """
            say(help_text)
            logger.info(f"Sent help message to user {user}")
            return
        
        if message.lower().startswith("list-docs"):
            if rag_engine:
                stats = rag_engine.get_system_status()
                files = stats.get("files", [])
                
                if files:
                    docs_list = "*📄 Uploaded Documents:*\n\n"
                    for file in files:
                        docs_list += f"• `{file}`\n"
                    say(docs_list)
                else:
                    say("📭 No documents uploaded yet. Add documents to the `documents/` folder.")
            else:
                say("❌ RAG system not available.")
            logger.info(f"Listed documents for user {user}")
            return
        
        if message.lower().startswith("stats"):
            if rag_engine:
                stats = rag_engine.get_system_status()
                stats_text = f"""
*📊 RAG System Statistics*

• Total documents: {len(stats.get('files', []))}
• Total chunks: {stats.get('total_chunks', 0)}
• Embedding model: `{stats.get('embedding_model', 'N/A')}`
• LLM provider: `{stats.get('llm_provider', 'N/A')}`
                """
                say(stats_text)
            else:
                say("❌ RAG system not available.")
            logger.info(f"Sent stats to user {user}")
            return
        
        # If RAG is available and it looks like a question, use RAG
        if rag_engine and (is_question(message) or len(message.split()) > 3):
            try:
                logger.info(f"Processing question from user {user}: {message}")
                result = rag_engine.answer_question(message)
                
                if result.get("success"):
                    response = format_rag_response(
                        result["answer"],
                        result.get("sources", [])
                    )
                    say(response)
                    logger.info(f"RAG response sent to user {user}")
                else:
                    say(f"❌ Sorry, I couldn't find an answer: {result.get('error', 'Unknown error')}")
                    logger.error(f"RAG error for user {user}: {result.get('error')}")
            except Exception as e:
                logger.error(f"Error generating RAG response: {e}")
                say("❌ Sorry, something went wrong while processing your question. Please try again.")
        else:
            # Fallback response if RAG is not available or message is too short
            say(f"Hi <@{user}>! Ask me a question about the program and I'll help you find the answer! Type `@bot help` for more info.")
        
        logger.info(f"Responded to app mention from user {user}")
    except Exception as e:
        logger.error(f"Error in app mention: {e}")
        say("Sorry, something went wrong. Please try again.")

@slack_app.event("message")
def handle_direct_message(event, say, logger):
    """Handle direct messages with RAG-powered responses."""
    # Only respond to direct messages (IMs)
    if event.get("channel_type") == "im" and "user" in event:
        user = event["user"]
        text = event.get("text", "")
        logger.info(f"Received DM from user {user}: {text}")
        
        # Check for help command
        if text.lower().strip() in ["help", "?", "commands"]:
            help_text = """
*📚 RAG-Powered Slack Bot - DM Commands*

*Asking Questions:*
• Just type your question directly: `What are the program requirements?`
• I'll search through uploaded documents and provide answers with sources

*Commands:*
• `help` - Show this help message
• `list-docs` - List all uploaded documents
• `stats` - Show RAG system statistics

*Tips:*
• Ask specific questions for better answers
• Make sure relevant documents are uploaded to the `documents/` folder
• I support PDF, TXT, MD, and CSV files
            """
            say(help_text)
            logger.info(f"Sent DM help message to user {user}")
            return
        
        if text.lower().strip() == "list-docs":
            if rag_engine:
                stats = rag_engine.get_system_status()
                files = stats.get("files", [])
                
                if files:
                    docs_list = "*📄 Uploaded Documents:*\n\n"
                    for file in files:
                        docs_list += f"• `{file}`\n"
                    say(docs_list)
                else:
                    say("📭 No documents uploaded yet. Add documents to the `documents/` folder.")
            else:
                say("❌ RAG system not available.")
            logger.info(f"Listed documents in DM for user {user}")
            return
        
        if text.lower().strip() == "stats":
            if rag_engine:
                stats = rag_engine.get_system_status()
                stats_text = f"""
*📊 RAG System Statistics*

• Total documents: {len(stats.get('files', []))}
• Total chunks: {stats.get('total_chunks', 0)}
• Embedding model: `{stats.get('embedding_model', 'N/A')}`
• LLM provider: `{stats.get('llm_provider', 'N/A')}`
                """
                say(stats_text)
            else:
                say("❌ RAG system not available.")
            logger.info(f"Sent stats in DM to user {user}")
            return
        
        # Use RAG for questions
        if rag_engine and len(text.strip()) > 0:
            try:
                logger.info(f"Processing DM question from user {user}: {text}")
                result = rag_engine.answer_question(text)
                
                if result.get("success"):
                    response = format_rag_response(
                        result["answer"],
                        result.get("sources", [])
                    )
                    say(response)
                    logger.info(f"RAG response sent in DM to user {user}")
                else:
                    say(f"❌ Sorry, I couldn't find an answer: {result.get('error', 'Unknown error')}")
                    logger.error(f"RAG error in DM for user {user}: {result.get('error')}")
            except Exception as e:
                logger.error(f"Error generating RAG response in DM: {e}")
                say("❌ Sorry, something went wrong while processing your question. Please try again.")
        else:
            say(f"Hi <@{user}>! Ask me a question and I'll help you find the answer! Type `help` for more info.")

@app.post("/slack/events")
async def slack_events(request: Request):
    """Handle Slack events."""
    # This is the main endpoint that receives ALL events from Slack
    # It acts as a gateway - when Slack sends any event (mentions, messages, etc.)
    # it comes through this endpoint and gets routed to the right handler
    try:
        return await handler.handle(request)
    except Exception as e:
        logger.error(f"Error processing Slack event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

