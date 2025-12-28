"""
Analytics & Monitoring Layer - Tracks performance and generates insights
"""
from datetime import datetime, timedelta
from collections import defaultdict, Counter

class AnalyticsLayer:
    """Handles analytics and monitoring operations"""
    
    def __init__(self, storage_layer):
        self.storage = storage_layer
    
    def track_conversation(self, user_id, intent, sentiment, response_strategy, success, response_time=None):
        """Track a conversation for analytics"""
        # Update total conversations
        self.storage.analytics_data['total_conversations'] += 1
        
        # Track user interactions
        if user_id not in self.storage.analytics_data['user_interactions']:
            self.storage.analytics_data['user_interactions'][user_id] = {
                'total_messages': 0,
                'first_interaction': datetime.now().isoformat(),
                'last_interaction': datetime.now().isoformat(),
                'intents': defaultdict(int),
                'avg_sentiment': 0,
                'sentiment_sum': 0
            }
        
        user_data = self.storage.analytics_data['user_interactions'][user_id]
        user_data['total_messages'] += 1
        user_data['last_interaction'] = datetime.now().isoformat()
        user_data['intents'][intent] += 1
        
        # Track sentiment
        polarity = sentiment.get('polarity', 0)
        user_data['sentiment_sum'] += polarity
        user_data['avg_sentiment'] = user_data['sentiment_sum'] / user_data['total_messages']
        
        # Store records in storage layer
        self.storage.store_intent_record(intent, 0.8, success)  # Default confidence
        self.storage.store_sentiment_record(sentiment, user_id)
        self.storage.store_response_success(response_strategy, success, 0.8, response_time)
        
        self.storage.save_analytics_data()
    
    def get_conversation_stats(self, days=30):
        """Get conversation statistics for the specified period"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_iso = cutoff_date.isoformat()
        
        stats = {
            'total_conversations': 0,
            'unique_users': set(),
            'daily_activity': defaultdict(int),
            'hourly_activity': defaultdict(int)
        }
        
        # Analyze chat data
        for user_id, user_data in self.storage.chat_data.items():
            for conversation in user_data['conversations']:
                if conversation['timestamp'] > cutoff_iso:
                    stats['total_conversations'] += 1
                    stats['unique_users'].add(user_id)
                    
                    # Extract date and hour
                    timestamp = datetime.fromisoformat(conversation['timestamp'])
                    date_key = timestamp.strftime('%Y-%m-%d')
                    hour_key = timestamp.hour
                    
                    stats['daily_activity'][date_key] += 1
                    stats['hourly_activity'][hour_key] += 1
        
        stats['unique_users'] = len(stats['unique_users'])
        return dict(stats)
    
    def get_intent_analytics(self):
        """Get intent classification analytics"""
        intent_analytics = {}
        
        for intent, data in self.storage.analytics_data['intent_counts'].items():
            if data['total'] > 0:
                intent_analytics[intent] = {
                    'total_count': data['total'],
                    'success_rate': (data['successful'] / data['total']) * 100,
                    'avg_confidence': data['avg_confidence'],
                    'failure_count': data['total'] - data['successful']
                }
        
        # Sort by total count
        sorted_intents = sorted(intent_analytics.items(), key=lambda x: x[1]['total_count'], reverse=True)
        
        return {
            'intent_breakdown': dict(sorted_intents),
            'most_common_intent': sorted_intents[0][0] if sorted_intents else None,
            'total_intents_processed': sum(data['total'] for data in self.storage.analytics_data['intent_counts'].values())
        }
    
    def get_sentiment_trends(self, days=30):
        """Get sentiment trends over time"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_iso = cutoff_date.isoformat()
        
        # Filter recent sentiment records
        recent_records = [
            record for record in self.storage.analytics_data['sentiment_records']
            if record['timestamp'] > cutoff_iso
        ]
        
        # Calculate sentiment distribution
        sentiment_counts = Counter(record['sentiment'] for record in recent_records)
        total_records = len(recent_records)
        
        sentiment_distribution = {}
        if total_records > 0:
            for sentiment, count in sentiment_counts.items():
                sentiment_distribution[sentiment] = (count / total_records) * 100
        
        # Calculate daily sentiment trends
        daily_sentiment = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0})
        
        for record in recent_records:
            date_key = record['timestamp'][:10]  # Extract date
            sentiment = record['sentiment']
            daily_sentiment[date_key][sentiment] += 1
        
        # Calculate emotion trends
        emotion_counts = Counter()
        for record in recent_records:
            for emotion in record.get('emotions', []):
                emotion_counts[emotion] += 1
        
        return {
            'sentiment_distribution': sentiment_distribution,
            'daily_sentiment_trends': dict(daily_sentiment),
            'top_emotions': dict(emotion_counts.most_common(5)),
            'total_analyzed': total_records
        }
    
    def get_response_effectiveness(self):
        """Get response strategy effectiveness metrics"""
        try:
            effectiveness = {}
            
            # Analyze successful responses
            strategy_stats = {}
            
            for record in self.storage.analytics_data.get('response_success', []):
                strategy = record.get('strategy', 'unknown')
                if strategy not in strategy_stats:
                    strategy_stats[strategy] = {'total': 0, 'successful': 0, 'confidence_sum': 0}
                strategy_stats[strategy]['total'] += 1
                strategy_stats[strategy]['successful'] += 1
                strategy_stats[strategy]['confidence_sum'] += record.get('confidence', 0)
            
            for record in self.storage.analytics_data.get('failed_responses', []):
                strategy = record.get('strategy', 'unknown')
                if strategy not in strategy_stats:
                    strategy_stats[strategy] = {'total': 0, 'successful': 0, 'confidence_sum': 0}
                strategy_stats[strategy]['total'] += 1
                strategy_stats[strategy]['confidence_sum'] += record.get('confidence', 0)
            
            # Calculate effectiveness metrics
            for strategy, stats in strategy_stats.items():
                if stats['total'] > 0:
                    effectiveness[strategy] = {
                        'success_rate': (stats['successful'] / stats['total']) * 100,
                        'total_attempts': stats['total'],
                        'successful_responses': stats['successful'],
                        'failed_responses': stats['total'] - stats['successful'],
                        'avg_confidence': stats['confidence_sum'] / stats['total']
                    }
            
            # Overall effectiveness
            total_attempts = sum(stats['total'] for stats in strategy_stats.values())
            total_successful = sum(stats['successful'] for stats in strategy_stats.values())
            
            overall_success_rate = (total_successful / total_attempts * 100) if total_attempts > 0 else 0
            
            return {
                'strategy_effectiveness': effectiveness,
                'overall_success_rate': overall_success_rate,
                'total_responses_generated': total_attempts,
                'failed_responses_count': len(self.storage.analytics_data.get('failed_responses', []))
            }
        except Exception as e:
            print(f"Error in get_response_effectiveness: {e}")
            return {
                'strategy_effectiveness': {},
                'overall_success_rate': 0,
                'total_responses_generated': 0,
                'failed_responses_count': 0
            }
    
    def get_user_engagement_metrics(self):
        """Get user engagement and retention metrics"""
        if not self.storage.analytics_data['user_interactions']:
            return {}
        
        user_data = self.storage.analytics_data['user_interactions']
        
        # Calculate engagement metrics
        total_users = len(user_data)
        total_messages = sum(data['total_messages'] for data in user_data.values())
        avg_messages_per_user = total_messages / total_users if total_users > 0 else 0
        
        # Calculate retention (users with more than 1 interaction)
        returning_users = sum(1 for data in user_data.values() if data['total_messages'] > 1)
        retention_rate = (returning_users / total_users * 100) if total_users > 0 else 0
        
        # Calculate active users (interacted in last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        active_users = sum(1 for data in user_data.values() if data['last_interaction'] > week_ago)
        
        # Most engaged users
        most_engaged = sorted(user_data.items(), key=lambda x: x[1]['total_messages'], reverse=True)[:5]
        
        return {
            'total_users': total_users,
            'total_messages': total_messages,
            'avg_messages_per_user': avg_messages_per_user,
            'retention_rate': retention_rate,
            'returning_users': returning_users,
            'active_users_7d': active_users,
            'most_engaged_users': [
                {'user_id': user_id, 'message_count': data['total_messages']}
                for user_id, data in most_engaged
            ]
        }
    
    def generate_insights(self):
        """Generate actionable insights from analytics data"""
        insights = []
        
        # Get analytics data
        intent_analytics = self.get_intent_analytics()
        sentiment_trends = self.get_sentiment_trends()
        response_effectiveness = self.get_response_effectiveness()
        engagement_metrics = self.get_user_engagement_metrics()
        
        # Insight: Low success rate
        overall_success = response_effectiveness.get('overall_success_rate', 0)
        if overall_success < 70:
            insights.append({
                'type': 'warning',
                'title': 'Low Response Success Rate',
                'message': f"Overall success rate is {overall_success:.1f}%. Consider improving response strategies.",
                'priority': 'high'
            })
        
        # Insight: High negative sentiment
        sentiment_dist = sentiment_trends.get('sentiment_distribution', {})
        negative_percentage = sentiment_dist.get('negative', 0)
        if negative_percentage > 30:
            insights.append({
                'type': 'warning',
                'title': 'High Negative Sentiment',
                'message': f"{negative_percentage:.1f}% of interactions have negative sentiment. Review response quality.",
                'priority': 'medium'
            })
        
        # Insight: Low user retention
        retention_rate = engagement_metrics.get('retention_rate', 0)
        if retention_rate < 30:
            insights.append({
                'type': 'info',
                'title': 'Low User Retention',
                'message': f"Only {retention_rate:.1f}% of users return for multiple conversations. Improve user experience.",
                'priority': 'medium'
            })
        
        # Insight: Most common intent
        most_common_intent = intent_analytics.get('most_common_intent')
        if most_common_intent:
            insights.append({
                'type': 'info',
                'title': 'Most Common Intent',
                'message': f"'{most_common_intent}' is the most frequent intent. Ensure high-quality responses for this category.",
                'priority': 'low'
            })
        
        # Insight: Failed responses
        failed_count = response_effectiveness.get('failed_responses_count', 0)
        if failed_count > 50:
            insights.append({
                'type': 'warning',
                'title': 'High Failure Rate',
                'message': f"{failed_count} failed responses recorded. Review and improve fallback mechanisms.",
                'priority': 'high'
            })
        
        return insights
    
    def get_dashboard_data(self, days=30):
        """Get comprehensive dashboard data"""
        return {
            'conversation_stats': self.get_conversation_stats(days),
            'intent_analytics': self.get_intent_analytics(),
            'sentiment_trends': self.get_sentiment_trends(days),
            'response_effectiveness': self.get_response_effectiveness(),
            'user_engagement': self.get_user_engagement_metrics(),
            'insights': self.generate_insights(),
            'summary': self.storage.get_analytics_summary()
        }