# AI Chatbot Setup Guide

This guide explains how to set up and use the AI chatbot feature in the Stock Market App.

## 🚀 Quick Start

### 1. Get OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up or log in
3. Navigate to "API Keys" section
4. Click "Create new secret key"
5. Copy the key (you won't be able to see it again!)

### 2. Configure Environment Variable

**Local Development:**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
OPENAI_API_KEY=sk-your-actual-api-key-here
```

**Render.com Production:**
1. Go to your Render dashboard
2. Select your web service
3. Go to "Environment" tab
4. Add environment variable:
   - Key: `OPENAI_API_KEY`
   - Value: `sk-your-actual-api-key-here`
5. Click "Save Changes"
6. Service will redeploy automatically

### 3. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements (includes openai>=1.12.0)
pip install -r requirements.txt
```

### 4. Initialize Database

The ChatMessage model needs to be added to your database:

```bash
# Run the app - it will create tables automatically
python run.py

# Or use the init script
python init_db.py
```

## 🎯 Features

### What the Chatbot Can Do

✅ **Educational Support:**
- Explain stock market concepts and terminology
- Answer questions about investing basics
- Provide information about stocks in the database

✅ **Portfolio Context (When Logged In):**
- Summarize your current holdings
- Explain your recent trades
- Help interpret your portfolio performance

✅ **Safe & Responsible:**
- Built-in safety filters
- Refuses to give personalized investment advice
- Clear disclaimers about educational purpose

### What the Chatbot Won't Do

❌ **Prohibited Actions:**
- Give personalized stock recommendations
- Predict stock prices
- Provide financial planning advice
- Recommend specific buy/sell actions

## 💬 Using the Chatbot

### Option 1: Full Chat Page

Visit `/chat` in your browser for a dedicated chat interface with:
- Full conversation history
- Quick question buttons
- Clear chat functionality
- Responsive design

### Option 2: Floating Widget

- Look for the purple chat button in the bottom-right corner
- Available on all pages
- Click to open a compact chat window
- Minimize when not in use

### Example Questions

Try asking:
- "What stocks are available in the app?"
- "Explain what a stock portfolio is"
- "How do I interpret my P&L?"
- "What's the difference between buy and sell orders?"
- "Can you summarize my current holdings?" (when logged in)

## 🔧 Configuration

### chat_prompts.py

Contains system prompts and templates. Customize to:
- Modify the chatbot's personality
- Add domain-specific knowledge
- Adjust safety filters
- Change response style

### chat_service.py

Handles OpenAI API integration. Configure:
- `model`: Default is "gpt-3.5-turbo" (cost-effective)
- `max_tokens`: Response length limit (default: 500)
- `temperature`: Creativity level (default: 0.7)

Example customization:
```python
self.model = "gpt-4"  # Use GPT-4 for better responses (more expensive)
self.max_tokens = 1000  # Allow longer responses
self.temperature = 0.5  # More consistent, less creative
```

## 🛡️ Security Best Practices

1. **Never Commit API Keys:**
   - `.env` is in `.gitignore`
   - Use environment variables only
   - Don't hardcode keys in source code

2. **API Key Rotation:**
   - Rotate keys periodically
   - Delete unused keys from OpenAI dashboard
   - Monitor usage in OpenAI dashboard

3. **Cost Management:**
   - Set usage limits in OpenAI dashboard
   - Monitor API usage regularly
   - GPT-3.5-turbo is more cost-effective than GPT-4

## 🧪 Testing Without API Key

The chatbot includes fallback functionality:

```python
# Without API key, users see:
"I'm sorry, but the AI chatbot is not configured properly.
Please contact the administrator to set up the OpenAI API key."
```

This allows you to:
- Test the UI without an API key
- Deploy without immediate costs
- Demonstrate the feature to stakeholders

## 📊 Database Schema

### ChatMessage Table

```python
class ChatMessage(db.Model):
    id = Integer (Primary Key)
    user_id = Integer (Foreign Key to User, nullable)
    session_id = String(64) (Indexed)
    role = String(10) ('user' or 'assistant')
    content = Text
    timestamp = DateTime (Indexed)
```

### Conversation Tracking

- Each browser session gets a unique `session_id`
- Messages stored for history/analytics
- Anonymous users supported (user_id is nullable)
- Limit: Last 10 messages sent to OpenAI for context

## 🐛 Troubleshooting

### "API key not configured" Error

**Solution:**
```bash
# Check if .env exists
ls -la .env

# Verify API key is set
cat .env | grep OPENAI_API_KEY

# Restart the server after adding key
python run.py
```

### "Rate limit exceeded" Error

**Cause:** Too many requests to OpenAI API

**Solution:**
1. Wait a few minutes
2. Upgrade OpenAI plan if needed
3. Implement request throttling

### Chat Widget Not Showing

**Check:**
1. `base.html` includes widget template
2. JavaScript console for errors
3. Browser compatibility (modern browsers only)

### Responses Are Slow

**Causes:**
- OpenAI API latency
- Network issues
- Using GPT-4 (slower than GPT-3.5)

**Solutions:**
- Use GPT-3.5-turbo for speed
- Reduce `max_tokens`
- Add loading indicators (already implemented)

## 💰 Cost Estimation

**GPT-3.5-turbo Pricing (as of 2024):**
- Input: ~$0.0005 per 1K tokens
- Output: ~$0.0015 per 1K tokens

**Average message:**
- User message: ~50 tokens
- System prompt with context: ~300 tokens
- Response: ~150 tokens
- **Total per conversation: ~$0.0007**

**Monthly estimates:**
- 100 conversations: ~$0.07
- 1,000 conversations: ~$0.70
- 10,000 conversations: ~$7.00

Set spending limits in your OpenAI dashboard!

## 📚 Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [OpenAI Pricing](https://openai.com/pricing)
- [Best Practices for Prompting](https://platform.openai.com/docs/guides/prompt-engineering)
- [Safety Best Practices](https://platform.openai.com/docs/guides/safety-best-practices)

## 🤝 Support

If you encounter issues:
1. Check the logs for error messages
2. Verify API key configuration
3. Review OpenAI dashboard for API errors
4. Check network connectivity

---

**Built with ❤️ using OpenAI GPT and Flask**
