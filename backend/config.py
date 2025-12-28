"""
Configuration Layer - System settings and constants
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """System configuration and constants"""
    
    # API Configuration
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
    
    # System Settings
    CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '0.6'))
    MAX_CONVERSATION_HISTORY = int(os.getenv('MAX_CONVERSATION_HISTORY', '10'))
    RESPONSE_TIMEOUT = int(os.getenv('RESPONSE_TIMEOUT', '30'))
    
    # File Paths
    DATA_DIR = 'data'
    MODELS_DIR = 'models'
    CHAT_HISTORY_FILE = os.path.join(DATA_DIR, 'chat_history.json')
    ANALYTICS_FILE = os.path.join(DATA_DIR, 'analytics.json')
    INTENT_MODEL_FILE = os.path.join(MODELS_DIR, 'intent_model.pkl')
    
    # Intent Categories
    INTENTS = {
        'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon'],
        'goodbye': ['bye', 'goodbye', 'see you', 'farewell', 'exit'],
        'question': ['what', 'how', 'when', 'where', 'why', 'who', 'pm', 'prime minister'],
        'help': ['help', 'assist', 'support', 'guide', 'can you'],
        'complaint': ['problem', 'issue', 'error', 'bug', 'broken', 'not working'],
        'compliment': ['good', 'great', 'excellent', 'amazing', 'thank you', 'thanks'],
        'general': ['tell me', 'information', 'about', 'explain', 'describe']
    }
    
    # Response Templates
    RESPONSES = {
        'greeting': [
            "Hello! How can I help you today?",
            "Hi there! What can I do for you?",
            "Greetings! I'm here to assist you."
        ],
        'goodbye': [
            "Goodbye! Have a great day!",
            "See you later! Take care!",
            "Farewell! Feel free to return anytime."
        ],
        'help': [
            "I'm here to help! What do you need assistance with?",
            "How can I assist you today?",
            "I'd be happy to help you with your questions."
        ],
        'question': [
            "That's an interesting question. Let me help you with that.",
            "I'd be happy to answer your question.",
            "The Prime Minister of India is Narendra Modi, serving since 2014."
        ],
        'complaint': [
            "I understand your concern. How can I help resolve this?",
            "I'm sorry to hear about this issue. Let me assist you.",
            "I appreciate you bringing this to my attention."
        ],
        'compliment': [
            "Thank you! I'm glad I could be helpful.",
            "I appreciate your kind words!",
            "Thank you! It's my pleasure to assist you."
        ],
        'general': [
            "I'd be happy to provide information about that.",
            "Let me share what I know about this topic.",
            "Here's what I can tell you about that."
        ]
    }
    
    # FAQ Database
    FAQ_DATABASE = {
        'what is pm of india': 'The Prime Minister of India is Narendra Modi, who has been serving since May 2014.',
        'who is prime minister': 'The current Prime Minister of India is Narendra Modi.',
        'pm india': 'Narendra Modi is the Prime Minister of India.',
        'best ai model': 'Some of the best AI models include GPT-4, Claude, Gemini, and LLaMA. Each excels in different areas like reasoning, coding, or creativity.',
        'ai model': 'Popular AI models include OpenAI GPT series, Google Gemini, Anthropic Claude, and Meta LLaMA.',
        'leader of inc': 'The current president of the Indian National Congress (INC) is Mallikarjun Kharge, elected in October 2022.',
        'inc leader': 'Mallikarjun Kharge is the current president of the Indian National Congress.',
        'rahul gandhi': 'Rahul Gandhi is an Indian politician and member of the Indian National Congress. He served as Congress President from 2017-2019 and is currently a Member of Parliament.',
        'rahul gandhi details': 'Rahul Gandhi is the son of Sonia Gandhi and late Rajiv Gandhi. He represents Wayanad constituency in Lok Sabha and is a prominent opposition leader in India.',
        'what time is it': 'I cannot access real-time information, but you can check your device clock.',
        'how are you': 'I am functioning well and ready to help you!',
        'what can you do': 'I can answer questions, provide information, and have conversations with you.'
    }