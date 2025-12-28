"""
Decision Engine - Routes requests and selects response strategies
"""
from backend.config import Config

class DecisionEngine:
    """Handles decision making for response strategy selection"""
    
    def __init__(self):
        self.config = Config()
    
    def check_faq(self, text):
        """Check if the query matches FAQ database"""
        text_lower = text.lower().strip()
        
        # Direct match
        if text_lower in self.config.FAQ_DATABASE:
            return self.config.FAQ_DATABASE[text_lower], 0.95
        
        # Partial match with better similarity
        best_match = None
        best_score = 0
        
        for faq_key, faq_answer in self.config.FAQ_DATABASE.items():
            similarity = self._calculate_similarity(text_lower, faq_key)
            if similarity > best_score and similarity > 0.5:  # Lower threshold
                best_score = similarity
                best_match = faq_answer
        
        if best_match:
            return best_match, best_score
        
        # Check for key terms
        key_terms = {
            'ai model': 'Some of the best AI models include GPT-4, Claude, Gemini, and LLaMA. Each excels in different areas like reasoning, coding, or creativity.',
            'inc': 'The current president of the Indian National Congress (INC) is Mallikarjun Kharge, elected in October 2022.',
            'rahul': 'Rahul Gandhi is an Indian politician and member of the Indian National Congress. He served as Congress President from 2017-2019 and is currently a Member of Parliament.',
            'gandhi': 'Rahul Gandhi is the son of Sonia Gandhi and late Rajiv Gandhi. He represents Wayanad constituency in Lok Sabha and is a prominent opposition leader in India.'
        }
        
        for term, answer in key_terms.items():
            if term in text_lower:
                return answer, 0.8
        
        return None, 0.0
    
    def _calculate_similarity(self, text1, text2):
        """Simple similarity calculation"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def should_use_rule_based(self, intent, confidence):
        """Decide if rule-based response should be used"""
        # Use rule-based for high-confidence common intents
        rule_based_intents = ['greeting', 'goodbye', 'compliment']
        
        if intent in rule_based_intents and confidence > 0.7:
            return True
        
        # Use rule-based for low-confidence queries as fallback
        if confidence < 0.4:
            return True
        
        return False
    
    def should_use_generative_ai(self, intent, confidence, context):
        """Decide if generative AI should be used"""
        # Use AI for complex questions and general queries
        ai_suitable_intents = ['question', 'general', 'help']
        
        if intent in ai_suitable_intents and confidence > 0.6:
            return True
        
        # Use AI if conversation history suggests complex discussion
        if context and len(context.get('history', [])) > 2:
            return True
        
        return False
    
    def get_fallback_strategy(self, intent, sentiment):
        """Determine fallback strategy when primary methods fail"""
        # If user seems frustrated, be more empathetic
        if sentiment.get('sentiment') == 'negative' or 'anger' in sentiment.get('emotions', []):
            return 'empathetic_fallback'
        
        # If user is asking questions, acknowledge and redirect
        if intent == 'question':
            return 'question_fallback'
        
        # Default friendly fallback
        return 'friendly_fallback'
    
    def decide_response_strategy(self, text, intent, confidence, sentiment, context):
        """Main decision logic for response strategy"""
        decision = {
            'strategy': 'rule_based',  # default
            'confidence': confidence,
            'reasoning': '',
            'fallback_needed': False
        }
        
        # Step 1: Check FAQ first
        faq_answer, faq_confidence = self.check_faq(text)
        if faq_answer:
            decision.update({
                'strategy': 'faq',
                'confidence': faq_confidence,
                'reasoning': 'Direct FAQ match found',
                'faq_answer': faq_answer
            })
            return decision
        
        # Step 2: Check if rule-based is appropriate
        if self.should_use_rule_based(intent, confidence):
            decision.update({
                'strategy': 'rule_based',
                'reasoning': f'Rule-based suitable for {intent} with confidence {confidence}'
            })
            return decision
        
        # Step 3: Check if generative AI should be used
        if self.should_use_generative_ai(intent, confidence, context):
            decision.update({
                'strategy': 'generative_ai',
                'reasoning': f'Complex query suitable for AI: {intent}'
            })
            return decision
        
        # Step 4: Determine fallback strategy
        fallback_strategy = self.get_fallback_strategy(intent, sentiment)
        decision.update({
            'strategy': 'fallback',
            'fallback_type': fallback_strategy,
            'reasoning': f'Using fallback strategy: {fallback_strategy}',
            'fallback_needed': True
        })
        
        return decision
    
    def get_response_priority(self, strategies):
        """Prioritize multiple response strategies"""
        priority_order = ['faq', 'rule_based', 'generative_ai', 'fallback']
        
        # Sort strategies by priority
        sorted_strategies = sorted(strategies, key=lambda x: priority_order.index(x['strategy']))
        
        return sorted_strategies[0] if sorted_strategies else {
            'strategy': 'fallback',
            'fallback_type': 'friendly_fallback',
            'confidence': 0.3
        }