"""
Core Orchestrator - Coordinates all layers of the chatbot system
"""
import time
from datetime import datetime
from backend.config import Config
from backend.preprocessing import PreprocessingLayer
from backend.nlp_layer import NLPLayer
from backend.sentiment_layer import SentimentLayer
from backend.decision_engine import DecisionEngine
from backend.response_layer import ResponseLayer
from backend.storage_layer import StorageLayer
from backend.analytics_layer import AnalyticsLayer
from backend.learning_layer import LearningLayer

class ChatbotCore:
    """Main orchestrator that coordinates all system layers"""
    
    def __init__(self):
        print("Initializing Layered AI Chatbot System...")
        
        # Initialize configuration
        self.config = Config()
        
        # Initialize layers in dependency order
        self.preprocessing = PreprocessingLayer()
        self.nlp = NLPLayer()
        self.sentiment = SentimentLayer()
        self.decision_engine = DecisionEngine()
        self.response_layer = ResponseLayer()
        self.storage = StorageLayer()
        self.analytics = AnalyticsLayer(self.storage)
        self.learning = LearningLayer(self.storage, self.nlp)
        
        print("✅ All layers initialized successfully!")
    
    def process_message(self, user_message, user_id="default_user"):
        """Main message processing pipeline through all layers"""
        start_time = time.time()
        
        try:
            # Layer 1: Preprocessing
            preprocessed = self.preprocessing.preprocess(user_message)
            
            # Layer 2: NLP Processing
            nlp_result = self.nlp.process(preprocessed['cleaned'], user_id)
            intent = nlp_result['intent']
            intent_confidence = nlp_result['intent_confidence']
            entities = nlp_result['entities']
            context = nlp_result['context']
            
            # Layer 3: Sentiment Analysis
            sentiment_result = self.sentiment.analyze(user_message)
            
            # Layer 4: Decision Engine
            decision = self.decision_engine.decide_response_strategy(
                user_message, intent, intent_confidence, sentiment_result, context
            )
            
            # Layer 5: Response Generation
            response = self.response_layer.generate_response(
                decision, user_message, intent, sentiment_result, context
            )
            
            # Determine success based on confidence and strategy
            success = self._evaluate_response_success(response, decision)
            
            # Layer 6: Storage
            self.storage.store_conversation(
                user_id, user_message, response['text'], intent, sentiment_result, success
            )
            
            # Layer 7: Analytics
            processing_time = time.time() - start_time
            self.analytics.track_conversation(
                user_id, intent, sentiment_result, response['strategy'], success, processing_time
            )
            
            # Layer 8: Learning
            self.learning.learn_from_conversation(
                user_id, user_message, response, intent, sentiment_result, success
            )
            
            # Update NLP context
            self.nlp.update_context(user_id, user_message, response['text'], intent)
            
            # Prepare final response
            final_response = {
                'text': response['text'],
                'intent': intent,
                'intent_confidence': intent_confidence,
                'sentiment': sentiment_result,
                'entities': entities,
                'strategy': response['strategy'],
                'confidence': response['confidence'],
                'success': success,
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat()
            }
            
            return final_response
            
        except Exception as e:
            print(f"Error in message processing pipeline: {e}")
            
            # Fallback response
            fallback_response = {
                'text': "I apologize, but I'm having trouble processing your message right now. Could you please try rephrasing?",
                'intent': 'error',
                'intent_confidence': 0.0,
                'sentiment': {'sentiment': 'neutral', 'polarity': 0},
                'entities': [],
                'strategy': 'error_fallback',
                'confidence': 0.3,
                'success': False,
                'processing_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            
            return fallback_response
    
    def _evaluate_response_success(self, response, decision):
        """Evaluate if the response generation was successful"""
        # High confidence responses are considered successful
        if response['confidence'] > 0.8:
            return True
        
        # FAQ responses are generally successful
        if decision['strategy'] == 'faq':
            return True
        
        # Rule-based responses for appropriate intents are successful
        if decision['strategy'] == 'rule_based' and response['confidence'] > 0.6:
            return True
        
        # AI responses with reasonable confidence are successful
        if decision['strategy'] == 'generative_ai' and response['confidence'] > 0.7:
            return True
        
        # Fallback responses are considered partially successful
        if decision['strategy'] == 'fallback':
            return response['confidence'] > 0.5
        
        return False
    
    def get_conversation_history(self, user_id, limit=10):
        """Get conversation history for a user"""
        return self.storage.get_user_history(user_id, limit)
    
    def get_user_profile(self, user_id):
        """Get user profile information"""
        return self.storage.get_user_profile(user_id)
    
    def get_analytics_dashboard(self, days=30):
        """Get comprehensive analytics dashboard data"""
        return self.analytics.get_dashboard_data(days)
    
    def get_learning_insights(self):
        """Get learning and improvement insights"""
        return self.learning.get_learning_insights()
    
    def process_feedback(self, session_id, rating, comment=""):
        """Process user feedback for learning"""
        try:
            # For now, we'll use session_id as user_id
            # In production, you'd have proper user management
            user_id = session_id
            
            # Get recent conversation to associate feedback
            history = self.get_conversation_history(user_id, 1)
            if history:
                last_conversation = history[-1]
                
                # Convert rating (1-5) to success boolean
                success = rating >= 3
                
                # Learn from feedback
                self.learning.learn_from_conversation(
                    user_id, 
                    last_conversation['user_message'],
                    {'strategy': 'feedback', 'confidence': rating / 5.0},
                    last_conversation['intent'],
                    last_conversation['sentiment'],
                    success
                )
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error processing feedback: {e}")
            return False
    
    def get_system_health(self):
        """Get system health status"""
        health_status = {
            'preprocessing_layer': 'operational',
            'nlp_layer': 'operational',
            'sentiment_layer': 'operational',
            'decision_engine': 'operational',
            'response_layer': 'operational',
            'storage_layer': 'operational',
            'analytics_layer': 'operational',
            'learning_layer': 'operational',
            'api_status': {
                'openrouter': 'available' if self.config.OPENROUTER_API_KEY else 'not_configured',
                'huggingface': 'available' if self.config.HUGGINGFACE_API_KEY else 'not_configured'
            },
            'system_metrics': {
                'total_conversations': self.storage.analytics_data['total_conversations'],
                'active_users': len(self.storage.chat_data),
                'intent_model_loaded': self.nlp.intent_model is not None
            }
        }
        
        return health_status
    
    def optimize_system(self):
        """Run system optimization based on learning insights"""
        try:
            optimization_results = {
                'intent_model_retrained': False,
                'patterns_discovered': 0,
                'suggestions_generated': 0,
                'data_cleaned': False
            }
            
            # Generate optimization suggestions
            suggestions = self.learning.generate_optimization_suggestions()
            optimization_results['suggestions_generated'] = len(suggestions)
            
            # Attempt to improve intent classifier
            if self.learning.improve_intent_classifier():
                optimization_results['intent_model_retrained'] = True
            
            # Clean up old data
            self.storage.cleanup_old_data()
            optimization_results['data_cleaned'] = True
            
            # Count pattern discoveries
            optimization_results['patterns_discovered'] = len(self.learning.learning_data['pattern_discoveries'])
            
            return optimization_results
            
        except Exception as e:
            print(f"Error during system optimization: {e}")
            return {'error': str(e)}
    
    def get_system_statistics(self):
        """Get comprehensive system statistics"""
        try:
            analytics_summary = self.storage.get_analytics_summary()
            learning_insights = self.get_learning_insights()
            
            return {
                'analytics_summary': analytics_summary,
                'learning_insights': learning_insights,
                'system_health': self.get_system_health(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting system statistics: {e}")
            return {'error': str(e)}
    
    def shutdown(self):
        """Graceful system shutdown"""
        print("Shutting down Layered AI Chatbot System...")
        
        # Save all data
        self.storage.save_chat_history()
        self.storage.save_analytics_data()
        self.learning._save_learning_data()
        
        print("✅ System shutdown complete!")