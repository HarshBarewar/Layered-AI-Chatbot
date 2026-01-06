#!/usr/bin/env python3
"""
Environment setup script for Layered AI Chatbot System
"""
import os
import sys
import subprocess
import venv

def create_virtual_environment():
    """Create and activate virtual environment"""
    venv_path = "venv"
    
    if not os.path.exists(venv_path):
        print("🔧 Creating virtual environment...")
        venv.create(venv_path, with_pip=True)
        print("✅ Virtual environment created!")
    else:
        print("✅ Virtual environment already exists!")
    
    # Get activation script path
    if os.name == 'nt':  # Windows
        activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
        python_exe = os.path.join(venv_path, "Scripts", "python.exe")
    else:  # Unix/Linux/macOS
        activate_script = os.path.join(venv_path, "bin", "activate")
        python_exe = os.path.join(venv_path, "bin", "python")
    
    return python_exe, activate_script

def install_dependencies(python_exe):
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.check_call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        subprocess.check_call([python_exe, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_nltk_data(python_exe):
    """Download required NLTK data"""
    print("📚 Setting up NLTK data...")
    
    nltk_script = '''
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
print("NLTK data downloaded successfully!")
'''
    
    try:
        subprocess.check_call([python_exe, "-c", nltk_script])
        print("✅ NLTK data setup complete!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Warning: NLTK setup failed: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        print("📝 Creating .env file...")
        env_content = """# Layered AI Chatbot System Configuration

# API Configuration (Optional - for enhanced AI responses)
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
        print("✅ .env file created! Please add your API keys.")
    else:
        print("✅ .env file already exists!")

def main():
    """Main setup function"""
    print("🚀 Setting up Layered AI Chatbot System Environment")
    print("=" * 60)
    
    # Create virtual environment
    python_exe, activate_script = create_virtual_environment()
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    if install_dependencies(python_exe):
        # Setup NLTK data
        setup_nltk_data(python_exe)
        
        print("\n🎉 Environment setup complete!")
        print("\n📋 Next steps:")
        print("1. Activate virtual environment:")
        if os.name == 'nt':
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print("2. Add your API keys to .env file (optional)")
        print("3. Run the chatbot: python run.py")
        
        return True
    else:
        print("\n❌ Environment setup failed!")
        return False

if __name__ == "__main__":
    main()