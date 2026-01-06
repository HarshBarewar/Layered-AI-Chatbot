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
        # Check if we have valid API keys
        if not self.config.OPENROUTER_API_KEY or self.config.OPENROUTER_API_KEY == 'your_openrouter_key_here':
            print("⚠️ OpenRouter API key not configured")
        
        if not self.config.HUGGINGFACE_API_KEY or self.config.HUGGINGFACE_API_KEY == 'your_huggingface_key_here':
            print("⚠️ Hugging Face API key not configured")
        
        # Try OpenRouter first (better for general questions)
        if self.config.OPENROUTER_API_KEY and self.config.OPENROUTER_API_KEY != 'your_openrouter_key_here':
            ai_response = self._call_openrouter_api(text, intent, sentiment, context)
            if ai_response:
                return {
                    'text': ai_response,
                    'strategy': 'generative_ai',
                    'confidence': 0.9
                }
        
        # Try Hugging Face as fallback
        if self.config.HUGGINGFACE_API_KEY and self.config.HUGGINGFACE_API_KEY != 'your_huggingface_key_here':
            ai_response = self._call_huggingface_api(text, intent, sentiment, context)
            if ai_response:
                return {
                    'text': ai_response,
                    'strategy': 'generative_ai',
                    'confidence': 0.8
                }
        
        # If no API keys available, use enhanced rule-based responses
        return self._generate_enhanced_rule_response(text, intent, sentiment, context)
    
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
                "messages": [
                    {"role": "system", "content": "You are a helpful, knowledgeable AI assistant. Provide accurate, informative, and concise responses. For technical topics like data science, explain concepts clearly with examples when appropriate. Always give direct, specific answers to questions."},
                    {"role": "user", "content": text}
                ],
                "max_tokens": 300,
                "temperature": 0.7
            }
            
            print(f"🔄 Calling OpenRouter API for: {text[:50]}...")
            
            response = requests.post(
                f"{self.config.OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=data,
                timeout=self.config.RESPONSE_TIMEOUT
            )
            
            print(f"📡 OpenRouter API Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content'].strip()
                print(f"✅ OpenRouter API Success: {ai_response[:100]}...")
                return ai_response
            else:
                print(f"❌ OpenRouter API Error: {response.status_code} - {response.text}")
            
        except Exception as e:
            print(f"❌ OpenRouter API Exception: {e}")
        
        return None
    
    def _call_huggingface_api(self, text, intent, sentiment, context):
        """Call Hugging Face API for AI response"""
        try:
            headers = {
                "Authorization": f"Bearer {self.config.HUGGINGFACE_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Use a better model for text generation
            prompt = self._build_ai_prompt(text, intent, sentiment, context)
            
            data = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 150,
                    "temperature": 0.7,
                    "do_sample": True,
                    "top_p": 0.9,
                    "repetition_penalty": 1.1
                },
                "options": {
                    "wait_for_model": True
                }
            }
            
            # Try different models based on the question type
            models = [
                "microsoft/DialoGPT-medium",
                "facebook/blenderbot-400M-distill",
                "gpt2"
            ]
            
            for model in models:
                try:
                    response = requests.post(
                        f"https://api-inference.huggingface.co/models/{model}",
                        headers=headers,
                        json=data,
                        timeout=self.config.RESPONSE_TIMEOUT
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if isinstance(result, list) and len(result) > 0:
                            generated_text = result[0].get('generated_text', '')
                            # Clean up the response
                            if generated_text.startswith(prompt):
                                clean_response = generated_text[len(prompt):].strip()
                            else:
                                clean_response = generated_text.strip()
                            
                            # Filter out incomplete or poor responses
                            if len(clean_response) > 10 and not clean_response.startswith('User:'):
                                return clean_response
                    
                except Exception as model_error:
                    print(f"Model {model} failed: {model_error}")
                    continue
            
        except Exception as e:
            print(f"Hugging Face API error: {e}")
        
        return None
    
    def _build_ai_prompt(self, text, intent, sentiment, context):
        """Build context-aware prompt for AI generation"""
        # Create a more natural conversation prompt
        prompt = ""
        
        # Add conversation context if available
        if context and context.get('history'):
            recent_history = context['history'][-2:]
            for exchange in recent_history:
                prompt += f"Human: {exchange['user']}\nAssistant: {exchange['bot']}\n"
        
        # Add current user message
        prompt += f"Human: {text}\nAssistant:"
        
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
            # Fallback to enhanced rules if AI fails
            print("🔄 AI failed, using enhanced rules...")
            return self._generate_enhanced_rule_response(text, intent, sentiment, context)
        
        elif strategy == 'fallback':
            fallback_type = strategy_decision.get('fallback_type', 'friendly_fallback')
            return self.generate_fallback_response(fallback_type, sentiment, context)
        
        else:
            # Default fallback
            return self._generate_enhanced_rule_response(text, intent, sentiment, context)
    
    def _generate_enhanced_rule_response(self, text, intent, sentiment, context):
        """Generate enhanced rule-based responses when APIs are not available"""
        text_lower = text.lower()
        
        # Enhanced responses for common questions
        if 'data science' in text_lower:
            response = "Data science is an interdisciplinary field that uses scientific methods, processes, algorithms, and systems to extract knowledge and insights from structured and unstructured data. It combines statistics, mathematics, programming, and domain expertise to analyze complex data sets and make data-driven decisions. Key areas include data collection, cleaning, analysis, visualization, and machine learning."
        elif 'machine learning' in text_lower or 'ml' in text_lower:
            response = "Machine Learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed. It includes supervised learning (with labeled data), unsupervised learning (finding patterns), and reinforcement learning (learning through rewards)."
        elif 'artificial intelligence' in text_lower or 'ai' in text_lower:
            response = "Artificial Intelligence (AI) is the simulation of human intelligence in machines. It includes machine learning, natural language processing, computer vision, robotics, and expert systems. AI aims to create systems that can perform tasks that typically require human intelligence."
        elif 'python' in text_lower and ('programming' in text_lower or 'language' in text_lower):
            response = "Python is a high-level, interpreted programming language known for its simplicity and readability. It's widely used in data science, web development, automation, and AI due to its extensive libraries like pandas, numpy, scikit-learn, and tensorflow."
        elif 'decision tree' in text_lower:
            response = "A Decision Tree Classifier is a supervised machine learning algorithm that uses a tree-like model to make decisions. It splits data based on feature values to create branches, with each leaf representing a class prediction. It's easy to interpret and visualize, making it popular for classification tasks."
        elif '7 c' in text_lower and 'communication' in text_lower:
            response = "The 7 C's of Communication are: 1) Clear - easy to understand, 2) Concise - brief and to the point, 3) Concrete - specific and definite, 4) Correct - accurate information, 5) Coherent - logical flow, 6) Complete - all necessary information, 7) Courteous - respectful and polite tone."
        elif any(word in text_lower for word in ['what', 'how', 'why', 'when', 'where', 'explain', 'tell me']):
            # For general questions, provide helpful responses
            if intent == 'question':
                response = "I'd be happy to help answer your question. Could you provide a bit more context or be more specific about what you'd like to know?"
            else:
                base_responses = self.config.RESPONSES.get(intent, self.config.RESPONSES['general'])
                response = random.choice(base_responses)
        else:
            # Use standard rule-based response
            base_responses = self.config.RESPONSES.get(intent, self.config.RESPONSES['general'])
            response = random.choice(base_responses)
        
        # Apply tone modifications
        response = self._apply_tone_modifications(response, sentiment)
        
        return {
            'text': response,
            'strategy': 'enhanced_rule_based',
            'confidence': 0.85
        }