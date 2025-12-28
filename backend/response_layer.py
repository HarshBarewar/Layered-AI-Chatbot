"""
Response Generation Layer - Generates responses using multiple strategies
"""
import random
import requests
from backend.config import Config

class ResponseLayer:
    """Handles response generation using various strategies"""
    
    def __init__(self):
        self.config = Config()
    
    def generate_rule_based_response(self, intent, sentiment, context=None):
        """Generate rule-based response from templates"""
        base_responses = self.config.RESPONSES.get(intent, self.config.RESPONSES['general'])
        response = random.choice(base_responses)
        
        # Apply tone modifications based on sentiment
        response = self._apply_tone_modifications(response, sentiment)
        
        return {
            'text': response,
            'strategy': 'rule_based',
            'confidence': 0.8
        }
    
    def generate_faq_response(self, faq_answer, sentiment):
        """Generate FAQ-based response"""
        response = faq_answer
        
        # Add polite framing
        if sentiment.get('sentiment') == 'positive':
            response = f"I'm happy to help! {response}"
        elif sentiment.get('sentiment') == 'negative':
            response = f"I understand your concern. {response}"
        
        return {
            'text': response,
            'strategy': 'faq',
            'confidence': 0.95
        }
    
    def generate_ai_response(self, text, intent, sentiment, context):
        """Generate AI-powered response using external APIs"""
        # Try OpenRouter first
        if self.config.OPENROUTER_API_KEY:
            ai_response = self._call_openrouter_api(text, intent, sentiment, context)
            if ai_response:
                return {
                    'text': ai_response,
                    'strategy': 'generative_ai',
                    'confidence': 0.9
                }
        
        # Try Hugging Face as fallback
        if self.config.HUGGINGFACE_API_KEY:
            ai_response = self._call_huggingface_api(text, intent, sentiment, context)
            if ai_response:
                return {
                    'text': ai_response,
                    'strategy': 'generative_ai',
                    'confidence': 0.8
                }
        
        return None
    
    def _call_openrouter_api(self, text, intent, sentiment, context):
        """Call OpenRouter API for AI response"""
        try:
            headers = {
                "Authorization": f"Bearer {self.config.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "Layered AI Chatbot"
            }
            
            # Build context-aware prompt
            prompt = self._build_ai_prompt(text, intent, sentiment, context)
            
            data = {
                "model": "meta-llama/llama-3.2-3b-instruct:free",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.config.OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=data,
                timeout=self.config.RESPONSE_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            print(f"OpenRouter API error: {e}")
        
        return None
    
    def _call_huggingface_api(self, text, intent, sentiment, context):
        """Call Hugging Face API for AI response"""
        try:
            headers = {
                "Authorization": f"Bearer {self.config.HUGGINGFACE_API_KEY}",
                "Content-Type": "application/json"
            }
            
            prompt = f"User: {text}\nAssistant:"
            
            data = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 100,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            response = requests.post(
                "https://api-inference.huggingface.co/models/gpt2",
                headers=headers,
                json=data,
                timeout=self.config.RESPONSE_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    if generated_text.startswith(prompt):
                        return generated_text[len(prompt):].strip()
                    return generated_text.strip()
            
        except Exception as e:
            print(f"Hugging Face API error: {e}")
        
        return None
    
    def _build_ai_prompt(self, text, intent, sentiment, context):
        """Build context-aware prompt for AI generation"""
        prompt = f"User message: {text}\n"
        prompt += f"Intent: {intent}\n"
        prompt += f"Sentiment: {sentiment.get('sentiment', 'neutral')}\n"
        
        # Add conversation context
        if context and context.get('history'):
            recent_history = context['history'][-2:]
            prompt += "Recent conversation:\n"
            for exchange in recent_history:
                prompt += f"User: {exchange['user']}\nBot: {exchange['bot']}\n"
        
        # Add tone instruction
        tone_instruction = self._get_tone_instruction(sentiment)
        prompt += f"\nRespond as a helpful AI assistant. {tone_instruction} Keep response concise.\n\nAssistant:"
        
        return prompt
    
    def _get_tone_instruction(self, sentiment):
        """Get tone instruction based on sentiment"""
        sentiment_label = sentiment.get('sentiment', 'neutral')
        emotions = sentiment.get('emotions', [])
        
        if sentiment_label == 'negative' or 'anger' in emotions:
            return "Respond with empathy and understanding."
        elif sentiment_label == 'positive' or 'joy' in emotions:
            return "Respond with enthusiasm and positivity."
        elif 'fear' in emotions or 'sadness' in emotions:
            return "Respond with reassurance and support."
        else:
            return "Respond in a helpful and professional manner."
    
    def generate_fallback_response(self, fallback_type, sentiment, context=None):
        """Generate fallback responses when other strategies fail"""
        fallback_responses = {
            'empathetic_fallback': [
                "I understand this might be frustrating. Let me try to help you in a different way.",
                "I can see this is important to you. Could you rephrase your question?",
                "I want to help you with this. Can you provide more details?"
            ],
            'question_fallback': [
                "That's an interesting question. While I don't have a specific answer, I'd be happy to help you explore this topic.",
                "I don't have complete information about that, but I can try to help you find what you're looking for.",
                "That's a good question. Could you provide more context so I can better assist you?"
            ],
            'friendly_fallback': [
                "I'm not sure I fully understand. Could you rephrase that?",
                "I'd like to help you with that. Can you tell me more?",
                "That's interesting! Could you elaborate a bit more?"
            ]
        }
        
        responses = fallback_responses.get(fallback_type, fallback_responses['friendly_fallback'])
        response = random.choice(responses)
        
        return {
            'text': response,
            'strategy': 'fallback',
            'confidence': 0.6
        }
    
    def _apply_tone_modifications(self, response, sentiment):
        """Apply tone modifications based on sentiment"""
        sentiment_label = sentiment.get('sentiment', 'neutral')
        emotions = sentiment.get('emotions', [])
        
        # Add empathy for negative sentiment
        if sentiment_label == 'negative' or 'anger' in emotions:
            empathy_prefixes = [
                "I understand that can be concerning. ",
                "I can see why that might be frustrating. ",
                "I hear you, and I want to help. "
            ]
            response = random.choice(empathy_prefixes) + response
        
        # Add enthusiasm for positive sentiment
        elif sentiment_label == 'positive' or 'joy' in emotions:
            enthusiasm_suffixes = [
                " I'm excited to help!",
                " This sounds great!",
                " I'm happy to assist!"
            ]
            response = response + random.choice(enthusiasm_suffixes)
        
        return response
    
    def generate_response(self, strategy_decision, text, intent, sentiment, context):
        """Main response generation based on strategy decision"""
        strategy = strategy_decision['strategy']
        
        if strategy == 'faq':
            return self.generate_faq_response(strategy_decision['faq_answer'], sentiment)
        
        elif strategy == 'rule_based':
            return self.generate_rule_based_response(intent, sentiment, context)
        
        elif strategy == 'generative_ai':
            ai_response = self.generate_ai_response(text, intent, sentiment, context)
            if ai_response:
                return ai_response
            # Fallback to rule-based if AI fails
            return self.generate_rule_based_response(intent, sentiment, context)
        
        elif strategy == 'fallback':
            fallback_type = strategy_decision.get('fallback_type', 'friendly_fallback')
            return self.generate_fallback_response(fallback_type, sentiment, context)
        
        else:
            # Default fallback
            return self.generate_rule_based_response(intent, sentiment, context)