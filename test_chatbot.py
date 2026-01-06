#!/usr/bin/env python3
"""
Simple test script to verify chatbot functionality
"""
import os
import sys

# Clear chat history
def clear_chat_history():
    """Clear existing chat history"""
    chat_file = "data/chat_history.json"
    analytics_file = "data/analytics.json"
    
    if os.path.exists(chat_file):
        os.remove(chat_file)
        print("✅ Cleared chat history")
    
    if os.path.exists(analytics_file):
        os.remove(analytics_file)
        print("✅ Cleared analytics data")

def test_chatbot():
    """Test the chatbot with various questions"""
    try:
        from backend.core import ChatbotCore
        
        print("🤖 Initializing Layered AI Chatbot...")
        chatbot = ChatbotCore()
        
        # Test questions
        test_questions = [
            "Hello, how are you?",
            "What is data science?",
            "Explain machine learning",
            "What is a decision tree classifier?",
            "What are the 7 C's of communication?",
            "Tell me about artificial intelligence",
            "How does Python work?",
            "What is the capital of France?"
        ]
        
        print("\n🧪 Testing chatbot responses:")
        print("=" * 60)
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n--- Test {i}/{len(test_questions)} ---")
            print(f"👤 User: {question}")
            
            response = chatbot.process_message(question, "test_user")
            
            print(f"🤖 Bot: {response['text']}")
            print(f"📊 Strategy: {response['strategy']} | Confidence: {response['confidence']:.2f}")
            print(f"⏱️  Processing Time: {response['processing_time']:.2f}s")
            
            if response['strategy'] == 'generative_ai':
                print("✅ Using AI API")
            elif response['strategy'] == 'enhanced_rule_based':
                print("🔧 Using Enhanced Rules")
            elif response['strategy'] == 'faq':
                print("📚 Using FAQ")
            else:
                print("⚙️  Using Basic Rules")
        
        print("\n" + "=" * 60)
        print("🎉 Test completed successfully!")
        
        # Cleanup
        chatbot.shutdown()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧹 Clearing previous chat history...")
    clear_chat_history()
    
    print("\n🚀 Starting chatbot test...")
    test_chatbot()