# 🚀 Quick Start Guide - Layered AI Chatbot

## Option 1: Simple Setup (Recommended)

### Step 1: Run the System
```bash
python run.py
```
This will automatically:
- Install all dependencies
- Set up NLTK data
- Create .env template
- Test the system
- Launch the Streamlit interface

### Step 2: Add API Keys (Optional but Recommended)
1. Open the `.env` file created in your project directory
2. Replace the placeholder values with your actual API keys:
   ```env
   HUGGINGFACE_API_KEY=hf_your_actual_key_here
   OPENROUTER_API_KEY=sk-or-v1-your_actual_key_here
   ```
3. Get your API keys from:
   - **Hugging Face**: https://huggingface.co/settings/tokens (Free)
   - **OpenRouter**: https://openrouter.ai/keys (Free tier available)

### Step 3: Restart and Enjoy!
```bash
python run.py
```

---

## Option 2: Virtual Environment Setup (Production)

### Step 1: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 2: Run Setup Script
```bash
python setup_environment.py
```

### Step 3: Run the Chatbot
```bash
python run.py
```

---

## 🎯 Usage Options

### Streamlit Interface Only
```bash
python run.py --streamlit
```
Access at: http://localhost:8501

### API Server Only
```bash
python run.py --api
```
Access at: http://localhost:5000

### Full System (Both)
```bash
python run.py --full
```

### Test System
```bash
python run.py --test
```

---

## 🔧 Troubleshooting

### "Module not found" errors:
```bash
pip install -r requirements.txt
```

### NLTK data issues:
```bash
python -c "import nltk; nltk.download('all')"
```

### API not working:
- Check your .env file has valid API keys
- System works without API keys using rule-based responses
- Verify internet connection for API calls

---

## 🤖 What You Can Ask

### General Questions
- "Hello, how are you?"
- "What can you help me with?"

### Technical Questions
- "What is data science?"
- "Explain machine learning"
- "What is artificial intelligence?"
- "Tell me about Python programming"

### Current Affairs
- "Who is the PM of India?"
- "What is the best AI model?"

### The system will provide intelligent responses using:
1. **API-powered responses** (if keys configured) - Most accurate
2. **Enhanced rule-based responses** - Good for technical topics
3. **FAQ matching** - Quick answers for common questions
4. **Fallback responses** - Graceful handling of edge cases

---

## 🎨 Features You'll See

- **Real-time Chat**: Instant responses with metadata
- **Analytics Dashboard**: Performance metrics and insights
- **Sentiment Analysis**: Emotion detection in conversations
- **Intent Recognition**: Understanding what users want
- **Learning System**: Continuous improvement over time

---

## 📊 System Architecture

The chatbot uses a 9-layer architecture:
1. **API Layer** - HTTP endpoints
2. **Preprocessing** - Text cleaning
3. **NLP Layer** - Intent & entity recognition
4. **Sentiment Layer** - Emotion analysis
5. **Decision Engine** - Strategy selection
6. **Response Layer** - Answer generation
7. **Storage Layer** - Data persistence
8. **Analytics Layer** - Performance tracking
9. **Learning Layer** - Continuous improvement

---

## 🆘 Need Help?

1. Check the main README.md for detailed documentation
2. Run `python run.py --test` to diagnose issues
3. Check the Streamlit sidebar for system health
4. All components work offline with rule-based responses

**Enjoy your AI chatbot! 🎉**