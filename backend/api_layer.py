"""
API / Communication Layer - REST API for chatbot interactions
"""
from flask import Flask, request, jsonify, session
import uuid
from datetime import datetime
import time

class APILayer:
    """Handles REST API communication and session management"""
    
    def __init__(self, core_orchestrator):
        self.app = Flask(__name__)
        self.app.secret_key = 'layered-ai-chatbot-secret-key'
        self.core = core_orchestrator
        self.active_sessions = {}
        
        # Register API routes
        self._register_routes()
    
    def _register_routes(self):
        """Register all API endpoints"""
        
        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            """Main chat endpoint"""
            try:
                data = request.get_json()
                
                if not data or 'message' not in data:
                    return jsonify({
                        'error': 'Message is required',
                        'status': 'error'
                    }), 400
                
                user_message = data['message']
                session_id = data.get('session_id') or self._create_session()
                
                # Process message through core orchestrator
                start_time = time.time()
                response = self.core.process_message(user_message, session_id)
                processing_time = time.time() - start_time
                
                # Update session info
                self._update_session(session_id, user_message, response, processing_time)
                
                return jsonify({
                    'response': response['text'],
                    'intent': response['intent'],
                    'sentiment': response['sentiment'],
                    'confidence': response['confidence'],
                    'session_id': session_id,
                    'processing_time': processing_time,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success'
                })
                
            except Exception as e:
                return jsonify({
                    'error': str(e),
                    'status': 'error',
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/session', methods=['POST'])
        def create_session():
            """Create a new chat session"""
            session_id = self._create_session()
            return jsonify({
                'session_id': session_id,
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/session/<session_id>', methods=['GET'])
        def get_session(session_id):
            """Get session information"""
            if session_id in self.active_sessions:
                session_data = self.active_sessions[session_id]
                return jsonify({
                    'session_id': session_id,
                    'session_data': session_data,
                    'status': 'success'
                })
            else:
                return jsonify({
                    'error': 'Session not found',
                    'status': 'error'
                }), 404
        
        @self.app.route('/api/history/<session_id>', methods=['GET'])
        def get_history(session_id):
            """Get conversation history for a session"""
            try:
                limit = request.args.get('limit', 10, type=int)
                history = self.core.get_conversation_history(session_id, limit)
                
                return jsonify({
                    'session_id': session_id,
                    'history': history,
                    'count': len(history),
                    'status': 'success'
                })
                
            except Exception as e:
                return jsonify({
                    'error': str(e),
                    'status': 'error'
                }), 500
        
        @self.app.route('/api/analytics', methods=['GET'])
        def get_analytics():
            """Get system analytics"""
            try:
                days = request.args.get('days', 30, type=int)
                analytics = self.core.get_analytics_dashboard(days)
                
                return jsonify({
                    'analytics': analytics,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({
                    'error': str(e),
                    'status': 'error'
                }), 500
        
        @self.app.route('/api/feedback', methods=['POST'])
        def submit_feedback():
            """Submit user feedback"""
            try:
                data = request.get_json()
                
                if not data or 'session_id' not in data or 'rating' not in data:
                    return jsonify({
                        'error': 'Session ID and rating are required',
                        'status': 'error'
                    }), 400
                
                session_id = data['session_id']
                rating = data['rating']  # 1-5 scale
                comment = data.get('comment', '')
                
                # Process feedback
                success = self.core.process_feedback(session_id, rating, comment)
                
                if success:
                    return jsonify({
                        'message': 'Feedback submitted successfully',
                        'status': 'success'
                    })
                else:
                    return jsonify({
                        'error': 'Failed to process feedback',
                        'status': 'error'
                    }), 500
                    
            except Exception as e:
                return jsonify({
                    'error': str(e),
                    'status': 'error'
                }), 500
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """System health check"""
            try:
                health_status = self.core.get_system_health()
                return jsonify({
                    'health': health_status,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'error': str(e),
                    'status': 'error'
                }), 500
        
        @self.app.route('/api/intents', methods=['GET'])
        def get_intents():
            """Get available intents"""
            return jsonify({
                'intents': list(self.core.storage.config.INTENTS.keys()),
                'status': 'success'
            })
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({
                'error': 'Endpoint not found',
                'status': 'error'
            }), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({
                'error': 'Internal server error',
                'status': 'error'
            }), 500
    
    def _create_session(self):
        """Create a new session"""
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = {
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'message_count': 0,
            'total_processing_time': 0
        }
        return session_id
    
    def _update_session(self, session_id, user_message, response, processing_time):
        """Update session information"""
        if session_id in self.active_sessions:
            session_data = self.active_sessions[session_id]
            session_data['last_activity'] = datetime.now().isoformat()
            session_data['message_count'] += 1
            session_data['total_processing_time'] += processing_time
            session_data['avg_processing_time'] = session_data['total_processing_time'] / session_data['message_count']
    
    def cleanup_inactive_sessions(self, hours=24):
        """Clean up inactive sessions"""
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        inactive_sessions = []
        for session_id, session_data in self.active_sessions.items():
            last_activity = datetime.fromisoformat(session_data['last_activity'])
            if last_activity < cutoff_time:
                inactive_sessions.append(session_id)
        
        for session_id in inactive_sessions:
            del self.active_sessions[session_id]
        
        return len(inactive_sessions)
    
    def get_session_stats(self):
        """Get session statistics"""
        total_sessions = len(self.active_sessions)
        total_messages = sum(session['message_count'] for session in self.active_sessions.values())
        
        if self.active_sessions:
            avg_messages_per_session = total_messages / total_sessions
            avg_processing_time = sum(
                session.get('avg_processing_time', 0) 
                for session in self.active_sessions.values()
            ) / total_sessions
        else:
            avg_messages_per_session = 0
            avg_processing_time = 0
        
        return {
            'total_active_sessions': total_sessions,
            'total_messages_processed': total_messages,
            'avg_messages_per_session': avg_messages_per_session,
            'avg_processing_time': avg_processing_time
        }
    
    def run(self, host='localhost', port=5000, debug=False):
        """Run the Flask API server"""
        print(f"Starting Layered AI Chatbot API on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)