"""
Streamlit Frontend for Layered AI Chatbot System
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import time

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.core import ChatbotCore

# Page configuration
st.set_page_config(
    page_title="Layered AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 10%;
        border-left-color: #2196f3;
    }
    .bot-message {
        background-color: #f5f5f5;
        margin-right: 10%;
        border-left-color: #4caf50;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .layer-status {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
    }
    .operational { background-color: #e8f5e8; color: #2e7d32; }
    .warning { background-color: #fff3e0; color: #f57c00; }
    .error { background-color: #ffebee; color: #d32f2f; }
</style>
""", unsafe_allow_html=True)

# Initialize chatbot
@st.cache_resource
def initialize_chatbot():
    return ChatbotCore()

# Initialize session state
def initialize_session_state():
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = initialize_chatbot()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def display_system_health():
    """Display system health status"""
    health = st.session_state.chatbot.get_system_health()
    
    st.subheader("🔧 System Health")
    
    # Layer status
    layers = [
        ('Preprocessing', health['preprocessing_layer']),
        ('NLP', health['nlp_layer']),
        ('Sentiment', health['sentiment_layer']),
        ('Decision Engine', health['decision_engine']),
        ('Response', health['response_layer']),
        ('Storage', health['storage_layer']),
        ('Analytics', health['analytics_layer']),
        ('Learning', health['learning_layer'])
    ]
    
    for layer_name, status in layers:
        status_class = 'operational' if status == 'operational' else 'error'
        st.markdown(f'<div class="layer-status {status_class}">🔹 {layer_name}: {status}</div>', 
                   unsafe_allow_html=True)
    
    # API Status
    st.write("**API Status:**")
    api_status = health['api_status']
    for api, status in api_status.items():
        color = "🟢" if status == "available" else "🟡"
        st.write(f"{color} {api.title()}: {status}")

def display_analytics_dashboard():
    """Display comprehensive analytics dashboard"""
    st.subheader("📊 Analytics Dashboard")
    
    try:
        dashboard_data = st.session_state.chatbot.get_analytics_dashboard(days=30)
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_conversations = dashboard_data['conversation_stats']['total_conversations']
            st.metric("Total Conversations", total_conversations)
        
        with col2:
            unique_users = dashboard_data['conversation_stats']['unique_users']
            st.metric("Unique Users", unique_users)
        
        with col3:
            success_rate = dashboard_data['response_effectiveness']['overall_success_rate']
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        with col4:
            total_intents = dashboard_data['intent_analytics']['total_intents_processed']
            st.metric("Intents Processed", total_intents)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Intent Distribution
            intent_data = dashboard_data['intent_analytics']['intent_breakdown']
            if intent_data:
                intent_df = pd.DataFrame([
                    {'Intent': intent, 'Count': data['total_count']}
                    for intent, data in intent_data.items()
                ])
                fig = px.pie(intent_df, values='Count', names='Intent', 
                           title="Intent Distribution")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Sentiment Distribution
            sentiment_data = dashboard_data['sentiment_trends']['sentiment_distribution']
            if sentiment_data:
                sentiment_df = pd.DataFrame([
                    {'Sentiment': sentiment, 'Percentage': percentage}
                    for sentiment, percentage in sentiment_data.items()
                ])
                colors = {'positive': '#2ecc71', 'negative': '#e74c3c', 'neutral': '#95a5a6'}
                fig = px.bar(sentiment_df, x='Sentiment', y='Percentage',
                           color='Sentiment', color_discrete_map=colors,
                           title="Sentiment Distribution")
                st.plotly_chart(fig, use_container_width=True)
        
        # Response Effectiveness
        st.subheader("🎯 Response Strategy Effectiveness")
        effectiveness_data = dashboard_data['response_effectiveness']['strategy_effectiveness']
        if effectiveness_data:
            eff_df = pd.DataFrame([
                {
                    'Strategy': strategy,
                    'Success Rate': data['success_rate'],
                    'Total Attempts': data['total_attempts']
                }
                for strategy, data in effectiveness_data.items()
            ])
            
            fig = px.bar(eff_df, x='Strategy', y='Success Rate',
                        title="Response Strategy Success Rates")
            st.plotly_chart(fig, use_container_width=True)
        
        # System Insights
        insights = dashboard_data.get('insights', [])
        if insights:
            st.subheader("💡 System Insights")
            for insight in insights:
                icon = {"warning": "⚠️", "info": "ℹ️", "success": "✅"}.get(insight['type'], "ℹ️")
                st.write(f"{icon} **{insight['title']}:** {insight['message']}")
    
    except Exception as e:
        st.error(f"Error loading analytics: {e}")

