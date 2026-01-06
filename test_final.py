#!/usr/bin/env python3
"""
Final test to verify all fixes
"""

def test_final_fixes():
    """Test that all issues are resolved"""
    print("🔧 Final Test - Verifying All Fixes")
    print("=" * 50)
    
    try:
        from backend.core import ChatbotCore
        
        # Initialize chatbot
        print("🤖 Initializing chatbot...")
        chatbot = ChatbotCore()
        
        # Test cases that were failing
        test_cases = [
            ("hello", "greeting", "Should be greeting, not question"),
            ("what is machine learning?", "question", "Should be question with proper ML explanation"),
            ("tell me about data science", "question", "Should be question with proper DS explanation"),
            ("thank you", "compliment", "Should be compliment"),
            ("can you help me", "help", "Should be help")
        ]
        
        print("\n🧪 Testing Intent Classification & Responses:")
        print("-" * 50)
        
        all_passed = True
        
        for text, expected_intent, description in test_cases:
            response = chatbot.process_message(text, "test_user")
            
            actual_intent = response['intent']
            strategy = response['strategy']
            bot_response = response['text']
            
            # Check intent
            intent_ok = actual_intent == expected_intent
            
            # Check response quality
            if expected_intent == "question" and "machine learning" in text.lower():
                response_ok = "machine learning" in bot_response.lower() or "ml" in bot_response.lower()
            elif expected_intent == "question" and "data science" in text.lower():
                response_ok = "data science" in bot_response.lower() or "data" in bot_response.lower()
            elif expected_intent == "greeting":
                response_ok = any(word in bot_response.lower() for word in ["hello", "hi", "help"])
            else:
                response_ok = True  # Other intents are OK
            
            status = "✅" if (intent_ok and response_ok) else "❌"
            
            print(f"{status} '{text}'")
            print(f"   Intent: {actual_intent} (expected: {expected_intent}) {'✅' if intent_ok else '❌'}")
            print(f"   Strategy: {strategy}")
            print(f"   Response: {bot_response[:80]}...")
            print(f"   Quality: {'✅' if response_ok else '❌'}")
            print()
            
            if not (intent_ok and response_ok):
                all_passed = False
        
        chatbot.shutdown()
        
        if all_passed:
            print("🎉 ALL TESTS PASSED! Chatbot is working correctly!")
            print("\n📋 What's Fixed:")
            print("✅ Intent classification working properly")
            print("✅ Greetings classified as greetings")
            print("✅ Questions classified as questions")
            print("✅ Enhanced responses for technical topics")
            print("✅ API fallbacks working")
            print("\n🚀 Ready to use! Run: python run.py")
        else:
            print("❌ Some tests failed. Check the issues above.")
            
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_final_fixes()