"""
Learning & Improvement Layer - Adaptive system enhancement and optimization
"""
import json
from datetime import datetime, timedelta
from collections import defaultdict

class LearningLayer:
    """Handles learning and continuous improvement of the chatbot system"""
    
    def __init__(self, storage_layer, nlp_layer):
        self.storage = storage_layer
        self.nlp_layer = nlp_layer
        self.learning_data = self._load_learning_data()
    
    def _load_learning_data(self):
        """Load learning data from storage"""
        learning_file = f"{self.storage.config.DATA_DIR}/learning_data.json"
        try:
            with open(learning_file, 'r') as f:
                return json.load(f)
        except:
            return {
                'intent_improvements': {},
                'response_feedback': [],
                'pattern_discoveries': [],
                'optimization_suggestions': [],
                'model_performance_history': []
            }
    
    def _save_learning_data(self):
        """Save learning data to storage"""
        learning_file = f"{self.storage.config.DATA_DIR}/learning_data.json"
        try:
            with open(learning_file, 'w') as f:
                json.dump(self.learning_data, f, indent=2)
        except Exception as e:
            print(f"Error saving learning data: {e}")
    
    def learn_from_conversation(self, user_id, user_message, bot_response, intent, sentiment, success):
        """Learn from individual conversation exchanges"""
        
        # Record conversation outcome
        conversation_record = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'user_message': user_message[:100],  # Truncate for privacy
            'intent': intent,
            'sentiment': sentiment.get('sentiment', 'neutral'),
            'success': success,
            'response_strategy': bot_response.get('strategy', 'unknown')
        }
        
        # Learn intent patterns
        self._learn_intent_patterns(user_message, intent, success)
        
        # Learn response effectiveness
        self._learn_response_effectiveness(bot_response, success, sentiment)
        
        # Discover new patterns
        self._discover_patterns(user_message, intent, sentiment)
        
        # Update model performance tracking
        self._track_model_performance(intent, success)
        
        self._save_learning_data()
    
    def _learn_intent_patterns(self, user_message, intent, success):
        """Learn and improve intent classification patterns"""
        if intent not in self.learning_data['intent_improvements']:
            self.learning_data['intent_improvements'][intent] = {
                'successful_patterns': [],
                'failed_patterns': [],
                'improvement_suggestions': []
            }
        
        intent_data = self.learning_data['intent_improvements'][intent]
        
        # Extract key patterns from the message
        patterns = self._extract_patterns(user_message)
        
        if success:
            intent_data['successful_patterns'].extend(patterns)
        else:
            intent_data['failed_patterns'].extend(patterns)
        
        # Keep only recent patterns
        intent_data['successful_patterns'] = intent_data['successful_patterns'][-50:]
        intent_data['failed_patterns'] = intent_data['failed_patterns'][-20:]
        
        # Generate improvement suggestions
        if len(intent_data['failed_patterns']) > 5:
            suggestion = f"Intent '{intent}' has {len(intent_data['failed_patterns'])} failed patterns. Consider retraining with more examples."
            if suggestion not in intent_data['improvement_suggestions']:
                intent_data['improvement_suggestions'].append(suggestion)
    
    def _learn_response_effectiveness(self, bot_response, success, sentiment):
        """Learn which response strategies work best"""
        feedback_record = {
            'timestamp': datetime.now().isoformat(),
            'strategy': bot_response.get('strategy', 'unknown'),
            'success': success,
            'user_sentiment': sentiment.get('sentiment', 'neutral'),
            'response_confidence': bot_response.get('confidence', 0)
        }
        
        self.learning_data['response_feedback'].append(feedback_record)
        
        # Keep only recent feedback
        if len(self.learning_data['response_feedback']) > 500:
            self.learning_data['response_feedback'] = self.learning_data['response_feedback'][-500:]
    
    def _discover_patterns(self, user_message, intent, sentiment):
        """Discover new conversation patterns"""
        # Look for emerging patterns in user messages
        patterns = self._extract_patterns(user_message)
        
        for pattern in patterns:
            # Check if this is a new pattern for this intent
            existing_patterns = [
                p['pattern'] for p in self.learning_data['pattern_discoveries']
                if p['intent'] == intent
            ]
            
            if pattern not in existing_patterns and len(pattern) > 3:
                discovery = {
                    'timestamp': datetime.now().isoformat(),
                    'pattern': pattern,
                    'intent': intent,
                    'sentiment': sentiment.get('sentiment', 'neutral'),
                    'frequency': 1
                }
                self.learning_data['pattern_discoveries'].append(discovery)
        
        # Update frequency for existing patterns
        for discovery in self.learning_data['pattern_discoveries']:
            if discovery['intent'] == intent and discovery['pattern'] in patterns:
                discovery['frequency'] += 1
        
        # Keep only recent discoveries
        if len(self.learning_data['pattern_discoveries']) > 200:
            self.learning_data['pattern_discoveries'] = self.learning_data['pattern_discoveries'][-200:]
    
    def _extract_patterns(self, text):
        """Extract meaningful patterns from text"""
        patterns = []
        words = text.lower().split()
        
        # Single word patterns
        patterns.extend([word for word in words if len(word) > 3])
        
        # Bigram patterns
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            if len(bigram) > 6:
                patterns.append(bigram)
        
        # Trigram patterns
        for i in range(len(words) - 2):
            trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
            if len(trigram) > 10:
                patterns.append(trigram)
        
        return patterns[:10]  # Return top 10 patterns
    
    def _track_model_performance(self, intent, success):
        """Track model performance over time"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Find or create today's performance record
        today_record = None
        for record in self.learning_data['model_performance_history']:
            if record['date'] == today:
                today_record = record
                break
        
        if not today_record:
            today_record = {
                'date': today,
                'intent_performance': defaultdict(lambda: {'total': 0, 'successful': 0}),
                'overall_accuracy': 0
            }
            self.learning_data['model_performance_history'].append(today_record)
        
        # Update performance
        intent_perf = today_record['intent_performance']
        if intent not in intent_perf:
            intent_perf[intent] = {'total': 0, 'successful': 0}
        
        intent_perf[intent]['total'] += 1
        if success:
            intent_perf[intent]['successful'] += 1
        
        # Calculate overall accuracy
        total_attempts = sum(data['total'] for data in intent_perf.values())
        total_successful = sum(data['successful'] for data in intent_perf.values())
        today_record['overall_accuracy'] = (total_successful / total_attempts * 100) if total_attempts > 0 else 0
        
        # Keep only recent performance history
        if len(self.learning_data['model_performance_history']) > 90:  # 90 days
            self.learning_data['model_performance_history'] = self.learning_data['model_performance_history'][-90:]
    
    def generate_optimization_suggestions(self):
        """Generate suggestions for system optimization"""
        suggestions = []
        
        # Analyze intent performance
        intent_suggestions = self._analyze_intent_performance()
        suggestions.extend(intent_suggestions)
        
        # Analyze response effectiveness
        response_suggestions = self._analyze_response_effectiveness()
        suggestions.extend(response_suggestions)
        
        # Analyze pattern discoveries
        pattern_suggestions = self._analyze_pattern_discoveries()
        suggestions.extend(pattern_suggestions)
        
        # Store suggestions
        self.learning_data['optimization_suggestions'] = suggestions
        self._save_learning_data()
        
        return suggestions
    
    def _analyze_intent_performance(self):
        """Analyze intent classification performance and suggest improvements"""
        suggestions = []
        
        for intent, data in self.learning_data['intent_improvements'].items():
            failed_count = len(data['failed_patterns'])
            successful_count = len(data['successful_patterns'])
            
            if failed_count > 10:
                suggestions.append({
                    'type': 'intent_improvement',
                    'priority': 'high',
                    'suggestion': f"Retrain intent classifier for '{intent}' - {failed_count} failed classifications",
                    'action': 'retrain_intent_model',
                    'target': intent
                })
            
            if successful_count > 50 and failed_count < 5:
                suggestions.append({
                    'type': 'intent_optimization',
                    'priority': 'low',
                    'suggestion': f"Intent '{intent}' is performing well - consider it as a template for other intents",
                    'action': 'use_as_template',
                    'target': intent
                })
        
        return suggestions
    
    def _analyze_response_effectiveness(self):
        """Analyze response strategy effectiveness"""
        suggestions = []
        
        # Group feedback by strategy
        strategy_performance = defaultdict(lambda: {'total': 0, 'successful': 0})
        
        for feedback in self.learning_data['response_feedback'][-100:]:  # Recent 100 feedbacks
            strategy = feedback['strategy']
            strategy_performance[strategy]['total'] += 1
            if feedback['success']:
                strategy_performance[strategy]['successful'] += 1
        
        # Analyze each strategy
        for strategy, performance in strategy_performance.items():
            if performance['total'] > 10:  # Enough data points
                success_rate = (performance['successful'] / performance['total']) * 100
                
                if success_rate < 60:
                    suggestions.append({
                        'type': 'response_improvement',
                        'priority': 'high',
                        'suggestion': f"Response strategy '{strategy}' has low success rate ({success_rate:.1f}%)",
                        'action': 'improve_response_strategy',
                        'target': strategy
                    })
                elif success_rate > 90:
                    suggestions.append({
                        'type': 'response_optimization',
                        'priority': 'low',
                        'suggestion': f"Response strategy '{strategy}' is highly effective ({success_rate:.1f}%)",
                        'action': 'expand_strategy_usage',
                        'target': strategy
                    })
        
        return suggestions
    
    def _analyze_pattern_discoveries(self):
        """Analyze discovered patterns for new insights"""
        suggestions = []
        
        # Find frequently occurring patterns
        pattern_frequency = defaultdict(int)
        for discovery in self.learning_data['pattern_discoveries']:
            pattern_frequency[discovery['pattern']] += discovery['frequency']
        
        # Suggest new intents for frequent patterns
        for pattern, frequency in pattern_frequency.items():
            if frequency > 10:  # Frequently occurring pattern
                # Check if pattern is already covered by existing intents
                covered = False
                for intent, keywords in self.storage.config.INTENTS.items():
                    if any(keyword in pattern for keyword in keywords):
                        covered = True
                        break
                
                if not covered:
                    suggestions.append({
                        'type': 'new_intent_suggestion',
                        'priority': 'medium',
                        'suggestion': f"Consider creating new intent for pattern '{pattern}' (frequency: {frequency})",
                        'action': 'create_new_intent',
                        'target': pattern
                    })
        
        return suggestions
    
    def improve_intent_classifier(self):
        """Improve intent classifier based on learning data"""
        # Collect successful patterns for retraining
        training_data = []
        labels = []
        
        for intent, data in self.learning_data['intent_improvements'].items():
            for pattern in data['successful_patterns']:
                training_data.append(pattern)
                labels.append(intent)
        
        # Add original training data
        for intent, patterns in self.storage.config.INTENTS.items():
            for pattern in patterns:
                training_data.append(pattern)
                labels.append(intent)
        
        # Retrain model if we have enough data
        if len(training_data) > 50:
            try:
                self.nlp_layer.train_intent_model()
                return True
            except Exception as e:
                print(f"Error retraining intent model: {e}")
                return False
        
        return False
    
    def reduce_fallback_responses(self):
        """Analyze and reduce fallback response usage"""
        fallback_analysis = {
            'total_fallbacks': 0,
            'fallback_patterns': defaultdict(int),
            'improvement_actions': []
        }
        
        # Analyze fallback usage
        for feedback in self.learning_data['response_feedback']:
            if feedback['strategy'] == 'fallback':
                fallback_analysis['total_fallbacks'] += 1
        
        # Generate improvement actions
        if fallback_analysis['total_fallbacks'] > 50:
            fallback_analysis['improvement_actions'].append(
                "High fallback usage detected. Consider expanding FAQ database and improving intent classification."
            )
        
        return fallback_analysis
    
    def get_learning_insights(self):
        """Get comprehensive learning insights"""
        return {
            'optimization_suggestions': self.generate_optimization_suggestions(),
            'intent_improvements': dict(self.learning_data['intent_improvements']),
            'pattern_discoveries': self.learning_data['pattern_discoveries'][-20:],  # Recent 20
            'model_performance_trend': self.learning_data['model_performance_history'][-7:],  # Last 7 days
            'fallback_analysis': self.reduce_fallback_responses()
        }