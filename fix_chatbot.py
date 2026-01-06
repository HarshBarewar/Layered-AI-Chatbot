#!/usr/bin/env python3
"""
Fix script to resolve intent classification issues
"""
import os

def fix_chatbot():
    """Fix the chatbot intent classification and response issues"""
    print("🔧 Fixing Layered AI Chatbot Issues...")
    
    # Step 1: Clear old data
    print("1️⃣ Clearing old data...")
    files_to_clear = [
        "data/chat_history.json",
        "data/analytics.json", 
        "models/intent_model.pkl"
    ]
    
    for file_path in files_to_clear:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"   ✅ Cleared {file_path}")
    
    # Step 2: Test intent classification
    print("\n2️⃣ Testing intent classification...")
    try:
        from backend.nlp_layer import NLPLayer
        nlp = NLPLayer()
        
        # Test critical cases
        test_cases = [
            "what is machine learning?",
            "tell me about machine learning", 
            "explain artificial intelligence",
            "what is data science"
        ]
        
        for text in test_cases:
            intent, confidence = nlp.classify_intent(text)
            status = "✅" if intent == "question" else "❌"
            print(f"   {status} '{text}' → {intent} ({confidence:.2f})")
            
    except Exception as e:
        print(f"   ❌ Intent test failed: {e}")
        return False
    
    # Step 3: Test full system
    print("\n3️⃣ Testing full system...")
    try:
        from backend.core import ChatbotCore
        chatbot = ChatbotCore()
        
        # Test a machine learning question
        response = chatbot.process_message("what is machine learning?", "test_user")
        
        print(f"   Question: what is machine learning?")
        print(f"   Intent: {response['intent']} (confidence: {response['intent_confidence']:.2f})")
        print(f"   Strategy: {response['strategy']}")
        print(f"   Response: {response['text'][:100]}...")
        
        if response['intent'] == 'question' and response['strategy'] != 'rule_based':
            print("   ✅ System working correctly!")
            success = True
        else:
            print("   ❌ System still has issues!")
            success = False
            
        chatbot.shutdown()
        return success
        
    except Exception as e:
        print(f"   ❌ System test failed: {e}")
        return False

def main():
    """Main fix function"""
    print("🚀 Layered AI Chatbot Fix Script")
    print("=" * 50)
    
    if fix_chatbot():
        print("\n🎉 Chatbot fixed successfully!")
        print("\n📋 Next steps:")
        print("1. Run: python run.py")
        print("2. Ask: 'what is machine learning?'")
        print("3. Should get proper AI/enhanced response")
    else:
        print("\n❌ Fix failed. Check the errors above.")

if __name__ == "__main__":
    main()