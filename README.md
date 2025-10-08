# RAGDemoBot 🤖

A Slack bot built with FastAPI and Slack Bolt framework that responds to mentions and direct messages with friendly greetings.

## 📋 Project Overview

RAGDemoBot is a simple yet powerful Slack bot that demonstrates the integration between:

- **FastAPI** - Modern web framework for building APIs
- **Slack Bolt** - Official framework for building Slack apps
- **ngrok** - Secure tunneling for local development
- **Python** - Core programming language

The bot listens for mentions in Slack channels and responds with personalized greetings. It also supports direct messaging, making it perfect for learning Slack bot development or as a foundation for more complex bots.

## 🏗️ Project Structure

```text
SlackDemoBOT/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create this)
├── slack_bot.log         # Application logs
├── README.md             # Project documentation
└── tests/                # Test directory
    ├── __init__.py
    ├── check_env.py          # Environment validation script
```

## ⚙️ Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Slack workspace with admin permissions
- ngrok installed

### 2. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt
```

**Required packages:**

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `slack-bolt` - Slack SDK
- `python-dotenv` - Environment variable management

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
bot_user_oauth_token=xoxb-your-bot-token-here
signing_secret=your-signing-secret-here
```

**Where to find these:**

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Select your RAGDemoBot app
3. **Bot Token**: OAuth & Permissions → Bot User OAuth Token
4. **Signing Secret**: Basic Information → Signing Secret

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

1. **Invite the bot** to a Slack channel
2. **Mention the bot**: `@RAGDemoBot hello there!`
3. **Expected response**: `Hi @yourname! How can I help you?`
4. **Send a direct message**: Open a DM with the bot and type `Hello!`
5. **Expected DM response**: `Hi @yourname, you sent me a DM: "Hello!"`

## 🔧 Code Structure Explanation

### Main Components

#### 1. Application Setup (`app.py`)

```python
# FastAPI app instance
app = FastAPI()

# Slack Bolt app instance
slack_app = App(
    token=os.getenv("bot_user_oauth_token"),
    signing_secret=os.getenv("signing_secret")
)

# Bridge between FastAPI and Slack Bolt
handler = SlackRequestHandler(slack_app)
```

#### 2. Event Listener

```python
@slack_app.event("app_mention")
def handle_app_mention(event, say, logger):
    # Responds when someone mentions the bot
    user = event["user"]
    say(f"Hi <@{user}>! How can I help you?")

@slack_app.event("message")
def handle_direct_message(event, say, logger):
    # Responds to direct messages
    if event.get("channel_type") == "im" and "user" in event:
        user = event["user"]
        text = event.get("text", "")
        say(f"Hi <@{user}>, you sent me a DM: \"{text}\"")
```

#### 3. HTTP Endpoint

```python
@app.post("/slack/events")
async def slack_events(request: Request):
    # Main endpoint that receives ALL events from Slack
    return await handler.handle(request)
```

### Data Flow

```bash
👤 User mentions bot OR sends DM → 📨 Slack sends event → 🌐 ngrok forwards to localhost:8000
                                                        ↓
🚪 /slack/events endpoint → 🔧 handler.handle() → 🎯 Event listener triggered
                                                  ↓
🤖 Bot processes → 📤 Response sent → 📱 User sees reply in Slack
```

## 🧪 Testing

### Environment Validation

```bash
# Quick environment check
python check_env.py
```

## 📝 Logging

The application logs to both console and file:

- **File**: `slack_bot.log`
- **Console**: Real-time output
- **Format**: `timestamp - logger_name - level - message`

Example log entries:

```bash
2025-09-27 23:43:11,807 - app - INFO - Slack app initialized successfully
2025-09-27 23:43:15,234 - app - INFO - Responded to app mention from user U12345
2025-10-09 00:15:30,456 - app - INFO - Received DM from user U12345: Hello bot!
```

## 🔍 Troubleshooting

### Common Issues

#### 1. **Module not found errors**

```bash
# Ensure virtual environment is activated
pip install -r requirements.txt
```

#### 2. **Environment variables not loaded**

```bash
# Check .env file exists and has correct format
python check_env.py
```

#### 3. **Slack events not received**

- Verify ngrok URL in Slack Event Subscriptions
- Check ngrok is running: `ngrok http 8000 --log stdout`
- Ensure FastAPI app is running on port 8000

#### 4. **Bot doesn't respond**

- Check bot is installed in the workspace
- Verify `app_mention` and `message.im` events are subscribed
- For direct messages: Ensure "Messages Tab" is enabled in App Home
- Check logs in `slack_bot.log`

#### 5. **Direct messages don't work**

- Enable "Allow users to send messages from the messages tab" in App Home
- Add `im:history` and `im:read` OAuth scopes
- Subscribe to `message.im` event
- Reinstall bot after making changes

## 🔐 Security Notes

- Never commit `.env` file to version control
- Rotate Slack tokens regularly
- Use HTTPS in production (ngrok provides this automatically)
- Validate all incoming Slack events

## 📚 Learning Resources

- **[SLACK_SETUP_MANUAL.md](SLACK_SETUP_MANUAL.md)** - Complete step-by-step Slack app creation guide
- [Slack Bolt Python Documentation](https://slack.dev/bolt-python/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ngrok Documentation](https://ngrok.com/docs)
- [Slack API Documentation](https://api.slack.com/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

---
Built with ❤️ using FastAPI, Slack Bolt, and ngrok
