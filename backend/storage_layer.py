"""
Data Storage Layer - Handles persistent data storage and retrieval
"""
import json
import os
from datetime import datetime
from backend.config import Config

class StorageLayer:
    """Handles data storage and retrieval operations"""
    
    def __init__(self):
        self.config = Config()
        self.chat_data = self._load_chat_history()
        self.analytics_data = self._load_analytics_data()
        
        # Ensure data directories exist
        os.makedirs(self.config.DATA_DIR, exist_ok=True)
    
    def _load_chat_history(self):
        """Load chat history from file"""
        if os.path.exists(self.config.CHAT_HISTORY_FILE):
            try:
                with open(self.config.CHAT_HISTORY_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _load_analytics_data(self):
        """Load analytics data from file"""
        if os.path.exists(self.config.ANALYTICS_FILE):
            try:
                with open(self.config.ANALYTICS_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'total_conversations': 0,
            'intent_counts': {},
            'sentiment_records': [],
            'response_success': [],
            'failed_responses': [],
            'user_interactions': {}
        }
    
    def save_chat_history(self):
        """Save chat history to file"""
        try:
            with open(self.config.CHAT_HISTORY_FILE, 'w') as f:
                json.dump(self.chat_data, f, indent=2)
        except Exception as e:
            print(f"Error saving chat history: {e}")
    
    def save_analytics_data(self):
        """Save analytics data to file"""
        try:
            with open(self.config.ANALYTICS_FILE, 'w') as f:
                json.dump(self.analytics_data, f, indent=2)
        except Exception as e:
            print(f"Error saving analytics data: {e}")
    
    def store_conversation(self, user_id, user_message, bot_response, intent, sentiment, success=True):
        """Store a conversation exchange"""
        timestamp = datetime.now().isoformat()
        
        # Initialize user data if not exists
        if user_id not in self.chat_data:
            self.chat_data[user_id] = {
                'conversations': [],
                'user_profile': {
                    'first_interaction': timestamp,
                    'total_messages': 0,
                    'preferred_intents': {},
                    'sentiment_history': []
                }
            }
        
        # Store conversation
        conversation_entry = {
            'timestamp': timestamp,
            'user_message': user_message,
            'bot_response': bot_response,
            'intent': intent,
            'sentiment': sentiment,
            'success': success
        }
        
        self.chat_data[user_id]['conversations'].append(conversation_entry)
        
        # Update user profile
        profile = self.chat_data[user_id]['user_profile']
        profile['total_messages'] += 1
        profile['last_interaction'] = timestamp
        
        # Track preferred intents
        if intent not in profile['preferred_intents']:
            profile['preferred_intents'][intent] = 0
        profile['preferred_intents'][intent] += 1
        
        # Track sentiment history
        profile['sentiment_history'].append({
            'timestamp': timestamp,
            'sentiment': sentiment.get('sentiment', 'neutral'),
            'polarity': sentiment.get('polarity', 0)
        })
        
        # Keep only recent sentiment history
        if len(profile['sentiment_history']) > 50:
            profile['sentiment_history'] = profile['sentiment_history'][-50:]
        
        # Keep only recent conversations
        if len(self.chat_data[user_id]['conversations']) > 100:
            self.chat_data[user_id]['conversations'] = self.chat_data[user_id]['conversations'][-100:]
        
        self.save_chat_history()
    
    def store_intent_record(self, intent, confidence, success):
        """Store intent classification record"""
        if intent not in self.analytics_data['intent_counts']:
            self.analytics_data['intent_counts'][intent] = {
                'total': 0,
                'successful': 0,
                'avg_confidence': 0,
                'confidence_sum': 0
            }
        
        intent_data = self.analytics_data['intent_counts'][intent]
        intent_data['total'] += 1
        intent_data['confidence_sum'] += confidence
        intent_data['avg_confidence'] = intent_data['confidence_sum'] / intent_data['total']
        
        if success:
            intent_data['successful'] += 1
        
        self.save_analytics_data()
    
    def store_sentiment_record(self, sentiment_data, user_id):
        """Store sentiment analysis record"""
        sentiment_record = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'sentiment': sentiment_data.get('sentiment', 'neutral'),
            'polarity': sentiment_data.get('polarity', 0),
            'emotions': sentiment_data.get('emotions', []),
            'primary_emotion': sentiment_data.get('primary_emotion')
        }
        
        self.analytics_data['sentiment_records'].append(sentiment_record)
        
        # Keep only recent records
        if len(self.analytics_data['sentiment_records']) > 1000:
            self.analytics_data['sentiment_records'] = self.analytics_data['sentiment_records'][-1000:]
        
        self.save_analytics_data()
    
    def store_response_success(self, strategy, success, confidence, response_time=None):
        """Store response generation success/failure"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'strategy': strategy,
            'success': success,
            'confidence': confidence,
            'response_time': response_time
        }
        
        if success:
            self.analytics_data['response_success'].append(record)
            # Keep only recent successful responses
            if len(self.analytics_data['response_success']) > 500:
                self.analytics_data['response_success'] = self.analytics_data['response_success'][-500:]
        else:
            self.analytics_data['failed_responses'].append(record)
            # Keep only recent failed responses
            if len(self.analytics_data['failed_responses']) > 200:
                self.analytics_data['failed_responses'] = self.analytics_data['failed_responses'][-200:]
        
        self.save_analytics_data()
    
    def get_user_history(self, user_id, limit=10):
        """Get conversation history for a user"""
        if user_id not in self.chat_data:
            return []
        
        conversations = self.chat_data[user_id]['conversations']
        return conversations[-limit:] if conversations else []
    
    def get_user_profile(self, user_id):
        """Get user profile data"""
        if user_id not in self.chat_data:
            return None
        
        return self.chat_data[user_id]['user_profile']
    
    def get_analytics_summary(self):
        """Get analytics summary"""
        # Calculate total conversations
        total_conversations = sum(
            len(user_data['conversations']) 
            for user_data in self.chat_data.values()
        )
        
        # Calculate intent success rates
        intent_success_rates = {}
        for intent, data in self.analytics_data['intent_counts'].items():
            if data['total'] > 0:
                intent_success_rates[intent] = {
                    'success_rate': (data['successful'] / data['total']) * 100,
                    'avg_confidence': data['avg_confidence'],
                    'total_count': data['total']
                }
        
        # Calculate sentiment distribution
        sentiment_distribution = {'positive': 0, 'negative': 0, 'neutral': 0}
        for record in self.analytics_data['sentiment_records'][-100:]:  # Recent 100 records
            sentiment = record['sentiment']
            if sentiment in sentiment_distribution:
                sentiment_distribution[sentiment] += 1
        
        # Calculate response strategy effectiveness
        strategy_effectiveness = {}
        for record in self.analytics_data['response_success'][-100:]:  # Recent 100 records
            strategy = record['strategy']
            if strategy not in strategy_effectiveness:
                strategy_effectiveness[strategy] = {'total': 0, 'successful': 0}
            
            strategy_effectiveness[strategy]['total'] += 1
            if record['success']:
                strategy_effectiveness[strategy]['successful'] += 1
        
        # Calculate success rates
        for strategy, data in strategy_effectiveness.items():
            if data['total'] > 0:
                data['success_rate'] = (data['successful'] / data['total']) * 100
        
        return {
            'total_conversations': total_conversations,
            'total_users': len(self.chat_data),
            'intent_success_rates': intent_success_rates,
            'sentiment_distribution': sentiment_distribution,
            'strategy_effectiveness': strategy_effectiveness,
            'failed_responses_count': len(self.analytics_data['failed_responses'])
        }
    
    def cleanup_old_data(self, days_to_keep=30):
        """Clean up old data beyond retention period"""
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_iso = cutoff_date.isoformat()
        
        # Clean up old conversations
        for user_id in list(self.chat_data.keys()):
            user_data = self.chat_data[user_id]
            
            # Filter conversations
            user_data['conversations'] = [
                conv for conv in user_data['conversations']
                if conv['timestamp'] > cutoff_iso
            ]
            
            # Remove users with no recent conversations
            if not user_data['conversations']:
                del self.chat_data[user_id]
        
        # Clean up old analytics records
        self.analytics_data['sentiment_records'] = [
            record for record in self.analytics_data['sentiment_records']
            if record['timestamp'] > cutoff_iso
        ]
        
        self.analytics_data['response_success'] = [
            record for record in self.analytics_data['response_success']
            if record['timestamp'] > cutoff_iso
        ]
        
        self.analytics_data['failed_responses'] = [
            record for record in self.analytics_data['failed_responses']
            if record['timestamp'] > cutoff_iso
        ]
        
        self.save_chat_history()
        self.save_analytics_data()