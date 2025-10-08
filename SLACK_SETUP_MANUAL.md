# 📖 Slack App Setup Manual for RAGDemoBot

This manual provides step-by-step instructions for creating and configuring your RAGDemoBot Slack application from scratch.

## 🚀 Prerequisites

Before starting, ensure you have:

- [ ] Admin access to a Slack workspace
- [ ] RAGDemoBot code running locally
- [ ] ngrok installed and running
- [ ] Your ngrok URL ready (e.g., `https://abc123.ngrok-free.app`)

## 📋 Part 1: Creating Your Slack App

### Step 1: Create New Slack App

1. **Go to Slack API website**: [https://api.slack.com/apps](https://api.slack.com/apps)
2. **Click**: "Create New App"
3. **Choose**: "From scratch"
4. **App Name**: Enter `RAGDemoBot`
5. **Pick a workspace**: Select your development workspace
6. **Click**: "Create App"

🎉 **Success!** You now have a basic Slack app created.

---

## ⚙️ Part 2: Basic Information Setup

### Step 2: Configure App Basic Information

1. **Navigate to**: "Basic Information" (should be selected by default)
2. **App Credentials**: You'll see important information here:
   - **App ID**: Keep this for reference
   - **Client ID**: Keep this for reference  
   - **Client Secret**: Keep this secure
   - **Signing Secret**: **COPY THIS** - you'll need it for your `.env` file
   - **Verification Token**: Not needed for Bolt apps

3. **Display Information** (optional but recommended):
   - **App name**: RAGDemoBot
   - **Short description**: "A demo bot that responds to mentions"
   - **Long description**: Add detailed description
   - **App icon**: Upload an icon if desired
   - **Background color**: Choose your preferred color

---

## 🔐 Part 3: OAuth & Permissions Setup

### Step 3: Configure OAuth Scopes

1. **Navigate to**: "OAuth & Permissions" (left sidebar)
2. **Scroll down to**: "Scopes" section
3. **Under "Bot Token Scopes"**, click "Add an OAuth Scope"
4. **Add these required scopes**:

   | Scope | Description | Why Needed |
   |-------|-------------|------------|
   | `app_mentions:read` | View messages that directly mention @your_bot | **CRITICAL**: Without this, your bot won't receive mention events |
   | `chat:write` | Send messages as RAGDemoBot | **CRITICAL**: Without this, your bot can't respond to users |
   | `im:history` | View messages in direct messages | **REQUIRED**: For direct message functionality |
   | `im:read` | View basic information about direct messages | **REQUIRED**: For direct message functionality |

5. **Optional but recommended scopes**:

   | Scope | Description | When Useful |
   |-------|-------------|-------------|
   | `channels:read` | View basic information about public channels | If you want to know channel names |
   | `users:read` | View people in the workspace | If you want to get user information |

⚠️ **Important**: The scopes `app_mentions:read` and `chat:write` are **MANDATORY** for your bot to work!

### Step 4: Install App to Workspace

1. **Scroll up** to "OAuth Tokens for Your Workspace"
2. **Click**: "Install to Workspace"
3. **Review permissions** and click "Allow"
4. **Copy the Bot User OAuth Token**: It starts with `xoxb-`
   - **SAVE THIS TOKEN** - you'll need it for your `.env` file

---

## 🎯 Part 4: Event Subscriptions Setup

### Step 5: Enable Event Subscriptions

1. **Navigate to**: "Event Subscriptions" (left sidebar)
2. **Turn on**: "Enable Events" toggle

### Step 6: Configure Request URL

🌐 **This is where ngrok comes in!**

1. **Request URL field**: Enter your ngrok URL + `/slack/events`

   ```text
   https://your-ngrok-url.ngrok.io/slack/events
   ```

   **Example**: If your ngrok shows:

   ```shell
   Forwarding https://abc123def456.ngrok-free.app -> http://localhost:8000
   ```

   Then enter:

   ```text
   https://abc123def456.ngrok-free.app/slack/events
   ```

2. **Verification**: Slack will send a challenge request to verify your URL
   - ✅ **Success**: You'll see a green checkmark ✓ Verified
   - ❌ **Failed**: Check that your FastAPI app is running and ngrok is forwarding properly

⚠️ **Troubleshooting URL Verification**:

- Ensure your FastAPI app is running: `uvicorn app:app --reload --port 8000`
- Ensure ngrok is running: `ngrok http 8000 --log stdout`
- Check your code has the `/slack/events` endpoint

### Step 7: Subscribe to Bot Events

📝 **This step is CRITICAL and matches your code!**

1. **Scroll down** to "Subscribe to bot events" section
2. **Click**: "Add Bot User Event"
3. **Add these events**:
   - `app_mention` (for channel mentions)
   - `message.im` (for direct messages)

**Why this matters**: Your code has these event listeners:

```python
@slack_app.event("app_mention")  # ← This matches the app_mention subscription
def handle_app_mention(event, say, logger):
    # Your bot's response to mentions

@slack_app.event("message")      # ← This matches the message.im subscription
def handle_direct_message(event, say, logger):
    # Your bot's response to direct messages
```

**Click**: "Save Changes"

---

## 💬 Part 5: Enable Direct Messages

### Step 8: Configure App Home for Direct Messages

🚨 **IMPORTANT**: This step is required for direct messaging to work!

1. **Navigate to**: "App Home" (left sidebar)
2. **Scroll down** to "Show Tabs" section
3. **Enable Messages Tab**:
   - ✅ Check "Allow users to send Slash commands and messages from the messages tab"
4. **Click**: "Save Changes"

⚠️ **Without this step**: Users will see "Sending messages to this app has been turned off" when trying to DM your bot.

---

## 🎯 Part 6: Code-to-Config Mapping

### Understanding the Connection

Your **code** and **Slack configuration** must match:

| Code Component | Slack Configuration | Purpose |
|----------------|-------------------|---------|
| `@slack_app.event("app_mention")` | Event Subscriptions → `app_mention` | Bot receives mention events |
| `@slack_app.event("message")` | Event Subscriptions → `message.im` | Bot receives direct messages |
| `say()` function | OAuth Scopes → `chat:write` | Bot can send messages |
| `event["user"]` | OAuth Scopes → `app_mentions:read` + `im:history` | Bot can read mention and DM details |
| `/slack/events` endpoint | Request URL | Where Slack sends events |
| Messages Tab | App Home → "Allow users to send messages" | Enables direct messaging |

---

## 📋 Part 7: Environment Variables Setup

### Step 9: Update Your .env File

Create or update your `.env` file with the tokens from Slack:

```env
# From OAuth & Permissions → Bot User OAuth Token
bot_user_oauth_token=xoxb-YOUR-BOT-TOKEN-GOES-HERE

# From Basic Information → Signing Secret  
signing_secret=your-signing-secret-goes-here
```

⚠️ **Security Notes**:

- Never commit `.env` file to version control
- Keep these tokens secret
- Regenerate tokens if compromised

---

## 🧪 Part 8: Testing Your Setup

### Step 10: Test the Configuration

#### Test 1: Invite Bot to Channel

1. **Go to any Slack channel**
2. **Type**: `/invite @RAGDemoBot`
3. **Or**: Go to channel details → Members → Add people → Search for RAGDemoBot

#### Test 2: Mention the Bot

1. **In the channel, type**: `@RAGDemoBot hello`
2. **Expected response**: `Hi @yourname! How can I help you?`

#### Test 3: Test Direct Messages

1. **Click on your bot** in the "Apps" section or "Direct messages"
2. **Send a message**: `Hello bot!`
3. **Expected response**: `Hi @yourname, you sent me a DM: "Hello bot!"`

#### Test 4: Check Logs

Monitor your application logs for:

```text
2025-09-27 23:43:15,234 - app - INFO - Responded to app mention from user U12345
2025-10-09 00:15:30,456 - app - INFO - Received DM from user U12345: Hello bot!
```

---

## 🔍 Part 9: Troubleshooting Guide

### Common Issues and Solutions

#### ❌ **URL Verification Failed**

**Problem**: Request URL shows error
**Solutions**:

- ✅ Check FastAPI is running: `http://localhost:8000`
- ✅ Check ngrok is running: `ngrok http 8000 --log stdout`
- ✅ Verify URL format: `https://abc123.ngrok-free.app/slack/events`
- ✅ Check firewall isn't blocking port 8000

#### ❌ **Bot Doesn't Respond to Mentions**

**Problem**: Bot is silent when mentioned
**Check these in order**:

1. ✅ **Event subscription**: Is `app_mention` added?
2. ✅ **OAuth scopes**: Do you have `app_mentions:read` and `chat:write`?
3. ✅ **Bot installation**: Is bot installed to workspace?
4. ✅ **Bot invitation**: Is bot added to the channel?
5. ✅ **Code running**: Is your FastAPI app running?
6. ✅ **ngrok running**: Is ngrok tunnel active?

#### ❌ **Bot Doesn't Respond to Direct Messages**

**Problem**: Shows "Sending messages to this app has been turned off"
**Solutions**:

1. ✅ **App Home**: Go to App Home → Enable "Allow users to send messages from the messages tab"
2. ✅ **Event subscription**: Add `message.im` event
3. ✅ **OAuth scopes**: Add `im:history` and `im:read` scopes
4. ✅ **Reinstall**: Reinstall bot to workspace after changes
5. ✅ **Code check**: Ensure you have `@slack_app.event("message")` handler

#### ❌ **Permission Errors**

**Problem**: Bot responds with permission errors
**Solutions**:

- ✅ Re-check OAuth scopes in "OAuth & Permissions"
- ✅ Reinstall bot to workspace after adding scopes
- ✅ Verify bot token starts with `xoxb-`

#### ❌ **ngrok URL Changes**

**Problem**: ngrok URL changes every restart
**Solutions**:

- ✅ Update Request URL in Event Subscriptions
- ✅ Consider ngrok paid plan for static URLs
- ✅ Use ngrok config file for consistency

---

## 📝 Part 10: Verification Checklist

Before going live, verify:

### Slack App Configuration

- [ ] App created with name "RAGDemoBot"
- [ ] Signing secret copied to `.env` file
- [ ] OAuth scopes: `app_mentions:read`, `chat:write`, `im:history`, `im:read` added
- [ ] Bot token copied to `.env` file (starts with `xoxb-`)
- [ ] App installed to workspace
- [ ] Event subscriptions enabled
- [ ] Request URL verified: `https://your-ngrok-url.ngrok.io/slack/events`
- [ ] Bot events `app_mention` and `message.im` subscribed
- [ ] App Home: Messages tab enabled ("Allow users to send messages")

### Local Development Setup

- [ ] FastAPI app running on port 8000
- [ ] ngrok tunnel running: `ngrok http 8000 --log stdout`
- [ ] `.env` file has correct tokens
- [ ] Bot responds to mentions: `@RAGDemoBot hello`
- [ ] Bot responds to direct messages
- [ ] Logs show successful responses

### Code-Config Alignment

- [ ] Code has `@slack_app.event("app_mention")` ← matches app_mention subscription
- [ ] Code has `@slack_app.event("message")` ← matches message.im subscription
- [ ] Code has `/slack/events` endpoint ← matches Request URL
- [ ] Code uses `say()` function ← requires `chat:write` scope
- [ ] Code reads `event["user"]` ← requires `app_mentions:read` and `im:history` scopes

---

## 🚀 Part 11: Next Steps

Once your bot is working:

1. **Add more event types**: `message`, `reaction_added`, etc.
2. **Add slash commands**: Create interactive commands
3. **Add interactive components**: Buttons, modals, etc.
4. **Deploy to production**: Use a cloud service instead of ngrok
5. **Add database**: Store user preferences and data
6. **Implement OAuth flow**: For multi-workspace installation

---

## 📞 Support

If you encounter issues:

1. **Check logs** in `slack_bot.log`
2. **Verify configuration** using this checklist
3. **Test connectivity**: Can you reach `http://localhost:8000/health`?
4. **Check Slack API docs**: [https://api.slack.com/](https://api.slack.com/)
5. **Review ngrok logs**: Look for request/response details

---

**🎉 Congratulations!** Your RAGDemoBot should now be fully functional and responding to mentions in Slack!
