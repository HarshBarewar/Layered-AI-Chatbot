#!/usr/bin/env python3
"""
Quick test for intent classification
"""

def test_intent_classification():
    """Test intent classification specifically"""
    try:
        from backend.nlp_layer import NLPLayer
        
        print("🧠 Testing Intent Classification...")
        nlp = NLPLayer()
        
        test_cases = [
            ("what is machine learning?", "question"),
            ("tell me about machine learning", "question"),
            ("explain artificial intelligence", "question"),
            ("what is data science", "question"),
            ("hello", "greeting"),
            ("hi there", "greeting"),
            ("thank you", "compliment"),
            ("can you help me", "help"),
            ("goodbye", "goodbye")
        ]
        
        print("\n🧪 Testing Intent Classification:")
        print("=" * 60)
        
        for text, expected in test_cases:
            intent, confidence = nlp.classify_intent(text)
            status = "✅" if intent == expected else "❌"
            print(f"{status} '{text}' → {intent} ({confidence:.2f}) [Expected: {expected}]")
        
        print("\n" + "=" * 60)
        print("🎯 Intent classification test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_intent_classification()