def display_learning_insights():
    """Display learning and improvement insights"""
    st.subheader("🧠 Learning Insights")
    
    try:
        learning_data = st.session_state.chatbot.get_learning_insights()
        
        # Optimization Suggestions
        suggestions = learning_data.get('optimization_suggestions', [])
        if suggestions:
            st.write("**Optimization Suggestions:**")
            for suggestion in suggestions[:5]:  # Show top 5
                priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(suggestion['priority'], "🔵")
                st.write(f"{priority_color} {suggestion['suggestion']}")
        
        # Pattern Discoveries
        patterns = learning_data.get('pattern_discoveries', [])
        if patterns:
            st.write("**Recent Pattern Discoveries:**")
            for pattern in patterns[-5:]:  # Show last 5
                st.write(f"• Pattern: '{pattern['pattern']}' (Intent: {pattern['intent']}, Frequency: {pattern['frequency']})")
        
        # Model Performance Trend
        performance_trend = learning_data.get('model_performance_trend', [])
        if performance_trend:
            st.write("**Model Performance Trend (Last 7 Days):**")
            perf_df = pd.DataFrame(performance_trend)
            if not perf_df.empty:
                fig = px.line(perf_df, x='date', y='overall_accuracy',
                            title="Model Accuracy Over Time")
                st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading learning insights: {e}")

