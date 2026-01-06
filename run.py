#!/usr/bin/env python3
"""
Main run script for Layered AI Chatbot System
"""
import os
import sys
import subprocess
import argparse
import threading
import time

def setup_environment():
    """Setup the environment and install dependencies"""
    print("🔧 Setting up Layered AI Chatbot System...")
    
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    # Check if .env file exists and has valid API keys
    env_path = '.env'
    if os.path.exists(env_path):
        from dotenv import load_dotenv
        load_dotenv()
        
        hf_key = os.getenv('HUGGINGFACE_API_KEY')
        or_key = os.getenv('OPENROUTER_API_KEY')
        
        if hf_key and hf_key != 'your_huggingface_key_here':
            print("✅ Hugging Face API key found")
        else:
            print("⚠️ Hugging Face API key not configured (will use rule-based responses)")
            
        if or_key and or_key != 'your_openrouter_key_here':
            print("✅ OpenRouter API key found")
        else:
            print("⚠️ OpenRouter API key not configured (will use rule-based responses)")
    else:
        print("⚠️ .env file not found - creating template")
        create_env_template()
    
    # Install requirements
    try:
        print("📦 Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    
    # Download NLTK data
    try:
        print("📚 Downloading NLTK data...")
        import nltk
        import ssl
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context
            
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        nltk.download('vader_lexicon', quiet=True)
        print("✅ NLTK data downloaded successfully!")
    except Exception as e:
        print(f"⚠️ Warning: Could not download NLTK data: {e}")
    
    return True

def create_env_template():
    """Create .env template file"""
    env_content = """# Layered AI Chatbot System Configuration

# API Configuration (Optional - for enhanced AI responses)
# Get your keys from:
# Hugging Face: https://huggingface.co/settings/tokens
# OpenRouter: https://openrouter.ai/keys
HUGGINGFACE_API_KEY=your_huggingface_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# System Configuration
CONFIDENCE_THRESHOLD=0.6
MAX_CONVERSATION_HISTORY=10
RESPONSE_TIMEOUT=30

# Analytics Configuration
ANALYTICS_RETENTION_DAYS=30
MAX_STORED_INTERACTIONS=10000

# Learning Configuration
LEARNING_ENABLED=True
AUTO_OPTIMIZATION=True

# API Server Configuration
API_HOST=localhost
API_PORT=5000
API_DEBUG=False

# Streamlit Configuration
STREAMLIT_PORT=8501
STREAMLIT_HOST=localhost
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    print("📝 Created .env template file")

def test_system():
    """Test the layered chatbot system"""
    print("🧪 Testing Layered AI Chatbot System...")
    
    try:
        # Import and test core functionality
        from backend.core import ChatbotCore
        
        print("🔄 Initializing all layers...")
        chatbot = ChatbotCore()
        
        # Test messages
        test_messages = [
            "Hello, how are you?",
            "What is the PM of India?",
            "I'm feeling sad today",
            "Can you help me with something?",
            "Thank you for your assistance"
        ]
        
        print("\n🤖 Testing layered processing:")
        for i, message in enumerate(test_messages, 1):
            print(f"\n--- Test {i}/5 ---")
            print(f"👤 User: {message}")
            
            start_time = time.time()
            response = chatbot.process_message(message, "test_user")
            processing_time = time.time() - start_time
            
            print(f"🤖 Bot: {response['text']}")
            print(f"📊 Metadata:")
            print(f"   • Intent: {response['intent']} (confidence: {response['intent_confidence']:.2f})")
            print(f"   • Sentiment: {response['sentiment']['sentiment']}")
            print(f"   • Strategy: {response['strategy']}")
            print(f"   • Success: {'✅' if response['success'] else '❌'}")
            print(f"   • Processing Time: {processing_time:.3f}s")
        
        print("\n📊 Getting system analytics...")
        analytics = chatbot.get_analytics_dashboard()
        print(f"   • Total Conversations: {analytics['conversation_stats']['total_conversations']}")
        print(f"   • Success Rate: {analytics['response_effectiveness']['overall_success_rate']:.1f}%")
        
        print("\n🧠 Getting learning insights...")
        learning = chatbot.get_learning_insights()
        suggestions = learning.get('optimization_suggestions', [])
        print(f"   • Optimization Suggestions: {len(suggestions)}")
        
        print("\n✅ All layers tested successfully!")
        
        # Cleanup
        chatbot.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_streamlit():
    """Run the Streamlit frontend"""
    print("🚀 Starting Layered AI Chatbot System...")
    print("📱 Opening Streamlit interface...")
    
    try:
        # Run Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "frontend/app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down Layered AI Chatbot System...")
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")

def run_api_server():
    """Run the Flask API server"""
    print("🌐 Starting API server...")
    
    try:
        from backend.core import ChatbotCore
        from backend.api_layer import APILayer
        
        # Initialize core system
        core = ChatbotCore()
        
        # Initialize API layer
        api = APILayer(core)
        
        # Run API server
        api.run(host='localhost', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down API server...")
    except Exception as e:
        print(f"❌ Error running API server: {e}")

def run_full_system():
    """Run both Streamlit frontend and API server"""
    print("🚀 Starting Full Layered AI Chatbot System...")
    
    # Start API server in a separate thread
    api_thread = threading.Thread(target=run_api_server, daemon=True)
    api_thread.start()
    
    # Give API server time to start
    time.sleep(3)
    
    # Start Streamlit frontend
    run_streamlit()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Layered AI Chatbot System")
    parser.add_argument("--setup", action="store_true", help="Setup environment and install dependencies")
    parser.add_argument("--test", action="store_true", help="Test the layered chatbot system")
    parser.add_argument("--streamlit", action="store_true", help="Run Streamlit interface only")
    parser.add_argument("--api", action="store_true", help="Run API server only")
    parser.add_argument("--full", action="store_true", help="Run both Streamlit and API server")
    
    args = parser.parse_args()
    
    # If no arguments provided, show help and run setup + streamlit
    if not any(vars(args).values()):
        print("🤖 Layered AI Chatbot System")
        print("=" * 50)
        print("Architecture: 9 specialized layers working together")
        print("Frontend: Streamlit with real-time analytics")
        print("Backend: Modular, extensible, production-ready")
        print("=" * 50)
        
        # Setup environment
        if setup_environment():
            print("\n🧪 Running system test...")
            if test_system():
                print("\n🚀 Starting Streamlit interface...")
                run_streamlit()
        return
    
    # Handle specific arguments
    if args.setup:
        setup_environment()
    
    if args.test:
        test_system()
    
    if args.streamlit:
        run_streamlit()
    
    if args.api:
        run_api_server()
    
    if args.full:
        run_full_system()

if __name__ == "__main__":
    main()