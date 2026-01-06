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
        
        # Enhanced training data
        training_examples = {
            'greeting': [
                'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
                'greetings', 'howdy', 'hiya', 'sup'
            ],
            'goodbye': [
                'bye', 'goodbye', 'see you later', 'farewell', 'take care', 'exit',
                'quit', 'see ya', 'catch you later', 'until next time'
            ],
            'question': [
                'what is machine learning', 'what is data science', 'how does AI work',
                'explain artificial intelligence', 'tell me about python', 'what are algorithms',
                'how do neural networks work', 'what is deep learning', 'define statistics',
                'what is the capital of france', 'who is the president', 'when was this invented',
                'where is this located', 'why does this happen', 'which is better',
                'what time is it', 'how old are you', 'what can you do'
            ],
            'help': [
                'help me', 'can you help', 'i need assistance', 'support me',
                'guide me', 'show me how', 'can you assist', 'i need help with',
                'help with this', 'assist me please'
            ],
            'compliment': [
                'thank you', 'thanks', 'good job', 'well done', 'excellent work',
                'great response', 'amazing', 'fantastic', 'you are helpful',
                'appreciate it', 'good answer'
            ],
            'general': [
                'tell me something', 'i want to know', 'information about',
                'details on', 'more about this', 'explain this topic',
                'i am interested in', 'show me', 'describe this'
            ]
        }
        
        # Generate training data
        for intent, examples in training_examples.items():
            for example in examples:
                training_data.append(example)
                labels.append(intent)
                
                # Add variations
                if intent == 'question':
                    training_data.append(f"can you {example}")
                    labels.append(intent)
                    training_data.append(f"please {example}")
                    labels.append(intent)
        
        # Create and train pipeline
        self.intent_model = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 3), stop_words='english', max_features=1000)),
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
        text_lower = text.lower().strip()
        
        # Priority 1: Greeting detection (must be first)
        greeting_patterns = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings']
        if any(greeting in text_lower for greeting in greeting_patterns):
            # Check if it's a simple greeting (not a question about greetings)
            if not any(q in text_lower for q in ['what', 'how', 'why', 'when', 'where', 'who', 'which', '?']):
                return 'greeting', 0.95
        
        # Priority 2: Goodbye detection
        goodbye_words = ['bye', 'goodbye', 'see you', 'farewell', 'exit', 'quit']
        if any(word in text_lower for word in goodbye_words):
            return 'goodbye', 0.9
        
        # Priority 3: Compliment detection
        compliment_words = ['thank', 'thanks', 'good job', 'well done', 'excellent', 'amazing', 'great']
        if any(word in text_lower for word in compliment_words):
            return 'compliment', 0.85
        
        # Priority 4: Help detection
        help_patterns = ['help me', 'can you help', 'need help', 'assist me', 'support me']
        if any(pattern in text_lower for pattern in help_patterns):
            return 'help', 0.9
        
        # Priority 5: Question detection (more specific)
        question_starters = ['what is', 'what are', 'how does', 'how do', 'tell me about', 'explain', 'describe', 'define']
        question_words = ['what', 'how', 'when', 'where', 'why', 'who', 'which']
        
        # Check for explicit question patterns
        if any(pattern in text_lower for pattern in question_starters) or '?' in text:
            return 'question', 0.95
        
        # Check for question words at the beginning
        words = text_lower.split()
        if len(words) > 0 and words[0] in question_words:
            return 'question', 0.9
        
        # Priority 6: ML-based classification as fallback
        if self.intent_model:
            try:
                predicted_intent = self.intent_model.predict([text])[0]
                confidence = max(self.intent_model.predict_proba([text])[0])
                
                if confidence > 0.7:  # Higher threshold for ML
                    return predicted_intent, confidence
            except:
                pass
        
        # Default to general for everything else
        return 'general', 0.6
    
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