def main():
    initialize_session_state()
    
    # Main header
    st.markdown('<h1 class="main-header">🤖 Layered AI Chatbot System</h1>', 
               unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Control Panel")
        
        # System Health
        with st.expander("🔧 System Health", expanded=False):
            display_system_health()
        
        # Analytics Toggle
        show_analytics = st.checkbox("📊 Show Analytics Dashboard", value=False)
        
        # Learning Insights Toggle
        show_learning = st.checkbox("🧠 Show Learning Insights", value=False)
        
        # System Actions
        st.subheader("⚙️ System Actions")
        
        if st.button("🔄 Optimize System"):
            with st.spinner("Optimizing system..."):
                results = st.session_state.chatbot.optimize_system()
                st.success("System optimization completed!")
                st.json(results)
        
        if st.button("📈 Get Statistics"):
            stats = st.session_state.chatbot.get_system_statistics()
            st.json(stats)
        
        # User Feedback
        st.subheader("📝 Feedback")
        if st.session_state.messages:
            feedback_rating = st.selectbox(
                "Rate the last response:",
                [1, 2, 3, 4, 5],
                index=2,
                format_func=lambda x: f"{'⭐' * x} ({x}/5)"
            )
            
            feedback_comment = st.text_area("Additional comments (optional):")
            
            if st.button("Submit Feedback"):
                success = st.session_state.chatbot.process_feedback(
                    st.session_state.user_id, 
                    feedback_rating, 
                    feedback_comment
                )
                if success:
                    st.success("Thank you for your feedback!")
                else:
                    st.error("Failed to submit feedback.")
    
    # Main content area
    if show_analytics:
        display_analytics_dashboard()
    elif show_learning:
        display_learning_insights()
    else:
        # Chat Interface
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("💬 Chat Interface")
            
            # Display chat messages
            chat_container = st.container()
            with chat_container:
                for i, message in enumerate(st.session_state.messages):
                    if message['role'] == 'user':
                        st.markdown(f"""
                        <div class="chat-message user-message">
                            <strong>You:</strong> {message['content']}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Display bot response with detailed metadata
                        metadata = message.get('metadata', {})
                        intent = metadata.get('intent', 'unknown')
                        sentiment = metadata.get('sentiment', {}).get('sentiment', 'neutral')
                        confidence = metadata.get('confidence', 0)
                        strategy = metadata.get('strategy', 'unknown')
                        processing_time = metadata.get('processing_time', 0)
                        
                        st.markdown(f"""
                        <div class="chat-message bot-message">
                            <strong>AI Assistant:</strong> {message['content']}<br>
                            <small>
                                Intent: {intent} | Sentiment: {sentiment} | 
                                Strategy: {strategy} | Confidence: {confidence:.1%} | 
                                Time: {processing_time:.2f}s
                            </small>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Chat input
            with st.form("chat_form", clear_on_submit=True):
                user_input = st.text_input("Type your message here...", key="user_input")
                col_send, col_clear = st.columns([1, 1])
                
                with col_send:
                    send_button = st.form_submit_button("Send 📤", use_container_width=True)
                
                with col_clear:
                    clear_button = st.form_submit_button("Clear Chat 🗑️", use_container_width=True)
            
            # Handle user input
            if send_button and user_input:
                # Add user message
                st.session_state.messages.append({
                    'role': 'user',
                    'content': user_input,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Get bot response
                with st.spinner("AI is processing through all layers..."):
                    response = st.session_state.chatbot.process_message(user_input, st.session_state.user_id)
                
                # Add bot response
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': response['text'],
                    'timestamp': response['timestamp'],
                    'metadata': response
                })
                
                st.rerun()
            
            # Handle clear chat
            if clear_button:
                st.session_state.messages = []
                st.rerun()
        
        with col2:
            st.subheader("📈 Live Metrics")
            
            # Current conversation stats
            if st.session_state.messages:
                user_messages = [msg for msg in st.session_state.messages if msg['role'] == 'user']
                bot_messages = [msg for msg in st.session_state.messages if msg['role'] == 'assistant']
                
                st.metric("Messages Exchanged", len(st.session_state.messages))
                st.metric("Your Messages", len(user_messages))
                st.metric("AI Responses", len(bot_messages))
                
                # Recent processing details
                if bot_messages:
                    last_response = bot_messages[-1]['metadata']
                    st.write("**Last Response Details:**")
                    st.write(f"• Intent: {last_response.get('intent', 'N/A')}")
                    st.write(f"• Sentiment: {last_response.get('sentiment', {}).get('sentiment', 'N/A')}")
                    st.write(f"• Strategy: {last_response.get('strategy', 'N/A')}")
                    st.write(f"• Confidence: {last_response.get('confidence', 0):.1%}")
                    st.write(f"• Processing Time: {last_response.get('processing_time', 0):.2f}s")
                    st.write(f"• Success: {'✅' if last_response.get('success', False) else '❌'}")
                
                # Recent intents
                recent_intents = [msg['metadata'].get('intent', 'unknown') for msg in bot_messages[-5:]]
                st.write("**Recent Intents:**")
                for intent in recent_intents:
                    st.write(f"• {intent}")
                
                # Recent sentiments
                recent_sentiments = [
                    msg['metadata'].get('sentiment', {}).get('sentiment', 'neutral') 
                    for msg in bot_messages[-5:]
                ]
                st.write("**Recent Sentiments:**")
                for sentiment in recent_sentiments:
                    emoji = {"positive": "😊", "negative": "😞", "neutral": "😐"}.get(sentiment, "😐")
                    st.write(f"• {emoji} {sentiment}")
            
            # System performance
            try:
                health = st.session_state.chatbot.get_system_health()
                metrics = health.get('system_metrics', {})
                
                st.subheader("🔧 System Metrics")
                st.metric("Total Conversations", metrics.get('total_conversations', 0))
                st.metric("Active Users", metrics.get('active_users', 0))
                
                model_status = "✅ Loaded" if metrics.get('intent_model_loaded', False) else "❌ Not Loaded"
                st.write(f"**Intent Model:** {model_status}")
                
            except Exception as e:
                st.error(f"Error loading system metrics: {e}")

if __name__ == "__main__":
    main()