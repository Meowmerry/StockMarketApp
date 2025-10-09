# OpenAI API Quota Issue - Solutions

## 🚨 Problem: "Network error" in Chatbot

When you try to use the chatbot and see:
```
Network error. Please check your connection and try again.
```

This is actually an OpenAI API quota/billing issue, not a network problem.

### The Real Error:
```
Error 429: insufficient_quota
You exceeded your current quota, please check your plan and billing details.
```

---

## ✅ Solutions (Choose One)

### **Solution 1: Add Billing to OpenAI (Recommended for Production)**

**Cost:** Pay-as-you-go, very cheap (~$0.0007 per chat)

**Steps:**
1. Go to https://platform.openai.com/account/billing
2. Click "Add payment method"
3. Add your credit/debit card
4. Set spending limit: $5-10/month (recommended)
5. Wait 5-10 minutes for activation
6. Test: `python test_openai.py`

**Monthly cost estimate:**
- 100 chats = ~$0.07
- 1,000 chats = ~$0.70
- 10,000 chats = ~$7.00

Very affordable! The chatbot uses GPT-3.5-turbo which is the cheapest model.

---

### **Solution 2: Use Mock Chatbot (For Testing)**

**Cost:** FREE

Use the built-in mock chatbot for testing without OpenAI:

#### Enable Mock Mode Locally:

**Option A: Environment Variable**
```bash
# In .env file, add:
USE_MOCK_CHAT=true
```

**Option B: Temporarily Without API Key**
```bash
# In .env file, comment out or remove OPENAI_API_KEY
# OPENAI_API_KEY=sk-...

# The app will automatically use mock service
```

Then run your app:
```bash
python run.py
# Visit http://localhost:5001/chat
```

#### Features of Mock Chatbot:
✅ Works without OpenAI API
✅ Responds to common questions
✅ Uses your actual stock/portfolio data
✅ Perfect for UI/UX testing
✅ Shows disclaimer that it's simulated

#### Limitations:
❌ Responses are pre-programmed, not AI-generated
❌ Limited to stock/portfolio/trading topics
❌ No natural conversation flow

---

### **Solution 3: Create New OpenAI Account (Free Trial)**

If you haven't used the free trial:

1. **Create New OpenAI Account**: https://platform.openai.com/signup
   - Use different email address
   - Get $5 free credits (new accounts only)

2. **Generate API Key**:
   - Go to https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Name it: "Stock Market App"
   - Copy the key (starts with `sk-`)

3. **Update .env File**:
   ```bash
   OPENAI_API_KEY=sk-your-new-key-here
   ```

4. **Test**:
   ```bash
   python test_openai.py
   ```

**Free credits:**
- $5 credit for new accounts
- Expires after 3 months
- Enough for ~7,000 chats!

---

## 🧪 Testing Your Setup

Use the test script to verify:

```bash
python test_openai.py
```

**Expected output:**
```
============================================================
OpenAI API Connection Test
============================================================
✅ API Key found: sk-proj-...xxxx
✅ OpenAI library imported successfully
✅ OpenAI client created successfully

🔄 Testing API call...
✅ API call successful!

AI Response: Hello! API is working!

Tokens used: 28
  - Prompt: 20
  - Completion: 8

============================================================
✅ All tests passed! Your OpenAI API is ready to use.
============================================================
```

---

## 🚀 For Production (Render.com)

Once you have a working OpenAI API key:

### Add to Render Dashboard:

1. **Go to**: https://dashboard.render.com
2. **Select your service**: `stock-market-app`
3. **Click**: Environment tab (left sidebar)
4. **Add environment variable**:
   - **Key**: `OPENAI_API_KEY`
   - **Value**: `sk-your-actual-working-key`
5. **Click**: "Save Changes"
6. Service will automatically redeploy

### Or Use Mock Mode in Production:

To deploy without OpenAI (using mock service):

1. **In Render Dashboard** → Environment:
   - **Key**: `USE_MOCK_CHAT`
   - **Value**: `true`
2. **Save Changes**
3. App will use mock chatbot

---

## 🔍 How to Check Your OpenAI Usage

1. **Visit**: https://platform.openai.com/account/usage
2. **View**:
   - Current month usage
   - Cost per day
   - Total tokens used
   - API calls made

3. **Set Spending Limits**:
   - Go to: https://platform.openai.com/account/billing/limits
   - Set monthly limit: $5, $10, $20, etc.
   - Get email alerts at 75%, 90%, 100%

---

## 💡 Recommendations

**For Development/Testing:**
→ Use **Mock Service** (free, instant)

**For Demo/Portfolio:**
→ Add **$5 to OpenAI** (shows real AI)

**For Production/Launch:**
→ Add **billing with $10-20 limit** (safe, affordable)

---

## 📊 Current Status

Run this to check your setup:

```bash
# Test OpenAI connection
python test_openai.py

# If successful: Use real OpenAI
# If quota error: Use mock service or add billing
```

---

## 🐛 Troubleshooting

### "invalid_api_key"
→ API key is wrong or revoked
→ Generate new key at: https://platform.openai.com/api-keys

### "insufficient_quota"
→ No credits/billing
→ Add payment method or use mock service

### "rate_limit_exceeded"
→ Too many requests
→ Wait 1 minute and try again
→ Consider upgrading plan

### "model_not_found"
→ Using wrong model name
→ Our app uses `gpt-3.5-turbo` (correct)

### Mock service not working
→ Check `USE_MOCK_CHAT=true` in .env
→ Restart Flask app: `python run.py`
→ Check logs for "Using mock chat service"

---

## ✅ Quick Decision Guide

**Do you need AI for...**

| Purpose | Solution | Cost |
|---------|----------|------|
| Just testing UI | Mock Service | Free |
| Showing to friends | Free trial ($5) | Free |
| Personal project | OpenAI with $5 limit | ~$0-5/month |
| Professional demo | OpenAI with $10 limit | ~$2-10/month |
| Production app | OpenAI with $20+ limit | Usage-based |

---

## 📝 Summary

Your chatbot has **2 modes**:

1. **Real AI Mode** (OpenAI GPT-3.5-turbo)
   - Natural conversations
   - Smart responses
   - Requires API key with credits
   - Costs ~$0.0007 per chat

2. **Mock Mode** (Simulated responses)
   - Pre-programmed answers
   - Works offline
   - Free forever
   - Good for testing

**Switch between them** by:
- Adding/removing `OPENAI_API_KEY`
- Setting `USE_MOCK_CHAT=true/false`

---

## 🎯 Next Steps

1. **Choose your solution** from above
2. **Test locally**: `python test_openai.py`
3. **Start app**: `python run.py`
4. **Visit**: http://localhost:5001/chat
5. **Test chatbot** functionality
6. **Deploy to Render** with working API key

---

**Need help?** Check:
- OpenAI Dashboard: https://platform.openai.com/account
- OpenAI Usage: https://platform.openai.com/account/usage
- OpenAI Billing: https://platform.openai.com/account/billing

Good luck! 🚀
