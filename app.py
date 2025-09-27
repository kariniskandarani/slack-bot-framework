from fastapi import FastAPI, Request, HTTPException
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from dotenv import load_dotenv
import os
import logging

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

# Example event listener
@slack_app.event("app_mention")
def handle_app_mention(event, say, logger):
    """Handle app mention events."""
    # This function runs whenever someone mentions your bot in Slack (like "@MyBot hello")
    # It receives the message data, responds with a greeting, and logs the interaction
    try:
        user = event["user"]
        say(f"Hi <@{user}>! How can I help you?")
        logger.info(f"Responded to app mention from user {user}")
    except Exception as e:
        logger.error(f"Error in app mention: {e}")
        say("Sorry, something went wrong. Please try again.")

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

