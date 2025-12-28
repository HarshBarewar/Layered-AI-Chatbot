"""
NLP Processing Layer - Intent recognition, NER, and context management
"""
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from backend.config import Config

class NLPLayer:
    """Handles NLP processing including intent recognition and NER"""
    
    def __init__(self):
        self.config = Config()
        self.intent_model = None
        self.context_memory = {}
        self.load_or_train_intent_model()
    
    def load_or_train_intent_model(self):
        """Load existing intent model or train a new one"""
        if os.path.exists(self.config.INTENT_MODEL_FILE):
            try:
                with open(self.config.INTENT_MODEL_FILE, 'rb') as f:
                    self.intent_model = pickle.load(f)
                return
            except:
                pass
        
        self.train_intent_model()
    
    def train_intent_model(self):
        """Train intent classification model"""
        training_data = []
        labels = []
        
        # Generate training data from config
        for intent, patterns in self.config.INTENTS.items():
            for pattern in patterns:
                training_data.append(pattern)
                labels.append(intent)
                
                # Add variations
                training_data.append(f"I want to {pattern}")
                labels.append(intent)
                training_data.append(f"Can you {pattern}")
                labels.append(intent)
        
        # Create and train pipeline
        self.intent_model = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), stop_words='english')),
            ('classifier', MultinomialNB(alpha=0.1))
        ])
        
        self.intent_model.fit(training_data, labels)
        
        # Save model
        os.makedirs(self.config.MODELS_DIR, exist_ok=True)
        try:
            with open(self.config.INTENT_MODEL_FILE, 'wb') as f:
                pickle.dump(self.intent_model, f)
        except:
            pass
    
    def classify_intent(self, text, context=None):
        """Classify user intent using ML model and rules"""
        # Rule-based classification first
        text_lower = text.lower()
        
        # Check for exact matches
        for intent, patterns in self.config.INTENTS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return intent, 0.9
        
        # Check for question patterns
        question_words = ['what', 'how', 'when', 'where', 'why', 'who', 'which']
        if any(word in text_lower for word in question_words) or '?' in text:
            return 'question', 0.8
        
        # ML-based classification
        if self.intent_model:
            try:
                predicted_intent = self.intent_model.predict([text])[0]
                confidence = max(self.intent_model.predict_proba([text])[0])
                
                if confidence > self.config.CONFIDENCE_THRESHOLD:
                    return predicted_intent, confidence
            except:
                pass
        
        return 'general', 0.5
    
    def extract_entities(self, text):
        """Extract named entities (simplified NER)"""
        entities = []
        text_lower = text.lower()
        
        # Simple entity patterns
        entity_patterns = {
            'PERSON': ['modi', 'narendra', 'pm', 'prime minister'],
            'LOCATION': ['india', 'delhi', 'mumbai', 'bangalore'],
            'TIME': ['today', 'tomorrow', 'yesterday', 'now', 'morning', 'evening'],
            'NUMBER': []
        }
        
        # Find numbers
        import re
        numbers = re.findall(r'\b\d+\b', text)
        for num in numbers:
            entities.append({'text': num, 'label': 'NUMBER'})
        
        # Find other entities
        for entity_type, patterns in entity_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    entities.append({'text': pattern, 'label': entity_type})
        
        return entities
    
    def update_context(self, user_id, user_message, bot_response, intent):
        """Update conversation context for multi-turn memory"""
        if user_id not in self.context_memory:
            self.context_memory[user_id] = {
                'history': [],
                'current_topic': None,
                'user_preferences': {}
            }
        
        context = self.context_memory[user_id]
        
        # Add to history
        context['history'].append({
            'user': user_message,
            'bot': bot_response,
            'intent': intent,
            'timestamp': None  # Would add timestamp in production
        })
        
        # Keep only recent history
        if len(context['history']) > self.config.MAX_CONVERSATION_HISTORY:
            context['history'] = context['history'][-self.config.MAX_CONVERSATION_HISTORY:]
        
        # Update current topic
        context['current_topic'] = intent
        
        return context
    
    def get_context(self, user_id):
        """Get conversation context for a user"""
        return self.context_memory.get(user_id, {
            'history': [],
            'current_topic': None,
            'user_preferences': {}
        })
    
    def process(self, text, user_id=None):
        """Main NLP processing pipeline"""
        # Classify intent
        intent, confidence = self.classify_intent(text)
        
        # Extract entities
        entities = self.extract_entities(text)
        
        # Get context if user_id provided
        context = self.get_context(user_id) if user_id else {}
        
        return {
            'intent': intent,
            'intent_confidence': confidence,
            'entities': entities,
            'context': context
        }